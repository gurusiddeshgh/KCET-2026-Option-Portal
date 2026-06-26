"""
KEA 2025 Data Loader
====================
Loads real KCET 2025-26 cutoff data for ALL 8 categories from parsed output.

Data sources (tried in order):
1. parsed_data/pdf_import.py — from the PDF (all categories: GM, 2AR, 3BK, SCG, STK, GMEWS, 2A, 3A)
2. parsed_data/kea_import.py — from the Excel (GM only)
3. Fallback to mock data in database.py

Enriches data with college location/type info from the known KCET seat matrix.
"""

import sys
import os
import json
from typing import Dict, List, Optional
from collections import defaultdict

# ── Known College Location/Type Mapping (from KCET seat matrix) ──
# Used to enrich real KEA 2025 data which may only have college codes and names.
KNOWN_COLLEGE_INFO = {
    # Bangalore
    "E001": {"location": "Bangalore", "college_type": "Government"},
    "E002": {"location": "Bangalore", "college_type": "Government"},
    "E003": {"location": "Bangalore", "college_type": "Private-Aided"},
    "E004": {"location": "Bangalore", "college_type": "Private-Aided"},
    "E005": {"location": "Bangalore", "college_type": "Private-Unaided"},
    "E006": {"location": "Bangalore", "college_type": "Private-Unaided"},
    "E007": {"location": "Bangalore", "college_type": "Private-Unaided"},
    "E008": {"location": "Bangalore", "college_type": "Private-Unaided"},
    "E009": {"location": "Bangalore", "college_type": "Private-Unaided"},
    "E010": {"location": "Bangalore", "college_type": "Private-Unaided"},
    "E082": {"location": "Bangalore", "college_type": "Private-Unaided"},
    "E095": {"location": "Bangalore", "college_type": "Private-Unaided"},
    "E103": {"location": "Bangalore", "college_type": "Private-Unaided"},
    "E145": {"location": "Bangalore", "college_type": "Private-Unaided"},
    "E149": {"location": "Bangalore", "college_type": "Private-Unaided"},
    # Mysore
    "E021": {"location": "Mysore", "college_type": "Government"},
    "E022": {"location": "Mysore", "college_type": "Government"},
    "E057": {"location": "Mysore", "college_type": "Private-University"},
    "E071": {"location": "Mysore", "college_type": "Private-Unaided"},
    # Belgaum
    "E029": {"location": "Belgaum", "college_type": "Private-Unaided"},
    "E036": {"location": "Belgaum", "college_type": "Private-University"},
    "E037": {"location": "Belgaum", "college_type": "Private-Unaided"},
    "E175": {"location": "Belgaum", "college_type": "Private-Unaided"},
    "E185": {"location": "Belgaum", "college_type": "Private-Unaided"},
    # Hubballi
    "E265": {"location": "Hubballi", "college_type": "Private-Unaided"},
    "E241": {"location": "Hubballi", "college_type": "Private-University"},
    # Mangalore
    "E144": {"location": "Mangalore", "college_type": "Private-Unaided"},
    "E146": {"location": "Mangalore", "college_type": "Private-Unaided"},
    "E151": {"location": "Mangalore", "college_type": "Private-Unaided"},
    "E159": {"location": "Mangalore", "college_type": "Private-Unaided"},
    "E160": {"location": "Mangalore", "college_type": "Private-Unaided"},
    # Hassan
    "E024": {"location": "Hassan", "college_type": "Government"},
    "E155": {"location": "Hassan", "college_type": "Government"},
    # Davangere
    "E061": {"location": "Davangere", "college_type": "Government"},
    "E062": {"location": "Davangere", "college_type": "Private-Unaided"},
    "E114": {"location": "Davangere", "college_type": "Private-Unaided"},
    # Tumkur
    "E016": {"location": "Tumkur", "college_type": "Private-Unaided"},
    "E130": {"location": "Tumkur", "college_type": "Private-Unaided"},
    # Chikkaballapur
    "E014": {"location": "Chikkaballapur", "college_type": "Private-Unaided"},
    "E278": {"location": "Chikkaballapur", "college_type": "Government"},
    # Gulbarga
    "E041": {"location": "Gulbarga", "college_type": "Government"},
    "E128": {"location": "Gulbarga", "college_type": "Private-University"},
    # Raichur
    "E046": {"location": "Raichur", "college_type": "Private-Unaided"},
    "E162": {"location": "Raichur", "college_type": "Government"},
    "E176": {"location": "Raichur", "college_type": "Private-Unaided"},
    # Ballari
    "E045": {"location": "Ballari", "college_type": "Private-Unaided"},
    "E075": {"location": "Ballari", "college_type": "Private-Unaided"},
    # Kolar
    "E015": {"location": "Kolar", "college_type": "Private-Unaided"},
    "E184": {"location": "Kolar", "college_type": "Private-Unaided"},
    # Mandya
    "E023": {"location": "Mandya", "college_type": "Government"},
    "E210": {"location": "Mandya", "college_type": "Private-Unaided"},
    # Gadag
    "E028": {"location": "Gadag", "college_type": "Private-Unaided"},
    # Bidar
    "E044": {"location": "Bidar", "college_type": "Private-Unaided"},
    # Shivamogga
    "E065": {"location": "Shivamogga", "college_type": "Private-Unaided"},
    "E150": {"location": "Shivamogga", "college_type": "Private-Unaided"},
    # Sullia
    "E054": {"location": "Sullia", "college_type": "Private-Unaided"},
}

