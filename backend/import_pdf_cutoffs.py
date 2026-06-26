"""
Script to import CET-2025 cutoff data from PDF into the database.
This handles the structured PDF format from K.E.A.

Data extraction and import with validation.
"""

import pandas as pd
import re
from typing import List, Tuple, Dict, Optional
import sys
sys.path.insert(0, '.')

from database import SessionLocal, College, Course, Cutoff2025, engine, Base
from sqlalchemy.exc import IntegrityError

# PDF was processed and converted to structured data
# Format: colleges -> courses -> categories -> rounds -> cutoff ranks

COLLEGES_DATA = {
    "E064": {
        "name": "Adhichunchanagiri Institute of Technology",
        "location": "Chikmagalur",
        "type": "PUA",
        "university": "VTU"
    },
    "E065": {
        "name": "Jawaharlal Nehru New College of Engineering",
        "location": "Shimoga",
        "type": "PUA",
        "university": "VTU"
    },
    "E066": {
        "name": "University B.D.T. College of Engineering",
        "location": "Davanagere",
        "type": "GOVT",
        "university": "VTU"
    },
    "E070": {
        "name": "Bahubali College of Engineering",
        "location": "Hassan",
        "type": "MR (JAIN)",
        "university": "VTU"
    },
    "E071": {
        "name": "Vidya Vardhaka College of Engineering",
        "location": "Mysore",
        "type": "PUA",
        "university": "Autonomous"
    },
    "E075": {
        "name": "Ballari Institute of Technology & Management",
        "location": "Ballari",
        "type": "PUA",
        "university": "Autonomous"
    },
    "E076": {
        "name": "Proudadevaraya Institute of Technology",
        "location": "Ballari",
        "type": "PUA",
        "university": "VTU"
    },
    "E077": {
        "name": "Vidya Vikas Institute of Engineering & Tech",
        "location": "Mysore",
        "type": "PUA",
        "university": "VTU"
    },
    "E078": {
        "name": "The Oxford College of Engineering",
        "location": "Bangalore",
        "type": "ML (TELUGU)",
        "university": "VTU"
    },
    "E079": {
        "name": "Acharya Institute of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "VTU"
    },
    "E081": {
        "name": "Sri Siddartha School of Engineering",
        "location": "Tumkur",
        "type": "PUA",
        "university": "VTU"
    },
    "E082": {
        "name": "JSS Academy of Technical Education",
        "location": "Bangalore",
        "type": "PUA",
        "university": "VTU"
    },
    "E083": {
        "name": "H.K.B.K. College of Engineering",
        "location": "Bangalore",
        "type": "MR (MUSLIM)",
        "university": "VTU"
    },
    "E085": {
        "name": "APS College of Engineering",
        "location": "Bangalore",
        "type": "PUA",
        "university": "VTU"
    },
    "E086": {
        "name": "Sri Sairam College of Engineering",
        "location": "Bangalore",
        "type": "PUA",
        "university": "VTU"
    },
    "E087": {
        "name": "Vivekananda Institute of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "VTU"
    },
    "E090": {
        "name": "Sri Revana Siddeswara Institute of Tech",
        "location": "Bangalore",
        "type": "PUA",
        "university": "VTU"
    },
    "E091": {
        "name": "K S Institute of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "Autonomous"
    },
    "E092": {
        "name": "Vemana Institute of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "VTU"
    },
    "E093": {
        "name": "Basavakalyana Engineering College",
        "location": "Bidar",
        "type": "PUA",
        "university": "VTU"
    },
    "E094": {
        "name": "Coorg Institute of Technology",
        "location": "Kodagu",
        "type": "PUA",
        "university": "VTU"
    },
    "E095": {
        "name": "AMC Engineering College",
        "location": "Bangalore",
        "type": "PUA",
        "university": "Autonomous"
    },
    "E096": {
        "name": "East Point College of Engineering & Tech",
        "location": "Bangalore",
        "type": "PUA",
        "university": "Autonomous"
    },
    "E097": {
        "name": "C M R Institute of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "VTU"
    },
    "E098": {
        "name": "Atria Institute of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "Autonomous"
    },
    "E099": {
        "name": "New Horizon College of Engineering",
        "location": "Bangalore",
        "type": "ML (SINDHI)",
        "university": "Autonomous"
    },
    "E100": {
        "name": "K N S Institute of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "VTU"
    },
    "E101": {
        "name": "Channabasaveshwara Institute of Technology",
        "location": "Tumkur",
        "type": "PUA",
        "university": "VTU"
    },
    "E102": {
        "name": "Donbosco Institute of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "Autonomous"
    },
    "E103": {
        "name": "Global Academy of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "Autonomous"
    },
    "E104": {
        "name": "Nagarjuna College of Engineering & Tech",
        "location": "Bangalore",
        "type": "PUA",
        "university": "Autonomous"
    },
    "E106": {
        "name": "East West Institute of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "Autonomous"
    },
    "E107": {
        "name": "B N M Institute of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "Autonomous"
    },
    "E108": {
        "name": "Sapthagiri NPS University",
        "location": "Bangalore",
        "type": "P UNI",
        "university": "Bangalore"
    },
    "E109": {
        "name": "City Engineering College",
        "location": "Bangalore",
        "type": "PUA",
        "university": "VTU"
    },
    "E111": {
        "name": "Sri Venkateshwara College of Engineering",
        "location": "Bangalore",
        "type": "PUA",
        "university": "Autonomous"
    },
    "E112": {
        "name": "Sri Krishna Institute of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "VTU"
    },
    "E113": {
        "name": "Sambhram Institute of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "VTU"
    },
    "E114": {
        "name": "G M Institute of Technology",
        "location": "Davanagere",
        "type": "PUA",
        "university": "VTU"
    },
    "E115": {
        "name": "S J B Institute of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "Autonomous"
    },
    "E116": {
        "name": "R.L. Jalappa Institute of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "VTU"
    },
    "E118": {
        "name": "RNS Institute of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "Autonomous"
    },
    "E119": {
        "name": "K C T Engineering College",
        "location": "Gulbarga",
        "type": "MR (MUSLIM)",
        "university": "VTU"
    },
    "E120": {
        "name": "Jnanavikasa Institute of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "VTU"
    },
    "E121": {
        "name": "Vivekananda College of Engineering Technology",
        "location": "Dakshina Kannada",
        "type": "PUA",
        "university": "VTU"
    },
    "E123": {
        "name": "Canara Engineering College",
        "location": "Dakshina Kannada",
        "type": "ML (KONKANI)",
        "university": "VTU"
    },
    "E124": {
        "name": "Rajiv Gandhi Institute of Technology",
        "location": "Bangalore",
        "type": "PUA",
        "university": "VTU"
    },
    "E126": {
        "name": "B M S Institute of Technology & Management",
        "location": "Bangalore",
        "type": "PUA",
        "university": "Autonomous"
    },
    "E127": {
        "name": "M S Engineering College",
        "location": "Bangalore",
        "type": "PUA",
        "university": "VTU"
    },
    "E128": {
        "name": "Sharnbasva University",
        "location": "Gulbarga",
        "type": "P UNI",
        "university": "Gulbarga"
    },
    "E129": {
        "name": "St. Joseph Engineering College",
        "location": "Dakshina Kannada",
        "type": "MR (CHRISTIAN)",
        "university": "Autonomous"
    },
    "E130": {
        "name": "Shridevi Institute of Engineering and Technology",
        "location": "Tumkur",
        "type": "PUA",
        "university": "VTU"
    },
    "E132": {
        "name": "Secab Institute of Engineering & Technology",
        "location": "Bijapur",
        "type": "PUA",
        "university": "VTU"
    },
    "E133": {
        "name": "G S S S Institute of Engineering and Technology for Women",
        "location": "Mysore",
        "type": "PUA",
        "university": "VTU"
    },
    "E134": {
        "name": "Smt. Kamala & Sri Venkappa M. Agadi College of Engineering & Tech",
        "location": "Gadag",
        "type": "PUA",
        "university": "VTU"
    },
    "E135": {
        "name": "K L S Viswanathrao Deshpande Institute of Technology",
        "location": "Uttara Kannada",
        "type": "PUA",
        "university": "VTU"
    },
    "E136": {
        "name": "Moodalakatte Institute of Technology",
        "location": "Udupi",
        "type": "PUA",
        "university": "VTU"
    }
}

