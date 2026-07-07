#!/usr/bin/env python3
"""
KCET 2025-26 Cutoff PDF Parser — All Categories
================================================
Parses the official KCET cutoff PDF (all 8 categories) and extracts:
  - Colleges (code, name, location, type)
  - Courses (code, name)
  - Cutoff ranks by college × course × category × round (1, 2, 3)

Outputs (in parsed_data/):
  - pdf_cutoffs_all.json       — Full structured data (all categories)
  - pdf_colleges.json          — College master list
  - pdf_courses.json           — Course master list
  - pdf_summary.json           — Summary statistics
  - pdf_import.py              — Python module for backend

Usage:
  python parse_kcet_pdf.py [--pdf path/to/pdf] [--output-dir ./parsed_data]

Dependencies (auto-installed):
  pip install pdfplumber  (best for table extraction)
"""

import os
import sys
import json
import re
import argparse
from collections import defaultdict
from typing import List, Dict, Optional, Tuple

# ── Configuration ────────────────────────────────────────────
DEFAULT_PDF_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "CUTOFF 2025-26 UPDATED09062026_260609_094612.pdf"
)
OUTPUT_DIR = "parsed_data"

ALL_CATEGORIES = {"GM", "2AR", "3BK", "SCG", "STK", "GMEWS", "2A", "3A"}
COURSE_ALIASES = {
    "CS":  ["COMPUTER SCIENCE", "CSE", "CS", "COMP"],
    "IS":  ["INFORMATION SCIENCE", "ISE", "IS", "INFO SCI"],
    "EC":  ["ELECTRONICS", "ECE", "EC", "ELECTRONICS AND COMMUNICATION"],
    "ME":  ["MECHANICAL", "MECH", "ME"],
    "CE":  ["CIVIL", "CE", "CIV"],
    "AI":  ["ARTIFICIAL", "AIML", "AI", "AI & ML", "AI AND ML"],
    "DS":  ["DATA SCIENCE", "DS", "DATA"],
    "BT":  ["BIOTECHNOLOGY", "BT", "BIOTECH", "BIO"],
}

GOVT_KEYWORDS = {"government", "govt", "gov"}
UNIV_KEYWORDS = {"university", "univ"}
AIDED_KEYWORDS = {"aided", "grant-in-aid"}


# ── Utility Functions ───────────────────────────────────────