# ── Category Relative Difficulty Multipliers ──
CATEGORY_MULTIPLIERS = {
    "GM":    1.00,
    "2AR":   1.35,
    "3BK":   1.50,
    "SCG":   2.20,
    "STK":   2.80,
    "GMEWS": 1.10,
    "2A":    1.40,
    "3A":    1.55,
}

ALL_CATEGORIES = ["GM", "2AR", "3BK", "SCG", "STK", "GMEWS", "2A", "3A"]


def _enrich_record(rec: Dict) -> Dict:
    """Add location and college_type if missing, using known mapping."""
    cc = rec.get("college_code", "")
    info = KNOWN_COLLEGE_INFO.get(cc, {})
    rec["location"] = rec.get("location") or info.get("location", "")
    rec["college_type"] = rec.get("college_type") or info.get("college_type", "Private-Unaided")
    rec["stream_group"] = "Engineering"
    # Ensure category is set
    if "category" not in rec or not rec["category"]:
        rec["category"] = "GM"
    return rec


def _load_module(module_name: str, source_desc: str) -> Optional[Dict]:
    """Try to load data from a Python module in parsed_data/."""
    try:
        mod = __import__(module_name)
        # Support both old (kea_import) and new (pdf_import) module interfaces
        if hasattr(mod, "ALL_CUTOFFS"):
            records = mod.ALL_CUTOFFS
        elif hasattr(mod, "CUTOFF_RECORDS"):
            records = mod.CUTOFF_RECORDS
        else:
            return None

        colleges_raw = getattr(mod, "COLLEGES", {})
        courses_raw = getattr(mod, "COURSES", {})

        # Enrich with location info
        for r in records:
            _enrich_record(r)
        for cc, cinfo in KNOWN_COLLEGE_INFO.items():
            if cc in colleges_raw:
                colleges_raw[cc]["location"] = colleges_raw[cc].get("location") or cinfo["location"]
                colleges_raw[cc]["college_type"] = colleges_raw[cc].get("college_type") or cinfo["college_type"]

        # Count categories
        cats = set(r.get("category") for r in records)
        print(f"[DataLoader] [OK] Loaded {len(records)} records from {source_desc} "
              f"({len(colleges_raw)} colleges, {len(courses_raw)} courses, {len(cats)} categories: {sorted(cats)})")
        return {"records": records, "colleges": colleges_raw, "courses": courses_raw, "source": source_desc}
    except (ImportError, AttributeError) as e:
        return None


