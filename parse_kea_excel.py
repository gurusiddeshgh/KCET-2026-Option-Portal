#!/usr/bin/env python3
"""
KEA 2025 GM Cutoff Excel Parser
================================
Parses the official KEA 2025 GM category cutoff Excel file (Rounds 1, 2, 3)
and outputs structured data for use by the KCET Predictor backend.

Outputs (in parsed_data/):
  - kea_cutoffs_2025.json       â€” Full structured cutoff records
  - kea_colleges_2025.json      â€” College master list extracted from Excel
  - kea_courses_2025.json       â€” Course master list
  - kea_import.py               â€” Direct Python data module for the backend

Usage:
  python parse_kea_excel.py

Dependencies:
  pip install pandas openpyxl
  (both are lightweight; pandas is already in backend/requirements.txt)
"""

import os
import sys
import json
import argparse
from collections import defaultdict
from typing import List, Dict, Optional, Tuple

# â”€â”€ Configuration â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
DEFAULT_EXCEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "KEA_2025_Master_GM_CutOffs_Round123.xlsx"
)
OUTPUT_DIR = "parsed_data"

# Full course name â†’ standardized (code, display_name) mapping
# Covers all course variants found in KEA 2025 Excel data
COURSE_FULL_NAME_MAP: list = [
    # --- Computer Science variants ---
    ("COMPUTER SCIENCE AND ENGINEERING",                 "CSE",   "Computer Science & Engineering"),
    ("COMPUTER SCIENCE & ENGINEERING",                  "CSE",   "Computer Science & Engineering"),
    ("COMPUTER SCIENCE AND ENGG",                       "CSE",   "Computer Science & Engineering"),
    ("COMPUTER SCIENCE ENGG",                           "CSE",   "Computer Science & Engineering"),
    ("COMPUTER ENGINEERING",                            "CSE",   "Computer Science & Engineering"),
    ("COMPUTER SCIENCE",                                "CSE",   "Computer Science & Engineering"),
    ("COMPUTER AND COMMUNICATION ENGINEERING",          "CCE",   "Computer & Communication Engineering"),
    ("COMPUTER SCIENCE AND TECHNOLOGY",                 "CST",   "Computer Science & Technology"),
    ("COMPUTER SCIENCE & TECHNOLOGY",                   "CST",   "Computer Science & Technology"),
    ("COMPUTER SCIENCE AND BUSINESS SYSTEMS",           "CBS",   "Computer Science & Business Systems"),
    ("COMPUTER BUSINESS SYSTEMS",                       "CBS",   "Computer Science & Business Systems"),
    ("COMPUTER SCIENCE AND DESIGN",                     "CSD",   "Computer Science & Design"),
    ("COMPUTER DESIGN",                                 "CSD",   "Computer Science & Design"),
    # --- AI/ML/DS variants ---
    ("ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",        "AIDS",  "AI & Data Science"),
    ("ARTIFICIAL INTELLIGENCE & DATA SCIENCE",          "AIDS",  "AI & Data Science"),
    ("ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",    "AIML",  "AI & Machine Learning"),
    ("ARTIFICIAL INTELLIGENCE & MACHINE LEARNING",      "AIML",  "AI & Machine Learning"),
    ("ARTIFICIAL INTELLIGENCE",                         "AI",    "Artificial Intelligence"),
    ("DATA SCIENCE",                                    "DS",    "Data Science"),
    ("INTELLIGENCE AND DATA SCIENCE",                   "AIDS",  "AI & Data Science"),
    # --- Information Science variants ---
    ("INFORMATION SCIENCE AND ENGINEERING",             "ISE",   "Information Science & Engineering"),
    ("INFORMATION SCIENCE & ENGINEERING",               "ISE",   "Information Science & Engineering"),
    ("INFORMATION SCIENCE",                             "ISE",   "Information Science & Engineering"),
    ("INFORMATION ENGINEERING",                         "ISE",   "Information Science & Engineering"),
    ("INFORMATION TECHNOLOGY",                          "IT",    "Information Technology"),
    # --- Electronics variants ---
    ("ELECTRONICS AND COMMUNICATION ENGINEERING",       "ECE",   "Electronics & Communication Engineering"),
    ("ELECTRONICS & COMMUNICATION ENGINEERING",         "ECE",   "Electronics & Communication Engineering"),
    ("ELECTRONICS AND COMMUNICATION ENGG",              "ECE",   "Electronics & Communication Engineering"),
    ("ELECTRONICS COMMUNICATION ENGG",                  "ECE",   "Electronics & Communication Engineering"),
    ("ELECTRONICS AND COMPUTER ENGINEERING",            "ECE2",  "Electronics & Computer Engineering"),
    ("ELECTRONICS & COMPUTER ENGINEERING",              "ECE2",  "Electronics & Computer Engineering"),
    ("ELECTRONICS AND COMPUTER SCIENCE",                "ECS",   "Electronics & Computer Science"),
    ("ELECTRONICS AND INSTRUMENTATION ENGINEERING",     "EIE",   "Electronics & Instrumentation Engineering"),
    ("ELECTRONICS & INSTRUMENTATION ENGINEERING",       "EIE",   "Electronics & Instrumentation Engineering"),
    ("ELECTRONICS INSTRUMENTATION ENGINEERING",         "EIE",   "Electronics & Instrumentation Engineering"),
    ("ELECTRONICS AND TELECOMMUNICATION ENGINEERING",   "ETE",   "Electronics & Telecommunication Engineering"),
    ("ELECTRONICS TELECOMMUNICATION ENGINEERING",       "ETE",   "Electronics & Telecommunication Engineering"),
    ("ELECTRONICS ENGINEERING",                         "EE",    "Electronics Engineering"),
    ("ELECTRONICS LSI DESIGN",                          "VLSI",  "VLSI Design"),
    ("VLSI",                                            "VLSI",  "VLSI Design"),
    ("MEDICAL ELECTRONICS ENGINEERING",                 "MEE",   "Medical Electronics Engineering"),
    # --- Electrical variants ---
    ("ELECTRICAL AND ELECTRONICS ENGINEERING",          "EEE",   "Electrical & Electronics Engineering"),
    ("ELECTRICAL & ELECTRONICS ENGINEERING",            "EEE",   "Electrical & Electronics Engineering"),
    ("ELECTRICAL AND COMPUTER ENGINEERING",             "ECE3",  "Electrical & Computer Engineering"),
    ("ELECTRICAL & COMPUTER ENGINEERING",               "ECE3",  "Electrical & Computer Engineering"),
    ("ELECTRICAL ENGINEERING",                          "EEE",   "Electrical & Electronics Engineering"),
    # --- Mechanical variants ---
    ("MECHANICAL ENGINEERING",                          "ME",    "Mechanical Engineering"),
    ("MECHANICAL AND SMART MANUFACTURING",              "MSM",   "Mechanical & Smart Manufacturing"),
    ("MECHANICAL AND AEROSPACE ENGINEERING",            "MAE",   "Mechanical & Aerospace Engineering"),
    ("MECHATRONICS",                                    "MCT",   "Mechatronics Engineering"),
    ("MECHATRONICS ENGINEERING",                        "MCT",   "Mechatronics Engineering"),
    ("ROBOTICS AND AUTOMATION",                         "RA",    "Robotics & Automation"),
    ("ROBOTICS AND ARTIFICIAL INTELLIGENCE",            "RAI",   "Robotics & AI"),
    ("ROBOTICS AND INTELLIGENCE",                       "RAI",   "Robotics & AI"),
    ("ROBOTICS",                                        "RA",    "Robotics & Automation"),
    # --- Civil variants ---
    ("CIVIL ENGINEERING",                               "CE",    "Civil Engineering"),
    ("CIVIL ENVIRONMENTAL ENGINEERING",                 "CEE",   "Civil & Environmental Engineering"),
    ("CIVIL CONSTRUCTION AND SUSTAINABILITY",           "CE",    "Civil Engineering"),
    ("CONSTRUCTION TECHNOLOGY AND MGMT",                "CTM",   "Construction Technology & Management"),
    ("ENVIRONMENTAL ENGINEERING",                       "EVE",   "Environmental Engineering"),
    # --- Biomedical / Biotech variants ---
    ("BIOMEDICAL AND ROBOTIC ENGINEERING",              "BME",   "Biomedical Engineering"),
    ("BIOMEDICAL ENGINEERING",                          "BME",   "Biomedical Engineering"),
    ("BIO-MEDICAL ENGINEERING",                         "BME",   "Biomedical Engineering"),
    ("BIO-MEDICAL",                                     "BME",   "Biomedical Engineering"),
    ("MEDICAL ENGINEERING",                             "BME",   "Biomedical Engineering"),
    ("BIOTECHNOLOGY",                                   "BT",    "Biotechnology"),
    ("BIO-TECHNOLOGY",                                  "BT",    "Biotechnology"),
    ("BIOTECHNOLOGY & BIO- ENGINEERING",                "BT",    "Biotechnology"),
    # --- Chemical variants ---
    ("CHEMICAL ENGINEERING",                            "CHE",   "Chemical Engineering"),
    ("CHEMICAL",                                        "CHE",   "Chemical Engineering"),
    ("POLYMER SCIENCE & TECHNOLOGY",                    "PST",   "Polymer Science & Technology"),
    ("CERAMICS & CEMENT ENGINEERING",                   "CCE2",  "Ceramics & Cement Engineering"),
    ("PHARMACEUTICAL ENGINEERING",                      "PE",    "Pharmaceutical Engineering"),
    # --- Aerospace / Marine ---
    ("AERONAUTICAL ENGINEERING",                        "AER",   "Aeronautical Engineering"),
    ("AEROSPACE ENGINEERING",                           "AER",   "Aeronautical Engineering"),
    ("MARINE ENGINEERING",                              "MAR",   "Marine Engineering"),
    ("SPACE ENGINEERING",                               "SPC",   "Space Engineering"),
    # --- Mining / Production / Industrial ---
    ("MINING ENGINEERING",                              "MIN",   "Mining Engineering"),
    ("PRODUCTION ENGINEERING",                          "PRE",   "Production Engineering"),
    ("INDUSTRIAL AND PRODUCTION ENGINEERING",           "IPE",   "Industrial & Production Engineering"),
    ("INDUSTRIAL & PRODUCTION ENGINEERING",             "IPE",   "Industrial & Production Engineering"),
    ("INDUSTRIAL ENGINEERING AND MANAGEMENT",           "IEM",   "Industrial Engineering & Management"),
    ("INDUSTRIAL IOT",                                  "IIOT",  "Industrial IoT"),
    ("INDUSTRIAL DESIGN",                               "IND",   "Industrial Design"),
    ("INDUSTRIAL MANAGEMENT",                           "IEM",   "Industrial Engineering & Management"),
    # --- Cyber Security ---
    ("CYBER SECURITY",                                  "CYS",   "Cyber Security"),
    # --- IoT ---
    ("INTERNET OF THINGS",                              "IOT",   "Internet of Things"),
    # --- Design / Planning ---
    ("ENGINEERING DESIGN",                              "ED",    "Engineering Design"),
    ("COMMUNICATION DESIGN",                            "CMD",   "Communication Design"),
    ("FASHION DESIGN",                                  "FD",    "Fashion Design"),
    ("DESIGN",                                          "DES",   "Design"),
    ("PLANNING",                                        "PLAN",  "Planning"),
    ("B.PLAN",                                          "PLAN",  "Planning"),
    # --- Textiles ---
    ("TEXTILES TECHNOLOGY",                             "TXT",   "Textiles Technology"),
    ("SILK",                                            "TXT",   "Textiles Technology"),
    # --- Energy ---
    ("ENERGY ENGINEERING",                              "ENE",   "Energy Engineering"),
    # --- Agriculture ---
    ("AGRICULTURE ENGINEERING",                         "AGE",   "Agriculture Engineering"),
    # --- Petroleum ---
    ("PETROLEUM ENGINEERING",                           "PEP",   "Petroleum Engineering"),
]

