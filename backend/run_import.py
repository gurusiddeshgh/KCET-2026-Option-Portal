"""
Master import script for CET-2025 cutoff data.

This script combines PDF data extraction, validation, and database import
into a single comprehensive workflow.
"""

import json
import sys
sys.path.insert(0, '.')

from database import SessionLocal, College, Course, Cutoff2025, engine, Base
from extract_pdf_data import flatten_cutoff_data
import pandas as pd
from typing import List, Dict, Tuple

def validate_record(record: Dict) -> Tuple[bool, str]:
    """Validate a single cutoff record"""
    required_fields = ["college_code", "course_code", "category", "round", "cutoff_rank"]
    
    for field in required_fields:
        if field not in record or record[field] is None:
            return False, f"Missing field: {field}"
    
    if record["cutoff_rank"] <= 0:
        return False, "Cutoff rank must be positive"
    
    if record["round"] not in [1, 2, 3]:
        return False, f"Invalid round: {record['round']}"
    
    valid_categories = ["1G", "2AG", "2BG", "3AG", "3BG", "GM", "SCG", "STG"]
    if record["category"] not in valid_categories:
        return False, f"Invalid category: {record['category']}"
    
    return True, ""

def import_cutoff_data(data: List[Dict], batch_size: int = 100) -> Dict:
    """
    Import cutoff data into database with validation and error handling.
    
    Args:
        data: List of cutoff records
        batch_size: Number of records to process before committing
    
    Returns:
        Dictionary with import statistics
    """
    
    db = SessionLocal()
    stats = {
        "total_records": len(data),
        "colleges_added": 0,
        "courses_added": 0,
        "cutoffs_added": 0,
        "validation_errors": 0,
        "database_errors": 0,
        "errors": []
    }
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created/verified")
        
        # Clear existing data (optional - uncomment to refresh)
        # print("\nClearing existing cutoff data...")
        # db.query(Cutoff2025).delete()
        # db.commit()
        # print("✓ Previous data cleared")
        
        added_colleges = set()
        added_courses = set()
        
        print(f"\nImporting {len(data)} records...")
        print("-" * 60)
        
        for idx, record in enumerate(data):
            try:
                # Validate record
                is_valid, error_msg = validate_record(record)
                if not is_valid:
                    stats["validation_errors"] += 1
                    stats["errors"].append(f"Record {idx}: {error_msg}")
                    continue
                
                college_code = record["college_code"]
                course_code = record["course_code"]
                category = record["category"]
                round_no = record["round"]
                cutoff_rank = int(record["cutoff_rank"])
                
                # Check if cutoff already exists
                existing = db.query(Cutoff2025).filter_by(
                    college_code=college_code,
                    course_code=course_code,
                    category=category,
                    round_no=round_no
                ).first()
                
                if existing:
                    # Update existing record
                    existing.cutoff_rank = cutoff_rank
                    continue  # Don't increment counter for updates
                
                # Add college if new
                if college_code not in added_colleges:
                    existing_college = db.query(College).filter_by(college_code=college_code).first()
                    
                    if not existing_college:
                        college = College(
                            college_code=college_code,
                            college_name=record.get("college_name", "Unknown"),
                            location=record.get("location", "Unknown"),
                            college_type="PUA",
                            status=True
                        )
                        db.add(college)
                        db.flush()
                        stats["colleges_added"] += 1
                    
                    added_colleges.add(college_code)
                
                # Add course if new
                if course_code not in added_courses:
                    existing_course = db.query(Course).filter_by(course_code=course_code).first()
                    
                    if not existing_course:
                        course = Course(
                            course_code=course_code,
                            course_name=record.get("course_name", "Unknown"),
                            stream_group="Engineering"
                        )
                        db.add(course)
                        db.flush()
                        stats["courses_added"] += 1
                    
                    added_courses.add(course_code)
                
                # Add cutoff
                cutoff = Cutoff2025(
                    college_code=college_code,
                    course_code=course_code,
                    category=category,
                    round_no=round_no,
                    cutoff_rank=cutoff_rank
                )
                db.add(cutoff)
                stats["cutoffs_added"] += 1
                
                # Commit in batches
                if (idx + 1) % batch_size == 0:
                    db.commit()
                    print(f"  ✓ Processed {idx + 1} records...")
                
            except Exception as e:
                stats["database_errors"] += 1
                stats["errors"].append(f"Record {idx}: {str(e)}")
                continue
        
        # Final commit
        db.commit()
        print(f"  ✓ Processed all {len(data)} records")
        
    except Exception as e:
        db.rollback()
        stats["database_errors"] += 1
        stats["errors"].append(f"Global error: {str(e)}")
    finally:
        db.close()
    
    return stats

def print_import_summary(stats: Dict):
    """Print formatted import summary"""
    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"Total Records Processed:     {stats['total_records']}")
    print(f"Colleges Added:               {stats['colleges_added']}")
    print(f"Courses Added:                {stats['courses_added']}")
    print(f"Cutoff Records Added:         {stats['cutoffs_added']}")
    print(f"Validation Errors:            {stats['validation_errors']}")
    print(f"Database Errors:              {stats['database_errors']}")
    print("=" * 60)
    
    if stats["errors"]:
        print(f"\n⚠ ERRORS ({len(stats['errors'])} total):")
        for error in stats["errors"][:20]:
            print(f"  • {error}")
        if len(stats["errors"]) > 20:
            print(f"  ... and {len(stats['errors']) - 20} more errors")
    else:
        print("\n✓ NO ERRORS - Import completed successfully!")
    
    print("=" * 60)

def get_database_summary(db: SessionLocal = None) -> Dict:
    """Get summary statistics from database"""
    if db is None:
        db = SessionLocal()
    
    try:
        total_colleges = db.query(College).count()
        total_courses = db.query(Course).count()
        total_cutoffs = db.query(Cutoff2025).count()
        
        # Get sample of categories
        cutoff_records = db.query(Cutoff2025).limit(10).all()
        categories = set(c.category for c in cutoff_records)
        
        return {
            "colleges": total_colleges,
            "courses": total_courses,
            "cutoffs": total_cutoffs,
            "categories": list(categories)
        }
    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CET-2025 CUTOFF DATA IMPORT TOOL")
    print("=" * 60)
    
    # Extract data from PDF structures
    print("\n1. Extracting cutoff data from PDF...")
    data = flatten_cutoff_data()
    print(f"   ✓ Extracted {len(data)} records")
    
    # Display sample
    print(f"\n2. Sample record:")
    print(f"   {json.dumps(data[0], indent=3) if data else 'No data'}")
    
    # Import to database
    print("\n3. Importing to database...")
    stats = import_cutoff_data(data)
    
    # Display summary
    print_import_summary(stats)
    
    # Get database summary
    print("\n4. Database Summary:")
    db_summary = get_database_summary()
    print(f"   Total Colleges:  {db_summary['colleges']}")
    print(f"   Total Courses:   {db_summary['courses']}")
    print(f"   Total Cutoffs:   {db_summary['cutoffs']}")
    print(f"   Categories:      {', '.join(db_summary['categories'])}")
    
    print("\n✓ Import process complete!")
    print("=" * 60)