def _load_json(json_filename: str, source_desc: str) -> Optional[Dict]:
    """Try to load data from a JSON file in parsed_data/."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(project_root, "parsed_data", json_filename)
    if not os.path.exists(json_path):
        return None
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        raw_records = data.get("records", data.get("cutoffs", []))
        records = [dict(r) for r in raw_records]  # copy
        colleges_raw = {}
        for c in data.get("colleges", []):
            if isinstance(c, dict) and "college_code" in c:
                colleges_raw[c["college_code"]] = dict(c)
        courses_raw = {}
        for c in data.get("courses", []):
            if isinstance(c, dict) and "course_code" in c:
                courses_raw[c["course_code"]] = dict(c)
        for r in records:
            _enrich_record(r)
        cats = set(r.get("category") for r in records)
        print(f"[DataLoader] [OK] Loaded {len(records)} records from JSON ({source_desc}) "
              f"({len(colleges_raw)} colleges, {len(courses_raw)} courses, {len(cats)} categories)")
        return {"records": records, "colleges": colleges_raw, "courses": courses_raw, "source": json_path}
    except Exception as e:
        return None


def load_real_data() -> Optional[Dict]:
    """
    Attempt to load real KCET 2025-26 cutoff data.
    
    Priority:
    1. PDF data (all categories) — Python module
    2. PDF data (all categories) — JSON
    3. Excel data (GM only) — Python module
    4. Excel data (GM only) — JSON
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parsed_data_dir = os.path.join(project_root, "parsed_data")
    if parsed_data_dir not in sys.path:
        sys.path.insert(0, parsed_data_dir)

    # Strategy 1: PDF Python module (all categories) — BEST
    data = _load_module("pdf_import", "PDF (all categories)")
    if data:
        return data

    # Strategy 2: PDF JSON
    data = _load_json("pdf_cutoffs_all.json", "PDF")
    if data:
        return data

    # Strategy 3: Excel Python module (GM only)
    data = _load_module("kea_import", "Excel (GM only)")
    if data:
        return data

    # Strategy 4: Excel JSON
    data = _load_json("kea_cutoffs_2025.json", "Excel (GM only)")
    if data:
        return data

    print("[DataLoader] ⚠ No real cutoff data found. Using fallback mock data.")
    return None


def estimate_category_cutoffs(gm_records: List[Dict], category: str) -> List[Dict]:
    """
    Estimate cutoff ranks for non-GM categories by applying historical multipliers
    to the real GM cutoff data. Used as fallback when only GM data is available.
    """
    multiplier = CATEGORY_MULTIPLIERS.get(category, 1.0)
    if category == "GM":
        return gm_records
    estimated = []
    for rec in gm_records:
        r1 = rec.get("round_1_cutoff")
        r2 = rec.get("round_2_cutoff")
        r3 = rec.get("round_3_cutoff")
        estimated.append({
            "college_code": rec["college_code"],
            "college_name": rec["college_name"],
            "course_code": rec["course_code"],
            "course_name": rec["course_name"],
            "location": rec.get("location", ""),
            "college_type": rec.get("college_type", "Unknown"),
            "stream_group": rec.get("stream_group", "Engineering"),
            "category": category,
            "round_1_cutoff": int(r1 * multiplier) if r1 else None,
            "round_2_cutoff": int(r2 * multiplier) if r2 else None,
            "round_3_cutoff": int(r3 * multiplier) if r3 else None,
        })
    return estimated


def _has_all_categories(records: List[Dict]) -> bool:
    """Check if records contain data for all 8 KCET categories."""
    cats = set(r.get("category") for r in records)
    return len(cats) >= 8


def get_cutoffs_by_category(category: str = "GM") -> Optional[List[Dict]]:
    """
    Get cutoff records for a specific category.
    
    - If data has all 8 categories: filters directly by category.
    - If data has only GM: estimates other categories via historical multipliers.
    - If no real data: returns None (caller falls back to mock data).
    """
    if not _real_data:
        return None
    records = _real_data["records"]
    if _has_all_categories(records):
        return [r for r in records if r.get("category") == category]
    else:
        # Only GM data available — estimate other categories
        gm_records = [r for r in records if r.get("category") == "GM"]
        if category == "GM":
            return gm_records
        return estimate_category_cutoffs(gm_records, category)


def get_real_colleges() -> Optional[List[Dict]]:
    return list(_real_data["colleges"].values()) if _real_data else None


def get_real_courses() -> Optional[List[Dict]]:
    return list(_real_data["courses"].values()) if _real_data else None


def has_real_data() -> bool:
    return _real_data is not None


def get_data_source() -> str:
    if _real_data:
        cats_in_data = set(r.get("category") for r in _real_data["records"])
        return f"Real KCET 2025 data ({_real_data['source']}) — categories: {sorted(cats_in_data)}"
    return "Fallback mock data"


def get_locations_from_data(colleges_list: List[Dict]) -> List[str]:
    return sorted(set(c.get("location", "") for c in colleges_list if c.get("location")))


# ── Singleton: Load once at import time ──
_real_data = load_real_data()