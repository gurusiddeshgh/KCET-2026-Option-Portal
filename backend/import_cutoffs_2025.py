"""
Script to import 2025 cutoff data from Excel sheet into the database.
This data will be used as the basis for 2026 predictions.
"""

import pandas as pd
import re
import hashlib
import sys
sys.path.insert(0, '.')

from database import SessionLocal, College, Course, Cutoff2025, engine
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

def parse_college_code_and_name(college_full_name: str):
    """
    Extract college code from format: (E001)University of Visvesvaraya College of Eng...
    Returns: (college_code, college_name_cleaned)
    """
    match = re.match(r'\((\w+)\)(.*)', str(college_full_name).strip())
    if match:
        return match.group(1), match.group(2).strip()
    # Handle format without parentheses
    match = re.match(r'(\w\d+)\s+(.*)', str(college_full_name).strip())
    if match:
        return match.group(1), match.group(2).strip()
    return None, str(college_full_name).strip()

def generate_course_code(course_name: str):
    """
    Generate a unique course code using hash to avoid collisions
    This ensures different courses don't map to the same code
    """
    course_name = str(course_name).strip().upper()
    # Create a stable hash from the course name
    hash_obj = hashlib.md5(course_name.encode())
    hash_hex = hash_obj.hexdigest()[:8]
    # Use first part of name + hash for readability and uniqueness
    course_prefix = course_name[:5].replace(' ', '_')
    return f"{course_prefix}_{hash_hex}"

def get_location_from_college_name(college_name: str):
    """Infer location from college name"""
    name_lower = college_name.lower()
    
    location_keywords = {
        'bangalore': ['bangalore', 'bengaluru', 'uvce', 'rvce', 'bms', 'dayananda'],
        'belagavi': ['belagavi', 'belgaum', 'rao bahadur'],
        'hubballi': ['hubballi', 'hubli', 'basaveshwar'],
        'mangalore': ['mangalore', 'mangaluru', 'nitte', 'miit'],
        'mysore': ['mysore', 'mysuru', 'vidyavardhaka'],
        'shimoga': ['shimoga', 'shivamogga', 'kle', 'nitte'],
        'raichur': ['raichur'],
        'bagalkot': ['bagalkot', 'basaveshwar'],
        'kolar': ['kolar'],
        'uttara kannada': ['uttara kannada'],
        'tumkur': ['tumkur', 'tumkuru'],
        'vikarabad': ['vikarabad'],
        'davanagere': ['davanagere'],
    }
    
    for location, keywords in location_keywords.items():
        if any(kw in name_lower for kw in keywords):
            return location.capitalize()
    
    return 'Unknown'

def import_excel_to_db(excel_path: str, category: str = "GM"):
    """
    Import cutoff data from Excel file to database.
    
    Args:
        excel_path: Path to the Excel file
        category: Category (default: "GM" for General Merit)
    """
    
    print(f"Reading Excel file: {excel_path}")
    df = pd.read_excel(excel_path, sheet_name='Master_Merged_Ranks')
    
    print(f"Total rows in Excel: {len(df)}")
    print(f"Columns: {df.columns.tolist()}\n")
    
    # Remove duplicate college-course combinations, keeping the first occurrence
    print("Removing duplicate college-course combinations...")
    df = df.drop_duplicates(subset=['College Name', 'Course Name'], keep='first')
    print(f"After deduplication: {len(df)} rows\n")
    
    db = SessionLocal()
    colleges_added = set()
    courses_added = set()
    cutoffs_added = 0
    errors = []
    
    try:
        # Initialize database tables
        from database import Base
        Base.metadata.create_all(bind=engine)
        print("Database tables created/verified.\n")
        
        # Clear existing cutoffs for this category to avoid duplicates
        print(f"Clearing existing {category} cutoffs...")
        deleted = db.query(Cutoff2025).filter_by(category=category).delete()
        db.commit()
        print(f"Deleted {deleted} existing records.\n")
        
        # Process each row
        for idx, row in df.iterrows():
            try:
                # Parse college code and name
                college_code, college_name = parse_college_code_and_name(row['College Name'])
                course_name = str(row.get('Course Name', 'Unknown')).strip()
                
                if not college_code:
                    errors.append(f"Row {idx}: Could not parse college code from {row['College Name']}")
                    continue
                
                # Generate unique course code using hash
                course_code = generate_course_code(course_name)
                
                # Get location
                location = get_location_from_college_name(college_name)
                
                # Add college if new
                if college_code not in colleges_added:
                    existing = db.query(College).filter_by(college_code=college_code).first()
                    if not existing:
                        college = College(
                            college_code=college_code,
                            college_name=college_name,
                            location=location,
                            college_type="Private-Unaided",  # Default - can be updated later
                            status=True
                        )
                        db.add(college)
                        db.flush()  # Flush to ensure college is created
                    colleges_added.add(college_code)
                
                # Add course if new
                if course_code not in courses_added:
                    existing = db.query(Course).filter_by(course_code=course_code).first()
                    if not existing:
                        course = Course(
                            course_code=course_code,
                            course_name=course_name,
                            stream_group="Engineering"
                        )
                        db.add(course)
                        db.flush()  # Flush to ensure course is created
                    courses_added.add(course_code)
                
                # Parse cutoff ranks
                round_1_rank = row.get('Round 1 Rank')
                round_2_rank = row.get('Round 2 Rank')
                round_3_rank = row.get('Round 3 Rank')
                
                # Convert to integer, handling '--' and NaN values
                def parse_rank(value):
                    if pd.isna(value) or value == '--' or value == '':
                        return None
                    try:
                        return int(float(str(value)))
                    except:
                        return None
                
                r1 = parse_rank(round_1_rank)
                r2 = parse_rank(round_2_rank)
                r3 = parse_rank(round_3_rank)
                
                # Add cutoff entries for each round with valid data
                for round_no, cutoff_rank in [(1, r1), (2, r2), (3, r3)]:
                    if cutoff_rank and cutoff_rank > 0:
                        # Check if already exists
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
                errors.append(f"Row {idx}: {str(e)}")
                continue
        
        # Commit all changes
        db.commit()
        
        print(f"\n✓ Import completed successfully!")
        print(f"  - Colleges added: {len(colleges_added)}")
        print(f"  - Courses added: {len(courses_added)}")
        print(f"  - Cutoff records added: {cutoffs_added}")
        
        if errors:
            print(f"\n⚠ {len(errors)} errors encountered:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors")
        
        # Verify data
        college_count = db.query(func.count(College.college_code)).scalar()
        course_count = db.query(func.count(Course.course_code)).scalar()
        cutoff_count = db.query(func.count(Cutoff2025.id)).scalar()
        
        print(f"\nDatabase verification:")
        print(f"  - Total colleges in DB: {college_count}")
        print(f"  - Total courses in DB: {course_count}")
        print(f"  - Total cutoff records in DB: {cutoff_count}")
        
    except Exception as e:
        print(f"Error during import: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import os
    excel_file = "KEA_2025_Master_GM_CutOffs_Round123.xlsx"
    
    if os.path.exists(excel_file):
        import_excel_to_db(excel_file, category="GM")
    else:
        print(f"Error: File not found: {excel_file}")