# Course code mapping for consistency
COURSE_CODES = {
    "ARTIFICIAL INTELLIGENCE AND DATA SCIENCE": "AD",
    "ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING": "AI",
    "AERONAUTICAL ENGINEERING": "AE",
    "BIO-TECHNOLOGY": "BT",
    "BIO-MEDICAL ENGINEERING": "BM",
    "CIVIL ENGINEERING": "CE",
    "COMPUTER SCIENCE AND ENGINEERING": "CS",
    "COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)": "DS",
    "COMPUTER SCIENCE AND ENGINEERING(DATA SCIENCE)": "DS",
    "COMPUTER SCIENCE AND DESIGN": "CD",
    "COMPUTER SCIENCE ANDENGG(ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING)": "CA",
    "COMPUTER SCIENCE AND ENGG(ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING)": "CA",
    "CYBER SECURITY": "ZU",
    "COMPUTER SCIENCE AND ENGINEERING (CYBER SECURITY)": "CY",
    "COMPUTER SCIENCE AND ENGINEERING (CYBER SECURITY )": "CY",
    "ELECTRICAL & ELECTRONICS ENGINEERING": "EE",
    "ELECTRICAL AND ELECTRONICS ENGINEERING": "EE",
    "ELECTRONICS AND COMMUNICATION ENGG": "EC",
    "ELECTRONICS AND TELECOMMUNICATION ENGINEERING": "ET",
    "ELECTRONICS AND INSTRUMENTATION ENGG": "EI",
    "ELECTRONICS ENGINEERING(VLSI DESIGN & TECHNOLOGY)": "EV",
    "ENERGY ENGINEERING": "EN",
    "INFORMATION SCIENCE AND ENGINEERING": "IE",
    "INFORMATION SCIENCE ANDENGINEERING": "IE",
    "INTERNET OF THINGS & CYBER SECURITY INCLUDING BLOCK CHAIN TECH": "IC",
    "MECHANICAL ENGINEERING": "ME",
    "MECHATRONICS": "MT",
    "ROBOTICS AND ARTIFICIAL INTELLIGENCE": "RI",
    "ROBOTICS AND AUTOMATION": "RA",
    "DATA SCIENCES": "DC",
    "QUANTUM COMPUTING": "QC",
    "AEROSPACE ENGINEERING": "SE",
    "AERONAUTICAL ENGINEERING": "AE"
}

