#!/usr/bin/env python3
"""
Parse KEA official college list PDF (2026-27 codewise).

Expected file name (place in project root):
  LIST OF COLLEGES DURING 2026-27 (CODEWISE)  - 09062026_260609_094212.pdf

Outputs:
  parsed_data/colleges_2026_27.json
  backend/parsed_data/colleges_2026_27.json

Usage:
  python parse_college_list_pdf.py
  python parse_college_list_pdf.py --pdf "path/to/college-list.pdf"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

# Reuse location helpers when available
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
try:
    from data_loader import infer_location_from_name as _infer_location
except ImportError:
    def _infer_location(name: str) -> str:
        upper = (name or "").upper()
        for token, city in [
            ("BANGALORE", "Bangalore"), ("MYSORE", "Mysore"), ("BELGAUM", "Belgaum"),
            ("BELAGAVI", "Belgaum"), ("HUBLI", "Hubballi"), ("MANGALORE", "Mangalore"),
        ]:
            if token in upper:
                return city
        return "Other"


def infer_college_type_from_name(name: str) -> str:
    nl = name.lower()
    if "government" in nl or "govt" in nl:
        return "Government"
    if "university" in nl:
        return "Private-University"
    if "aided" in nl:
        return "Private-Aided"
    return "Private-Unaided"


DEFAULT_PDF_CANDIDATES = [
    "LIST OF COLLEGES DURING 2026-27 (CODEWISE)  - 09062026_260609_094212.pdf",
    "LIST OF COLLEGES DURING 2026-27 (CODEWISE) - 09062026_260609_094212.pdf",
    "LIST OF COLLEGES DURING 2026-27 (CODEWISE)-09062026_260609_094212.pdf",
]

CODE_RE = re.compile(r"\b(E\d{3})\b", re.IGNORECASE)
COLLEGE_PREFIX_RE = re.compile(
    r"College:\s*\(?(E\d{3})\)?\s*(.+)$", re.IGNORECASE
)
TABLE_ROW_RE = re.compile(
    r"^\s*\d+\s+(E\d{3})\s+(.+)$", re.IGNORECASE
)

TYPE_MAP = {
    "GOVT": "Government",
    "GOVERNMENT": "Government",
    "PA": "Private-Aided",
    "PUA": "Private-Unaided",
    "PU": "Private-Unaided",
    "ML": "Private-Unaided",
    "MR": "Private-Unaided",
    "DU": "Private-University",
    "UNIVERSITY": "Private-University",
}


def ensure_pdfplumber():
    try:
        import pdfplumber  # noqa: F401
        return True
    except ImportError:
        import subprocess
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", "pdfplumber", "-q"],
            capture_output=True,
            text=True,
        )
        return r.returncode == 0


def normalize_code(raw: str) -> Optional[str]:
    m = CODE_RE.search(str(raw or ""))
    return m.group(1).upper() if m else None


def normalize_type(raw: str, college_name: str) -> str:
    token = (raw or "").strip().upper()
    if token in TYPE_MAP:
        return TYPE_MAP[token]
    return infer_college_type_from_name(college_name)


def parse_college_name_line(code: str, rest: str) -> Dict:
    name = rest.strip().rstrip(",")
    # Strip leading (E001) duplicate if present
    name = re.sub(r"^\(?E\d{3}\)?\s*", "", name, flags=re.I).strip()
    location = _infer_location(name)
    return {
        "college_code": code,
        "college_name": name,
        "location": location,
        "college_type": infer_college_type_from_name(name),
        "status": True,
    }


def extract_from_text(text: str) -> Dict[str, Dict]:
    colleges: Dict[str, Dict] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        m = COLLEGE_PREFIX_RE.search(line)
        if m:
            code = m.group(1).upper()
            colleges[code] = parse_college_name_line(code, m.group(2))
            continue

        m = TABLE_ROW_RE.match(line)
        if m:
            code = m.group(1).upper()
            colleges[code] = parse_college_name_line(code, m.group(2))
            continue

        code = normalize_code(line)
        if code and code not in colleges:
            # Line contains code — use full line as name if long enough
            if len(line) > 10:
                colleges[code] = parse_college_name_line(code, line)

    return colleges


def extract_from_pdf(pdf_path: str) -> Dict[str, Dict]:
    import pdfplumber

    colleges: Dict[str, Dict] = {}
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            colleges.update(extract_from_text(text))

            tables = page.extract_tables() or []
            for table in tables:
                for row in table:
                    if not row:
                        continue
                    cells = [str(c or "").strip() for c in row]
                    row_text = " ".join(cells)
                    code = None
                    for cell in cells:
                        code = normalize_code(cell)
                        if code:
                            break
                    if not code:
                        continue

                    name = ""
                    college_type = ""
                    location = ""
                    for cell in cells:
                        if normalize_code(cell) == code:
                            continue
                        cu = cell.upper()
                        if cu in TYPE_MAP:
                            college_type = normalize_type(cu, name or row_text)
                        elif len(cell) > 15 and not name:
                            name = cell
                        elif cell and len(cell) < 30 and _infer_location(cell) != "Other":
                            location = _infer_location(cell)

                    if not name:
                        name = re.sub(r"\bE\d{3}\b", "", row_text, flags=re.I).strip()

                    colleges[code] = {
                        "college_code": code,
                        "college_name": name,
                        "location": location or _infer_location(name),
                        "college_type": college_type or infer_college_type_from_name(name),
                        "status": True,
                    }

    return colleges


def find_pdf(explicit: Optional[str]) -> Optional[str]:
    root = os.path.dirname(os.path.abspath(__file__))
    if explicit and os.path.isfile(explicit):
        return explicit
    for name in DEFAULT_PDF_CANDIDATES:
        path = os.path.join(root, name)
        if os.path.isfile(path):
            return path
    for fname in os.listdir(root):
        if not fname.lower().endswith(".pdf"):
            continue
        upper = fname.upper()
        if "COLLEGE" in upper and "2026" in upper and "CODE" in upper:
            return os.path.join(root, fname)
        if "094212" in fname:
            return os.path.join(root, fname)
    return None


def load_fallback_json() -> Dict[str, Dict]:
    """Fallback: merge existing parsed college JSON sources."""
    root = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(root, "parsed_data", "kea_colleges_2025.json"),
        os.path.join(root, "backend", "parsed_data", "kea_colleges_2025.json"),
    ]
    merged: Dict[str, Dict] = {}
    for path in candidates:
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for c in data.get("colleges", []):
            code = c.get("college_code")
            if code:
                merged[code] = dict(c)
    return merged


def write_outputs(colleges: Dict[str, Dict]) -> List[str]:
    root = os.path.dirname(os.path.abspath(__file__))
    payload = {
        "source": "KEA 2026-27 College List (Codewise)",
        "total": len(colleges),
        "colleges": sorted(colleges.values(), key=lambda x: x["college_code"]),
    }
    written = []
    for sub in ("parsed_data", os.path.join("backend", "parsed_data")):
        out_dir = os.path.join(root, sub)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "colleges_2026_27.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        written.append(out_path)
    return written


def main():
    parser = argparse.ArgumentParser(description="Parse KEA 2026-27 codewise college list PDF")
    parser.add_argument("--pdf", help="Path to college list PDF")
    parser.add_argument("--fallback-only", action="store_true", help="Use JSON fallback only")
    args = parser.parse_args()

    colleges: Dict[str, Dict] = {}
    pdf_path = None if args.fallback_only else find_pdf(args.pdf)

    if pdf_path:
        if not ensure_pdfplumber():
            print("ERROR: pdfplumber required")
            sys.exit(1)
        print(f"Parsing PDF: {pdf_path}")
        colleges = extract_from_pdf(pdf_path)
        print(f"  Extracted {len(colleges)} colleges from PDF")
    else:
        print("College list PDF not found — using JSON fallback (kea_colleges_2025.json)")
        colleges = load_fallback_json()
        print(f"  Loaded {len(colleges)} colleges from fallback JSON")

    if not colleges:
        print("ERROR: No colleges extracted")
        sys.exit(1)

    paths = write_outputs(colleges)
    for p in paths:
        print(f"  Wrote {p}")
    print(f"Done — {len(colleges)} colleges in master list")


if __name__ == "__main__":
    main()