# Backwards-compat short-code map for fallback
COURSE_MAP = {
    "CS":   "Computer Science & Engineering",
    "CSE":  "Computer Science & Engineering",
    "IS":   "Information Science & Engineering",
    "ISE":  "Information Science & Engineering",
    "EC":   "Electronics & Communication Engineering",
    "ECE":  "Electronics & Communication Engineering",
    "EE":   "Electrical & Electronics Engineering",
    "EEE":  "Electrical & Electronics Engineering",
    "ME":   "Mechanical Engineering",
    "MECH": "Mechanical Engineering",
    "CE":   "Civil Engineering",
    "CIV":  "Civil Engineering",
    "AI":   "Artificial Intelligence",
    "AIML": "AI & Machine Learning",
    "DS":   "Data Science",
    "BT":   "Biotechnology",
}

# College type inference
GOVT_KEYWORDS = ["government", "govt", "gov"]
UNIV_KEYWORDS = ["university", "univ"]
AIDED_KEYWORDS = ["aided", "grant-in-aid"]


def infer_college_type(name: str) -> str:
    nl = name.lower()
    if any(kw in nl for kw in GOVT_KEYWORDS): return "Government"
    if any(kw in nl for kw in UNIV_KEYWORDS): return "Private-University"
    if any(kw in nl for kw in AIDED_KEYWORDS): return "Private-Aided"
    return "Private-Unaided"