def normalize_course_name(course_name: str) -> str:
    """Normalize course name for matching"""
    return str(course_name).strip().upper()

def get_course_code(course_name: str) -> str:
    """Get standardized course code from course name"""
    normalized = normalize_course_name(course_name)
    
    # Try exact match first
    for key, code in COURSE_CODES.items():
        if normalize_course_name(key) == normalized:
            return code
    
    # Try partial match for common variations
    for key, code in COURSE_CODES.items():
        if normalize_course_name(key) in normalized or normalized in normalize_course_name(key):
            return code
    
    # Fallback: use abbreviated form
    words = normalized.split()
    abbrev = "".join([w[0] for w in words if w])[:3].upper()
    return abbrev if abbrev else "XX"

def import_cutoff_data_from_pdf(cutoff_data: List[Dict]) -> Tuple[int, int, int, List[str]]:
    """
    Import cutoff data extracted from PDF.
    
    Args:
        cutoff_data: List of dictionaries with keys:
                    - college_code, course_code (if provided), college_name, course_name
                    - category_1G, category_2AG, etc. (with Round I/II values)
    
    Returns:
        (colleges_added, courses_added, cutoffs_added, errors)
    """
    
    db = SessionLocal()
    colleges_added = 0
    courses_added = 0
    cutoffs_added = 0
    errors = []
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created/verified.")
        
        # Process each record
        for idx, record in enumerate(cutoff_data):
            try:
                college_code = record.get("college_code")
                college_name = record.get("college_name")
                course_name = record.get("course_name", "Unknown").upper()
                
                if not college_code or not college_name:
                    errors.append(f"Record {idx}: Missing college code or name")
                    continue
                
                # Get course code
                course_code = record.get("course_code") or get_course_code(course_name)
                
                # Add college
                existing_college = db.query(College).filter_by(college_code=college_code).first()
                if not existing_college:
                    college_info = COLLEGES_DATA.get(college_code, {})
                    college = College(
                        college_code=college_code,
                        college_name=college_info.get("name", college_name),
                        location=college_info.get("location", "Unknown"),
                        college_type=college_info.get("type", "PUA"),
                        status=True
                    )
                    db.add(college)
                    db.flush()
                    colleges_added += 1
                
                # Add course
                existing_course = db.query(Course).filter_by(course_code=course_code).first()
                if not existing_course:
                    course = Course(
                        course_code=course_code,
                        course_name=course_name,
                        stream_group="Engineering"
                    )
                    db.add(course)
                    db.flush()
                    courses_added += 1
                
                # Extract and add cutoff data for all categories
                categories = ["1G", "2AG", "2BG", "3AG", "3BG", "GM", "SCG", "STG"]
                
                for category in categories:
                    round_1_key = f"category_{category}_round_i"
                    round_2_key = f"category_{category}_round_ii"
                    
                    for round_no, data_key in [(1, round_1_key), (2, round_2_key)]:
                        cutoff_rank = record.get(data_key)
                        
                        # Skip if no data or invalid
                        if cutoff_rank is None or cutoff_rank == "" or cutoff_rank == "-":
                            continue
                        
                        try:
                            cutoff_rank = int(cutoff_rank)
                            if cutoff_rank <= 0:
                                continue
                        except (ValueError, TypeError):
                            continue
                        
                        # Check if exists
                        existing = db.query(Cutoff2025).filter_by(
                            college_code=college_code,
                            course_code=course_code,
                            category=category,
                            round_no=round_no
                        ).first()
                        
                        if not existing:
                            cutoff = Cutoff2025(
                                college_code=college_code,
                                course_code=course_code,
                                category=category,
                                round_no=round_no,
                                cutoff_rank=cutoff_rank
                            )
                            db.add(cutoff)
                            cutoffs_added += 1
                
            except Exception as e:
                errors.append(f"Record {idx}: {str(e)}")
                continue
        
        # Commit all changes
        db.commit()
        
    except Exception as e:
        db.rollback()
        errors.append(f"Database error: {str(e)}")
    finally:
        db.close()
    
    return colleges_added, courses_added, cutoffs_added, errors