def ensure_deps():
    """Install pdfplumber if not available."""
    try:
        import pdfplumber
        return True
    except ImportError:
        print("  Installing pdfplumber...")
        import subprocess
        r = subprocess.run([sys.executable, "-m", "pip", "install", "pdfplumber", "-q"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            print("  ✅ pdfplumber installed")
            return True
        print(f"  ❌ Failed: {r.stderr[:200]}")
        return False


def infer_college_type(name: str) -> str:
    nl = name.lower()
    if any(kw in nl for kw in GOVT_KEYWORDS): return "Government"
    if any(kw in nl for kw in UNIV_KEYWORDS): return "Private-University"
    if any(kw in nl for kw in AIDED_KEYWORDS): return "Private-Aided"
    return "Private-Unaided"


def normalize_course(raw: str) -> Optional[str]:
    """Normalize various course text to standard 2-char code."""
    ru = re.sub(r'[^A-Za-z0-9]', '', raw.strip().upper())
    for code, aliases in COURSE_ALIASES.items():
        normalized_aliases = [re.sub(r'[^A-Za-z0-9]', '', a) for a in aliases]
        if ru in normalized_aliases:
            return code
        for a in normalized_aliases:
            if a in ru or ru in a:
                return code
    return None


def find_college_code(text: str) -> Optional[str]:
    m = re.search(r'E(\d{2,3})', str(text))
    return f"E{m.group(1)}" if m else None


def parse_rank(val) -> Optional[int]:
    if val is None: return None
    v = str(val).strip().replace(",", "").replace(" ", "")
    if not v or v in {"-", "--", "---", "—", "", "N/A", "NA", "NULL"}:
        return None
    try:
        iv = int(float(v))
        return iv if iv > 0 else None
    except (ValueError, TypeError):
        return None


def is_valid_category(text: str) -> bool:
    return text.strip().upper() in ALL_CATEGORIES


def normalize_category(text: str) -> str:
    return text.strip().upper()


# ── Strategy 1: pdfplumber Table Extraction ─────────────────

def parse_with_pdfplumber(pdf_path: str) -> List[Dict]:
    """
    Parse PDF using pdfplumber's table detection.
    Handles the standard KCET cutoff table format where each row contains:
      CollegeCode | CollegeName | Course | Category | R1_cutoff | R2_cutoff | R3_cutoff
    """
    import pdfplumber
    records = []
    current_college_code = None
    current_college_name = None

    print(f"  PDF pages: ", end="", flush=True)
    with pdfplumber.open(pdf_path) as pdf:
        print(f"{len(pdf.pages)}", flush=True)

        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            if not tables:
                continue

            for table in tables:
                for row_idx, row in enumerate(table):
                    if not row:
                        continue

                    # Clean cells
                    cells = []
                    for c in row:
                        s = str(c).strip() if c else ""
                        cells.append(s)

                    # Skip empty rows and headers
                    text = " ".join(cells).strip()
                    if not text or len(text) < 5:
                        continue
                    if any(h in text.upper() for h in ["COLLEGE CODE", "COLLEGE NAME", "SI.NO",
                                                         "SL.NO", "SNO", "CUTOFF", "ROUND"]):
                        continue

                    # Try to extract a record from this row
                    rec = _parse_row(cells)
                    if rec:
                        records.append(rec)
                        # Track current college for context
                        current_college_code = rec.get("college_code")

            if page_num % 5 == 0:
                print(f"{page_num}..", end="", flush=True)

    print(f" done")
    print(f"  Raw extracted: {len(records)} records")
    return records


def _parse_row(cells: List[str]) -> Optional[Dict]:
    """Parse a single row from a KCET cutoff table."""
    if len(cells) < 4:
        return None

    # Step 1: Find college code
    college_code = None
    college_name = ""
    course_code = None
    category = None
    rank_values = []

    for cell in cells:
        cc = find_college_code(cell)
        if cc:
            college_code = cc
            break

    if not college_code:
        return None

    # Step 2: Find category in cells
    cat_idx = None
    for i, cell in enumerate(cells):
        if is_valid_category(cell):
            category = normalize_category(cell)
            cat_idx = i
            break

    if not category:
        return None

    # Step 3: Find course code (before the category)
    for i in range(cat_idx):
        cc = normalize_course(cells[i])
        if cc:
            course_code = cc
            break

    if not course_code:
        # Try matching any cell before category
        for i in range(cat_idx):
            if find_college_code(cells[i]):
                continue
            cc = normalize_course(cells[i])
            if cc:
                course_code = cc
                break

    if not course_code:
        return None

    # Step 4: Extract college name (cells between college code and course, that are not codes)
    code_idx = None
    for i, cell in enumerate(cells):
        if find_college_code(cell):
            code_idx = i
            break

    if code_idx is not None:
        name_parts = []
        for i in range(code_idx + 1, cat_idx):
            v = cells[i].strip()
            if v and not find_college_code(v) and not normalize_course(v) and v != course_code:
                name_parts.append(v)
        college_name = " ".join(name_parts).strip()

    # Step 5: Extract rank values (cells after category)
    for i in range(cat_idx + 1, len(cells)):
        r = parse_rank(cells[i])
        if r is not None:
            rank_values.append(r)

    # Assign ranks to rounds
    r1 = rank_values[0] if len(rank_values) >= 1 else None
    r2 = rank_values[1] if len(rank_values) >= 2 else None
    r3 = rank_values[2] if len(rank_values) >= 3 else None

    return {
        "college_code": college_code,
        "college_name": college_name or f"College {college_code}",
        "course_code": course_code,
        "course_name": "",  # filled later
        "category": category,
        "round_1_cutoff": r1,
        "round_2_cutoff": r2,
        "round_3_cutoff": r3,
    }


# ── Strategy 2: pdfplumber Word-level Extraction ────────────

def parse_with_words(pdf_path: str) -> List[Dict]:
    """
    Parse PDF using pdfplumber's word-level extraction with positional analysis.
    Good for PDFs where tables aren't detected but words are spatially arranged.
    """
    import pdfplumber
    records = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words()
            if not words:
                continue

            # Group words by their vertical position (y-coordinate) — each row is at a y-level
            rows_dict = defaultdict(list)
            for w in words:
                y_key = round(w["top"], 0)  # round to group close y values
                rows_dict[y_key].append(w)

            # Sort rows by y position (top to bottom)
            sorted_rows = sorted(rows_dict.values(), key=lambda r: r[0]["top"])

            for row_words in sorted_rows:
                # Sort words in row by x position (left to right)
                row_words.sort(key=lambda w: w["x0"])
                texts = [w["text"].strip() for w in row_words]
                rec = _parse_row(texts)
                if rec:
                    # De-duplicate
                    key = (rec["college_code"], rec["course_code"],
                           rec["category"], rec["round_1_cutoff"],
                           rec["round_2_cutoff"], rec["round_3_cutoff"])
                    if not any(
                        r["college_code"] == rec["college_code"] and
                        r["course_code"] == rec["course_code"] and
                        r["category"] == rec["category"]
                        for r in records
                    ):
                        records.append(rec)

    return records


def parse_college_block_tables(pdf_path: str) -> List[Dict]:
    """
    Parse PDFs formatted as per-college blocks where a page begins with
    'College: E###' and contains wide tables where columns are category tokens
    (e.g., '1G','2AG','3AG','GM','STG'). This function flattens the table into
    records of the form used by the import pipeline:
      {college_code, college_name, course_name, category, round, cutoff_rank}
    """
    import pdfplumber

    records: List[Dict] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            # Try to extract college code and name from the page text
            cc_match = re.search(r"College:\s*(?:\()?\s*(E\d{2,3})", text, re.IGNORECASE)
            college_code = cc_match.group(1) if cc_match else None
            name_match = re.search(r"College:\s*(.*)", text)
            college_name = name_match.group(1).split('\n')[0].strip() if name_match else ""

            tables = page.extract_tables() or []
            for table in tables:
                if not table:
                    continue
                # Header row should contain 'Course' in first cell
                header = [str(c).strip() if c else "" for c in table[0]]
                if not header or 'COURSE' not in header[0].upper():
                    continue

                # Process course rows
                for row in table[1:]:
                    if not row:
                        continue
                    cells = [str(c).strip() if c else "" for c in row]
                    course_name = cells[0].replace('\n', ' ').strip()
                    if not course_name:
                        continue

                    course_code = normalize_course(course_name)
                    if not course_code:
                        # Try to infer from substrings if the full course name is long
                        for token in re.split(r"[\s/,&()]+", course_name):
                            course_code = normalize_course(token)
                            if course_code:
                                break

                    if not course_code:
                        continue

                    category_round_map = {}
                    for idx in range(1, min(len(cells), len(header))):
                        h = header[idx].strip()
                        if not h:
                            continue
                        token = re.sub(r'[^A-Za-z0-9]', '', h).upper()
                        if not token:
                            continue

                        val = parse_rank(cells[idx])
                        if val is None:
                            continue

                        if token not in category_round_map:
                            category_round_map[token] = {
                                'college_code': college_code or '',
                                'college_name': college_name or '',
                                'course_code': course_code,
                                'course_name': course_name,
                                'category': token,
                                'round_1_cutoff': None,
                                'round_2_cutoff': None,
                                'round_3_cutoff': None,
                            }

                        # All columns in this PDF are essentially round 2 values
                        category_round_map[token]['round_2_cutoff'] = val

                    records.extend(category_round_map.values())

    return records


# ── Strategy 3: PyMuPDF Table Detection ─────────────────────

def parse_with_pymupdf(pdf_path: str) -> List[Dict]:
    """Parse using PyMuPDF's table detection (alternative engine)."""
    import fitz

    doc = fitz.open(pdf_path)
    records = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        try:
            tabs = page.find_tables()
            for tab in tabs:
                for row in tab.extract():
                    cells = [str(c).strip() if c else "" for c in row]
                    rec = _parse_row(cells)
                    if rec:
                        records.append(rec)
        except Exception:
            # Fallback to text extraction
            text = page.get_text("text")
            lines = text.split("\n")
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                # Look for E-code patterns
                cc = find_college_code(line)
                if cc:
                    # Check surrounding lines for more context
                    context = " ".join(lines[max(0, i - 1):i + 3])
                    cells = context.split()
                    rec = _parse_row(cells)
                    if rec:
                        records.append(rec)

    doc.close()
    return records


# ── Post-processing ─────────────────────────────────────────

def deduplicate(records: List[Dict]) -> List[Dict]:
    """Remove duplicate college-course-category combinations."""
    seen = set()
    unique = []
    for rec in records:
        key = (rec["college_code"], rec["course_code"], rec["category"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(rec)
    print(f"  After dedup: {len(unique)} unique college-course-category combos")
    return unique


def fill_course_names(records: List[Dict]) -> None:
    """Fill in full course names based on course codes."""
    course_names = {
        "CS": "Computer Science & Engineering",
        "IS": "Information Science & Engineering",
        "EC": "Electronics & Communication Engineering",
        "ME": "Mechanical Engineering",
        "CE": "Civil Engineering",
        "AI": "Artificial Intelligence & Machine Learning",
        "DS": "Data Science",
        "BT": "Biotechnology",
    }
    for rec in records:
        cc = rec.get("course_code")
        if cc and not rec.get("course_name"):
            rec["course_name"] = course_names.get(cc, cc)


def build_master_lists(records: List[Dict]) -> Tuple[Dict, Dict]:
    """Build college and course master lists from records."""
    colleges = {}
    courses = {}
    for rec in records:
        cc = rec["college_code"]
        if cc and cc not in colleges:
            colleges[cc] = {
                "college_code": cc,
                "college_name": rec.get("college_name", f"College {cc}"),
                "location": "",
                "college_type": infer_college_type(rec.get("college_name", "")),
            }
        co = rec["course_code"]
        if co and co not in courses:
            courses[co] = {
                "course_code": co,
                "course_name": rec.get("course_name", co),
                "stream_group": "Engineering",
            }
    return colleges, courses


# ── Output ──────────────────────────────────────────────────

def save_outputs(records: List[Dict], colleges: Dict, courses: Dict,
                 output_dir: str, pdf_path: str):
    """Save parsed data to JSON files and generate Python module."""
    os.makedirs(output_dir, exist_ok=True)

    # ── 1. Full cutoffs JSON ──
    json_path = os.path.join(output_dir, "pdf_cutoffs_all.json")
    cat_counts = defaultdict(int)
    for r in records:
        cat_counts[r["category"]] += 1

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "source": pdf_path,
            "total_records": len(records),
            "total_colleges": len(colleges),
            "total_courses": len(courses),
            "categories_found": sorted(cat_counts.keys()),
            "records_per_category": dict(cat_counts),
            "records": records,
        }, f, indent=2, default=str)
    print(f"\n  ✅ All cutoffs -> {json_path}")

    # ── 2. Colleges JSON ──
    col_path = os.path.join(output_dir, "pdf_colleges.json")
    with open(col_path, "w", encoding="utf-8") as f:
        json.dump({"total": len(colleges), "colleges": list(colleges.values())}, f, indent=2)
    print(f"  ✅ Colleges     -> {col_path}")

    # ── 3. Courses JSON ──
    crs_path = os.path.join(output_dir, "pdf_courses.json")
    with open(crs_path, "w", encoding="utf-8") as f:
        json.dump({"total": len(courses), "courses": list(courses.values())}, f, indent=2)
    print(f"  ✅ Courses      -> {crs_path}")

    # ── 4. Summary ──
    summary_path = os.path.join(output_dir, "pdf_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "source": pdf_path,
            "total_records": len(records),
            "total_colleges": len(colleges),
            "total_courses": len(courses),
            "categories_found": sorted(cat_counts.keys()),
            "records_per_category": dict(cat_counts),
            "college_codes": sorted(colleges.keys()),
            "course_codes": sorted(courses.keys()),
            "records_with_r1": sum(1 for r in records if r.get("round_1_cutoff")),
            "records_with_r2": sum(1 for r in records if r.get("round_2_cutoff")),
            "records_with_r3": sum(1 for r in records if r.get("round_3_cutoff")),
        }, f, indent=2)
    print(f"  ✅ Summary      -> {summary_path}")

    # ── 5. Python module ──
    py_path = os.path.join(output_dir, "pdf_import.py")
    _generate_python_module(records, colleges, courses, py_path)
    print(f"  ✅ Python mod   -> {py_path}")

    # ── Summary ──
    print(f"\n  {'='*55}")
    print(f"  PARSING RESULTS")
    print(f"  {'='*55}")
    print(f"  Records:      {len(records)}")
    print(f"  Colleges:     {len(colleges)}")
    print(f"  Courses:      {len(courses)}")
    print(f"  Categories:   {', '.join(sorted(cat_counts.keys()))}")
    print(f"  Per category:")
    for cat in sorted(cat_counts.keys()):
        print(f"    {cat}: {cat_counts[cat]} records")
    print(f"  R1 data:      {sum(1 for r in records if r.get('round_1_cutoff'))}")
    print(f"  R2 data:      {sum(1 for r in records if r.get('round_2_cutoff'))}")
    print(f"  R3 data:      {sum(1 for r in records if r.get('round_3_cutoff'))}")
    print(f"  {'='*55}\n")


def _generate_python_module(records: List[Dict], colleges: Dict, courses: Dict,
                            output_path: str):
    """Generate a Python module for direct import by the backend."""
    sorted_records = sorted(records, key=lambda r: (r["college_code"], r["course_code"], r["category"]))
    sorted_colleges = sorted(colleges.keys())
    sorted_courses = sorted(courses.keys())

    lines = [
        '"""',
        'Auto-generated KCET PDF All-Category Cutoff Data',
        'Generated by parse_kcet_pdf.py',
        '"""',
        "",
        "from typing import Dict, List, Optional",
        "",
        "# ── College Master Data ────────────────────────────",
        "COLLEGES: Dict[str, Dict] = {",
    ]
    for code in sorted_colleges:
        c = colleges[code]
        lines.append(f'    "{code}": {{')
        lines.append(f'        "college_code": "{code}",')
        lines.append(f'        "college_name": {json.dumps(c["college_name"])},')
        lines.append(f'        "location": {json.dumps(c.get("location", ""))},')
        lines.append(f'        "college_type": {json.dumps(c.get("college_type", "Private-Unaided"))},')
        lines.append("    },")
    lines.append("}")
    lines.append("")

    lines.append("# ── Course Master Data ─────────────────────────────")
    lines.append("COURSES: Dict[str, Dict] = {")
    for code in sorted_courses:
        c = courses[code]
        lines.append(f'    "{code}": {{')
        lines.append(f'        "course_code": "{code}",')
        lines.append(f'        "course_name": {json.dumps(c["course_name"])},')
        lines.append(f'        "stream_group": {json.dumps(c.get("stream_group", "Engineering"))},')
        lines.append("    },")
    lines.append("}")
    lines.append("")

    lines.append("# ── Cutoff Records (Col × Course × Category × 3 Rounds) ───")
    lines.append("ALL_CUTOFFS: List[Dict] = [")
    for rec in sorted_records:
        lines.append("    {")
        lines.append(f'        "college_code": {json.dumps(rec["college_code"])},')
        lines.append(f'        "college_name": {json.dumps(rec.get("college_name", ""))},')
        lines.append(f'        "course_code": {json.dumps(rec["course_code"])},')
        lines.append(f'        "course_name": {json.dumps(rec.get("course_name", ""))},')
        lines.append(f'        "category": {json.dumps(rec["category"])},')
        lines.append(f'        "round_1_cutoff": {rec.get("round_1_cutoff")},')
        lines.append(f'        "round_2_cutoff": {rec.get("round_2_cutoff")},')
        lines.append(f'        "round_3_cutoff": {rec.get("round_3_cutoff")},')
        lines.append("    },")
    lines.append("]")
    lines.append("")

    # Gather stats
    cats_found = sorted(set(r["category"] for r in records))
    lines.append(f"""
# ── Helpers ───────────────────────────────────────────────

def get_cutoffs_by_category(category: str) -> List[Dict]:
    \"\"\"Get cutoff records for a specific category.\"\"\"
    return [r for r in ALL_CUTOFFS if r["category"] == category]

def get_all_categories() -> List[str]:
    return {json.dumps(cats_found)}

def get_colleges_list() -> List[Dict]:
    return list(COLLEGES.values())

def get_courses_list() -> List[Dict]:
    return list(COURSES.values())

def get_locations() -> List[str]:
    return sorted(set(c["location"] for c in COLLEGES.values() if c.get("location")))
""")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ── Main Orchestration ──────────────────────────────────────

def parse_pdf(pdf_path: str) -> List[Dict]:
    """Try multiple strategies to extract data from the PDF."""
    all_records = []
    
    # Strategy 0: Per-college table blocks (mock allotment PDFs)
    print("  Strategy 0: per-college table block extraction...")
    try:
        recs = parse_college_block_tables(pdf_path)
        if recs:
            all_records.extend(recs)
            print(f"    -> {len(recs)} records from college-block tables")
        else:
            print("    -> 0 records from college-block tables")
    except Exception as e:
        print(f"    -> Failed: {e}")

    # Strategy 1: pdfplumber table extraction
    print("  Strategy 1: pdfplumber table extraction...")
    try:
        recs = parse_with_pdfplumber(pdf_path)
        all_records.extend(recs)
        print(f"    -> {len(recs)} records")
    except Exception as e:
        print(f"    -> Failed: {e}")

    # Strategy 2: pdfplumber word-level extraction
    print("  Strategy 2: pdfplumber word-level extraction...")
    try:
        recs = parse_with_words(pdf_path)
        # Only add ones we don't already have
        existing = {(r["college_code"], r["course_code"], r["category"]) for r in all_records}
        new = [r for r in recs if (r["college_code"], r["course_code"], r["category"]) not in existing]
        all_records.extend(new)
        print(f"    -> {len(recs)} found, {len(new)} new")
    except Exception as e:
        print(f"    -> Failed: {e}")

    # Strategy 3: PyMuPDF
    print("  Strategy 3: PyMuPDF table extraction...")
    try:
        recs = parse_with_pymupdf(pdf_path)
        existing = {(r["college_code"], r["course_code"], r["category"]) for r in all_records}
        new = [r for r in recs if (r["college_code"], r["course_code"], r["category"]) not in existing]
        all_records.extend(new)
        print(f"    -> {len(recs)} found, {len(new)} new")
    except Exception as e:
        print(f"    -> Skipped (fitz not installed): {e}" if "fitz" in str(e) else f"    -> Failed: {e}")

    return deduplicate(all_records)


def main():
    parser = argparse.ArgumentParser(description="Parse KCET 2025-26 Cutoff PDF (all categories)")
    parser.add_argument("--pdf", default=DEFAULT_PDF_PATH, help="Path to PDF file")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="Output directory")
    args = parser.parse_args()

    pdf_path = args.pdf
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        sys.exit(1)

    print(f"\n  {'='*60}")
    print(f"  KCET PDF PARSER — ALL CATEGORIES")
    print(f"  {'='*60}")
    print(f"  File: {pdf_path}")
    print(f"  Size: {os.path.getsize(pdf_path) / 1024 / 1024:.1f} MB")

    if not ensure_deps():
        sys.exit(1)

    records = parse_pdf(pdf_path)

    if not records:
        print("\n  ❌ No structured data could be extracted.")
        print("  The PDF format may be unusual. Saving raw text dump...")
        try:
            from pdfminer.high_level import extract_text
            text = extract_text(pdf_path)
            dump_path = "raw_pdf_text.txt"
            with open(dump_path, "w", encoding="utf-8") as f:
                f.write(text[:100000])
            print(f"  Raw text saved to {dump_path}")
        except Exception as e:
            print(f"  Could not dump text: {e}")
        sys.exit(1)

    fill_course_names(records)
    colleges, courses = build_master_lists(records)
    save_outputs(records, colleges, courses, args.output_dir, pdf_path)

    print("  Next steps:")
    print("  1. Run: python parse_kcet_pdf.py")
    print("  2. Restart the backend — it will auto-detect the PDF data")
    print()

    return records, colleges, courses


if __name__ == "__main__":
    main()