def normalize_course(raw: str) -> Optional[tuple]:
    """
    Normalize a full course name string (as it appears in the Excel) to
    a (course_code, display_name) tuple.

    Matching strategy:
    1. Strip the raw text and uppercase for comparison.
    2. Try each pattern in COURSE_FULL_NAME_MAP (longest/most-specific first).
    3. Fall back to keyword heuristics.
    Returns None if unrecognized.
    """
    if not raw:
        return None
    raw_u = raw.strip().upper()
    # Remove common prefix noise like "B TECH IN ", "B.TECH IN ", etc.
    import re
    raw_clean = re.sub(
        r'^(B\.?\s*TECH\s+IN\s*|BACHELOR\s+OF\s+(ENGINEERING|TECHNOLOGY)\s+(IN\s*)?)'
        r'|\s*\(.*?\)'
        r'|\s*(KANNADA MEDIUM|EXCLUSIVELY FOR DIFFERENTLY ABLED)',
        '', raw_u
    ).strip()

    # Try full-name map (sorted longest pattern first for greedy match)
    for pattern, code, display in COURSE_FULL_NAME_MAP:
        if pattern in raw_clean or pattern in raw_u:
            return (code, display)

    # Keyword heuristics as final fallback
    if 'COMPUTER' in raw_u and ('SCIENCE' in raw_u or 'ENGG' in raw_u or 'ENGINEERING' in raw_u):
        return ('CSE', 'Computer Science & Engineering')
    if 'INFORMATION' in raw_u and ('SCIENCE' in raw_u or 'ENGG' in raw_u):
        return ('ISE', 'Information Science & Engineering')
    if 'ARTIFICIAL' in raw_u or 'MACHINE LEARNING' in raw_u:
        return ('AIML', 'AI & Machine Learning')
    if 'DATA SCIENCE' in raw_u:
        return ('DS', 'Data Science')
    if 'ELECTRONICS' in raw_u and 'COMMUNICATION' in raw_u:
        return ('ECE', 'Electronics & Communication Engineering')
    if 'ELECTRONICS' in raw_u and 'INSTRUMENTATION' in raw_u:
        return ('EIE', 'Electronics & Instrumentation Engineering')
    if 'ELECTRONICS' in raw_u:
        return ('EE', 'Electronics Engineering')
    if 'ELECTRICAL' in raw_u:
        return ('EEE', 'Electrical & Electronics Engineering')
    if 'MECHANICAL' in raw_u:
        return ('ME', 'Mechanical Engineering')
    if 'CIVIL' in raw_u:
        return ('CE', 'Civil Engineering')
    if 'BIOMEDICAL' in raw_u or 'BIO-MEDICAL' in raw_u:
        return ('BME', 'Biomedical Engineering')
    if 'BIOTECHNOLOGY' in raw_u or 'BIO-TECHNOLOGY' in raw_u:
        return ('BT', 'Biotechnology')
    if 'CHEMICAL' in raw_u:
        return ('CHE', 'Chemical Engineering')
    if 'AERONAUTICAL' in raw_u or 'AEROSPACE' in raw_u:
        return ('AER', 'Aeronautical Engineering')
    if 'ROBOTICS' in raw_u:
        return ('RA', 'Robotics & Automation')
    if 'CYBER' in raw_u:
        return ('CYS', 'Cyber Security')
    if 'VLSI' in raw_u:
        return ('VLSI', 'VLSI Design')
    if 'IOT' in raw_u or 'INTERNET OF THINGS' in raw_u:
        return ('IOT', 'Internet of Things')
    if 'MECHATRONICS' in raw_u:
        return ('MCT', 'Mechatronics Engineering')
    if 'MINING' in raw_u:
        return ('MIN', 'Mining Engineering')
    if 'MARINE' in raw_u:
        return ('MAR', 'Marine Engineering')
    if 'PETROLEUM' in raw_u:
        return ('PEP', 'Petroleum Engineering')
    if 'INDUSTRIAL' in raw_u and 'PRODUCTION' in raw_u:
        return ('IPE', 'Industrial & Production Engineering')
    if 'PRODUCTION' in raw_u:
        return ('PRE', 'Production Engineering')
    return None