def manual_data_entry_example():
    """
    Example function showing how to manually add cutoff data.
    This can be extended to parse PDF data programmatically.
    """
    
    # Sample data structure from PDF
    sample_cutoff_data = [
        {
            "college_code": "E064",
            "college_name": "Adhichunchanagiri Institute of Technology",
            "course_name": "ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",
            "category_1G_round_i": 58912,
            "category_1G_round_ii": 63801,
            "category_2AG_round_i": 59451,
            "category_2AG_round_ii": 63379,
            "category_2BG_round_i": 48651,
            "category_2BG_round_ii": 63539,
            "category_3AG_round_i": 42481,
            "category_3AG_round_ii": 44416,
            "category_3BG_round_i": 54001,
            "category_3BG_round_ii": 64718,
            "category_GM_round_i": 42330,
            "category_GM_round_ii": 44050,
            "category_SCG_round_i": 88835,
            "category_SCG_round_ii": 88835,
            "category_STG_round_i": 77519,
            "category_STG_round_ii": 77519,
        }
    ]
    
    return sample_cutoff_data


if __name__ == "__main__":
    print("CET-2025 PDF Cutoff Data Import Tool\n")
    print("=" * 50)
    
    # Get sample data
    sample_data = manual_data_entry_example()
    
    # Import
    colleges, courses, cutoffs, errors = import_cutoff_data_from_pdf(sample_data)
    
    print(f"\n✓ Import completed!")
    print(f"  - Colleges added: {colleges}")
    print(f"  - Courses added: {courses}")
    print(f"  - Cutoff records added: {cutoffs}")
    
    if errors:
        print(f"\n⚠ Errors encountered: {len(errors)}")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