def normalize_course_code(raw: str) -> Optional[str]:
    """Legacy wrapper â€” returns just the course code string."""
    result = normalize_course(raw)
    return result[0] if result else None


def extract_college_code(text: str) -> Optional[str]:
    """Extract college code like E001, E002 from text."""
    import re
    m = re.search(r'E\d{2,3}', str(text).strip())
    return m.group(0) if m else None


def parse_rank(value) -> Optional[int]:
    """Parse a rank value, handling various formats."""
    if value is None:
        return None
    try:
        v = str(value).strip().replace(",", "").replace(" ", "")
        if not v or v in ["-", "--", "---", "â€”", "", "N/A", "NA", "null", "None"]:
            return None
        # Handle potential float
        iv = int(float(v))
        return iv if iv > 0 else None
    except (ValueError, TypeError):
        return None


# â”€â”€ Excel Parsing â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def parse_excel_pandas(excel_path: str) -> Tuple[List[Dict], Dict[str, Dict], Dict[str, Dict]]:
    """
    Parse the Excel file using pandas.
    Returns (cutoff_records, colleges_dict, courses_dict).
    """
    import pandas as pd

    # Read all sheets
    xls = pd.ExcelFile(excel_path)
    print(f"  Excel sheets: {xls.sheet_names}")

    records = []
    colleges = {}
    courses = {}
    sheet_count = 0

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        sheet_count += 1
        print(f"  Sheet '{sheet_name}': {df.shape[0]} rows x {df.shape[1]} cols")

        # Normalize column names
        df.columns = [str(c).strip().upper() for c in df.columns]

        # Detect the column layout
        # Typical layouts:
        #   Layout A: CollegeCode | CollegeName | Course | R1 | R2 | R3
        #   Layout B: SI.No | CollegeCode | CollegeName | CourseCode | CourseName | R1 | R2 | R3
        #   Layout C: CollegeCode | CourseCode | Round1 | Round2 | Round3

        code_col = None
        name_col = None
        course_col = None
        r1_col = None
        r2_col = None
        r3_col = None

        for col in df.columns:
            col_clean = col.replace(" ", "").replace("_", "").replace("-", "")
            if col_clean in ["COLLEGECODE", "CODE", "INSTCODE", "INSTITUTECODE"]:
                code_col = col
            elif col_clean in ["COLLEGENAME", "NAME", "INSTITUTENAME", "INSTNAME", "COLLEGE"]:
                name_col = col
            elif col_clean in ["COURSENAME", "COURSECODE", "COURSE", "BRANCH", "BRANCHCODE", "PROGRAM"]:
                course_col = col
            elif col_clean in ["ROUND1RANK", "ROUND1", "R1", "CUTOFF1", "CUTOFFR1", "RANK1"]:
                r1_col = col
            elif col_clean in ["ROUND2RANK", "ROUND2", "R2", "CUTOFF2", "CUTOFFR2", "RANK2"]:
                r2_col = col
            elif col_clean in ["ROUND3RANK", "ROUND3", "R3", "CUTOFF3", "CUTOFFR3", "RANK3"]:
                r3_col = col

        # If columns weren't found by name, try position-based detection
        if not code_col:
            # Check first few columns for E-code pattern
            for col in df.columns[:3]:
                sample = df[col].dropna().astype(str).iloc[0] if len(df) > 0 else ""
                if extract_college_code(sample):
                    code_col = col
                    break

        if not code_col:
            print(f"    âš  Could not detect college code column in sheet '{sheet_name}', skipping...")
            continue

        # Process each row
        row_count = 0
        for idx, row in df.iterrows():
            # Extract college code
            raw_code = str(row.get(code_col, "")).strip()
            college_code = extract_college_code(raw_code)

            if not college_code:
                # Try to find E-code in any cell of this row
                for col in df.columns[:5]:
                    cc = extract_college_code(str(row.get(col, "")))
                    if cc:
                        college_code = cc
                        break

            if not college_code:
                continue

            # Extract college name
            college_name = ""
            if name_col:
                college_name = str(row.get(name_col, "")).strip()
            else:
                # Use the raw code text as name (sometimes it contains both)
                college_name = raw_code.replace(college_code, "").strip()
                if not college_name:
                    college_name = f"College {college_code}"

            # Extract course â€” use full name mapping
            raw_course = ""
            if course_col:
                raw_course = str(row.get(course_col, "")).strip()

            course_result = normalize_course(raw_course) if raw_course else None

            # Try other columns if primary course column failed
            if not course_result:
                for col in df.columns:
                    if col in [code_col, name_col, r1_col, r2_col, r3_col]:
                        continue
                    val = str(row.get(col, "")).strip()
                    if val and val != "nan":
                        cr = normalize_course(val)
                        if cr:
                            course_result = cr
                            break

            course_code = course_result[0] if course_result else None
            course_display = course_result[1] if course_result else raw_course

            # Extract cutoff ranks
            r1 = parse_rank(row.get(r1_col)) if r1_col else None
            r2 = parse_rank(row.get(r2_col)) if r2_col else None
            r3 = parse_rank(row.get(r3_col)) if r3_col else None

            # If specific round columns not found, try to find rank values in remaining columns
            if r1 is None and r2 is None and r3 is None:
                rank_cols = []
                for col in df.columns:
                    if col in [code_col, name_col, course_col]:
                        continue
                    r = parse_rank(row.get(col))
                    if r is not None:
                        rank_cols.append(r)
                # First 3 rank-like values are R1, R2, R3
                if len(rank_cols) >= 1:
                    r1 = rank_cols[0]
                if len(rank_cols) >= 2:
                    r2 = rank_cols[1]
                if len(rank_cols) >= 3:
                    r3 = rank_cols[2]

            # Skip rows with no valid data
            if not course_code or (r1 is None and r2 is None and r3 is None):
                continue

            # Store college info
            if college_code not in colleges:
                colleges[college_code] = {
                    "college_code": college_code,
                    "college_name": college_name or f"College {college_code}",
                    "location": "",
                    "college_type": infer_college_type(college_name or ""),
                }

            # Store course info
            if course_code not in courses:
                courses[course_code] = {
                    "course_code": course_code,
                    "course_name": course_display,
                    "stream_group": "Engineering",
                }

            # Add record
            rec = {
                "college_code": college_code,
                "college_name": college_name or colleges[college_code]["college_name"],
                "course_code": course_code,
                "course_name": courses[course_code]["course_name"],
                "location": colleges[college_code].get("location", ""),
                "college_type": colleges[college_code].get("college_type", "Private-Unaided"),
                "stream_group": "Engineering",
                "category": "GM",
                "round_1_cutoff": r1,
                "round_2_cutoff": r2,
                "round_3_cutoff": r3,
            }
            records.append(rec)
            row_count += 1

        print(f"    Parsed {row_count} records from sheet '{sheet_name}'")

    print(f"\n  Total: {len(records)} records, {len(colleges)} colleges, {len(courses)} courses")
    return records, colleges, courses


def deduplicate_records(records: List[Dict]) -> List[Dict]:
    """Remove duplicate college-course combinations by keeping first occurrence."""
    seen = set()
    unique = []
    for rec in records:
        key = (rec["college_code"], rec["course_code"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(rec)
    return unique


def save_outputs(records: List[Dict], colleges: Dict, courses: Dict, output_dir: str, excel_path: str):
    """Save parsed data to JSON files."""
    os.makedirs(output_dir, exist_ok=True)

    # 1. Full cutoffs JSON
    cutoff_path = os.path.join(output_dir, "kea_cutoffs_2025.json")
    with open(cutoff_path, "w", encoding="utf-8") as f:
        json.dump({
            "source": excel_path,
            "category": "GM",
            "total_records": len(records),
            "total_colleges": len(colleges),
            "total_courses": len(courses),
            "records": records,
        }, f, indent=2, default=str)
    print(f"\n  âœ… Cutoff data -> {cutoff_path}")

    # 2. Colleges JSON
    colleges_path = os.path.join(output_dir, "kea_colleges_2025.json")
    with open(colleges_path, "w", encoding="utf-8") as f:
        json.dump({
            "total": len(colleges),
            "colleges": list(colleges.values()),
        }, f, indent=2)
    print(f"  âœ… Colleges      -> {colleges_path}")

    # 3. Courses JSON
    courses_path = os.path.join(output_dir, "kea_courses_2025.json")
    with open(courses_path, "w", encoding="utf-8") as f:
        json.dump({
            "total": len(courses),
            "courses": list(courses.values()),
        }, f, indent=2)
    print(f"  âœ… Courses       -> {courses_path}")

    # 4. Generate Python import module for the backend
    py_path = os.path.join(output_dir, "kea_import.py")
    generate_python_module(records, colleges, courses, py_path)
    print(f"  âœ… Python module -> {py_path}")

    # Print summary
    print(f"\n  {'='*50}")
    print(f"  PARSING SUMMARY")
    print(f"  {'='*50}")
    print(f"  Total records:        {len(records)}")
    print(f"  Unique colleges:      {len(colleges)}")
    print(f"  Unique courses:       {len(courses)}")
    print(f"  Category:             GM (General Merit)")

    # Count records with data per round
    with_r1 = sum(1 for r in records if r["round_1_cutoff"] is not None)
    with_r2 = sum(1 for r in records if r["round_2_cutoff"] is not None)
    with_r3 = sum(1 for r in records if r["round_3_cutoff"] is not None)
    print(f"  Records with R1 data: {with_r1}")
    print(f"  Records with R2 data: {with_r2}")
    print(f"  Records with R3 data: {with_r3}")

    # Top colleges by number of courses
    print(f"\n  Colleges with most courses:")
    college_course_count = defaultdict(int)
    for r in records:
        college_course_count[r["college_code"]] += 1
    top_colleges = sorted(college_course_count.items(), key=lambda x: -x[1])[:10]
    for code, count in top_colleges:
        name = colleges[code]["college_name"]
        print(f"    {code}: {name} ({count} courses)")

    print(f"  {'='*50}\n")


def generate_python_module(records: List[Dict], colleges: Dict, courses: Dict, output_path: str):
    """Generate a Python module with the parsed data for direct import by the backend."""
    # Sort records by college code then course code
    sorted_records = sorted(records, key=lambda r: (r["college_code"], r["course_code"]))

    lines = []
    lines.append('"""')
    lines.append('Auto-generated KEA 2025 GM Cutoff Data')
    lines.append('Generated by parse_kea_excel.py')
    lines.append('"""')
    lines.append("")
    lines.append("from typing import Dict, List, Optional")
    lines.append("")

    # Colleges
    lines.append("# â”€â”€ College Master Data â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")
    lines.append("COLLEGES: Dict[str, Dict] = {")
    for code in sorted(colleges.keys()):
        c = colleges[code]
        lines.append(f'    "{code}": {{')
        lines.append(f'        "college_code": "{code}",')
        lines.append(f'        "college_name": {json.dumps(c["college_name"])},')
        lines.append(f'        "location": {json.dumps(c["location"])},')
        lines.append(f'        "college_type": {json.dumps(c["college_type"])},')
        lines.append("    },")
    lines.append("}")
    lines.append("")

    # Courses
    lines.append("# â”€â”€ Course Master Data â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")
    lines.append("COURSES: Dict[str, Dict] = {")
    for code in sorted(courses.keys()):
        c = courses[code]
        lines.append(f'    "{code}": {{')
        lines.append(f'        "course_code": "{code}",')
        lines.append(f'        "course_name": {json.dumps(c["course_name"])},')
        lines.append(f'        "stream_group": {json.dumps(c["stream_group"])},')
        lines.append("    },")
    lines.append("}")
    lines.append("")

    # Cutoff records
    lines.append("# â”€â”€ Cutoff Records (College Ã— Course, 3 Rounds) â”€â”€â”€")
    lines.append("CUTOFF_RECORDS: List[Dict] = [")
    for rec in sorted_records:
        lines.append("    {")
        lines.append(f'        "college_code": "{rec["college_code"]}",')
        lines.append(f'        "college_name": {json.dumps(rec["college_name"])},')
        lines.append(f'        "course_code": "{rec["course_code"]}",')
        lines.append(f'        "course_name": {json.dumps(rec["course_name"])},')
        lines.append(f'        "category": "GM",')
        lines.append(f'        "round_1_cutoff": {rec["round_1_cutoff"]},')
        lines.append(f'        "round_2_cutoff": {rec["round_2_cutoff"]},')
        lines.append(f'        "round_3_cutoff": {rec["round_3_cutoff"]},')
        lines.append("    },")
    lines.append("]")
    lines.append("")

    # Helper function
    lines.append("""
def get_cutoffs_by_category(category: str = "GM") -> List[Dict]:
    \"\"\"Get cutoff records filtered by category.\"\"\"
    if category == "GM":
        return CUTOFF_RECORDS
    # For other categories, return empty (data not available from this Excel)
    return []

def get_colleges_list() -> List[Dict]:
    \"\"\"Get list of all colleges.\"\"\"
    return list(COLLEGES.values())

def get_courses_list() -> List[Dict]:
    \"\"\"Get list of all courses.\"\"\"
    return list(COURSES.values())

def get_locations() -> List[str]:
    \"\"\"Get unique locations.\"\"\"
    return sorted(set(c["location"] for c in COLLEGES.values() if c["location"]))
""")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Parse KEA 2025 GM Cutoff Excel")
    parser.add_argument("--excel", default=DEFAULT_EXCEL_PATH, help="Path to Excel file")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="Output directory")
    args = parser.parse_args()

    excel_path = args.excel
    if not os.path.exists(excel_path):
        print(f"âŒ Excel file not found: {excel_path}")
        sys.exit(1)

    print(f"\n  {'='*60}")
    print(f"  KEA 2025 GM CUTOFF EXCEL PARSER")
    print(f"  {'='*60}")
    print(f"  File: {excel_path}")
    print(f"  Size: {os.path.getsize(excel_path) / 1024:.1f} KB")

    # Install dependencies if needed
    try:
        import pandas
        import openpyxl
    except ImportError:
        print("  Installing required packages (pandas, openpyxl)...")
        import subprocess
        for pkg in ["pandas", "openpyxl"]:
            r = subprocess.run([sys.executable, "-m", "pip", "install", pkg, "-q"],
                               capture_output=True, text=True)
            if r.returncode == 0:
                print(f"    Installed {pkg}")
            else:
                print(f"    Failed to install {pkg}: {r.stderr[:100]}")
                sys.exit(1)

    # Parse
    records, colleges, courses = parse_excel_pandas(excel_path)
    records = deduplicate_records(records)

    if not records:
        print("\n  âŒ No records could be extracted.")
        print("     The Excel format may differ from expected. Check the file structure.")
        sys.exit(1)

    # Save
    save_outputs(records, colleges, courses, args.output_dir, excel_path)

    # Instructions
    print("\n  Next steps:")
    print("  1. Run:  python parse_kea_excel.py")
    print("  2. Then update the backend to use the real data.")
    print("     See parsed_data/kea_import.py for the data module.")
    print()

    return records, colleges, courses


if __name__ == "__main__":
    records, colleges, courses = main()

