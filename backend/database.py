import os
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, UniqueConstraint
from typing import Optional, List

# Try to load real KEA 2025 data; falls back to mock data if unavailable
# Uses same try/except pattern as algorithms.py for import compatibility
try:
    from data_loader import (
        get_cutoffs_by_category as get_real_cutoffs,
        get_real_colleges,
        get_real_courses,
        has_real_data,
        get_data_source
    )
    _HAS_REAL_DATA = has_real_data()
except ImportError:
    try:
        from .data_loader import (
            get_cutoffs_by_category as get_real_cutoffs,
            get_real_colleges,
            get_real_courses,
            has_real_data,
            get_data_source
        )
        _HAS_REAL_DATA = has_real_data()
    except ImportError:
        _HAS_REAL_DATA = False

        def get_real_cutoffs(category): return None
        def get_real_colleges(): return None
        def get_real_courses(): return None
        def get_data_source(): return "Fallback mock data"

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kcet_2026.db")

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class College(Base):
    __tablename__ = "colleges"
    
    college_code = Column(String(10), primary_key=True)
    college_name = Column(String(255), nullable=False)
    location = Column(String(100), nullable=False)
    college_type = Column(String(50), nullable=False)
    status = Column(Boolean, default=True)


class Course(Base):
    __tablename__ = "courses"
    
    course_code = Column(String(10), primary_key=True)
    course_name = Column(String(255), nullable=False)
    stream_group = Column(String(50), nullable=False)


class Cutoff2025(Base):
    __tablename__ = "cutoffs_2025"
    
    id = Column(Integer, primary_key=True)
    college_code = Column(String(10), ForeignKey("colleges.college_code"), nullable=False)
    course_code = Column(String(10), ForeignKey("courses.course_code"), nullable=False)
    category = Column(String(15), nullable=False)
    round_no = Column(Integer, nullable=False)
    cutoff_rank = Column(Integer, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('college_code', 'course_code', 'category', 'round_no', name='uniq_cutoff_node'),
    )


def get_db():
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ensure_college_location(college: dict) -> dict:
    """Ensure every college dict has a non-empty location for UI dropdowns."""
    if college.get("location"):
        return college
    try:
        from data_loader import KNOWN_COLLEGE_INFO, infer_location_from_name
    except ImportError:
        from .data_loader import KNOWN_COLLEGE_INFO, infer_location_from_name
    code = college.get("college_code", "")
    known = KNOWN_COLLEGE_INFO.get(code, {})
    college["location"] = known.get("location") or infer_location_from_name(
        college.get("college_name", "")
    )
    return college


def get_cutoffs_by_category(db, category: str, limit: Optional[int] = None) -> List[dict]:
    """
    Retrieve all cutoffs for a specific category (full dataset, not capped at 1000).
    """
    real_data = get_real_cutoffs(category, limit=limit)
    if real_data is not None:
        return real_data
    # Comprehensive college data from KCET 2026 PDF - 50+ colleges across all Karnataka locations
    colleges = {
        # Bangalore - Major tech hub
        "E001": {"name": "UVCE Bangalore", "location": "Bangalore", "type": "Government"},
        "E002": {"name": "SJCE Bangalore", "location": "Bangalore", "type": "Government"},
        "E003": {"name": "BMS College of Engineering", "location": "Bangalore", "type": "Private-Aided"},
        "E004": {"name": "Dr. Ambedkar Institute of Technology", "location": "Bangalore", "type": "Private-Aided"},
        "E005": {"name": "RV College of Engineering", "location": "Bangalore", "type": "Private-Unaided"},
        "E006": {"name": "MS Ramaiah Institute of Technology", "location": "Bangalore", "type": "Private-Unaided"},
        "E007": {"name": "Dayananda Sagar College", "location": "Bangalore", "type": "Private-Unaided"},
        "E008": {"name": "Bangalore Institute of Technology", "location": "Bangalore", "type": "Private-Unaided"},
        "E009": {"name": "PES University", "location": "Bangalore", "type": "Private-Unaided"},
        "E010": {"name": "Sir M.V Institute of Tech", "location": "Bangalore", "type": "Private-Unaided"},
        "E082": {"name": "JSS Academy of Technical Education", "location": "Bangalore", "type": "Private-Unaided"},
        "E095": {"name": "AMC Engineering College", "location": "Bangalore", "type": "Private-Unaided"},
        "E103": {"name": "Global Academy of Technology", "location": "Bangalore", "type": "Private-Unaided"},
        "E145": {"name": "Rajarajeswari College", "location": "Bangalore", "type": "Private-Unaided"},
        "E149": {"name": "Cambridge Institute of Technology", "location": "Bangalore", "type": "Private-Unaided"},
        
        # Mysore - Educational hub
        "E021": {"name": "Sri Jayachamarajendra College of Engineering", "location": "Mysore", "type": "Government"},
        "E022": {"name": "The National Institute of Engineering", "location": "Mysore", "type": "Government"},
        "E057": {"name": "JSS Science and Technology University", "location": "Mysore", "type": "Private-University"},
        "E071": {"name": "Vidya Vardhaka College of Engineering", "location": "Mysore", "type": "Private-Unaided"},
        
        # Belgaum/Belagavi - Multi-institute hub
        "E029": {"name": "Maratha Mandal Engineering College", "location": "Belgaum", "type": "Private-Unaided"},
        "E036": {"name": "KLE Technological University", "location": "Belgaum", "type": "Private-University"},
        "E037": {"name": "KLS Gogte Institute of Technology", "location": "Belgaum", "type": "Private-Unaided"},
        "E175": {"name": "SG Balekundri Institute of Technology", "location": "Belgaum", "type": "Private-Unaided"},
        "E185": {"name": "Angadi Institute of Technology", "location": "Belgaum", "type": "Private-Unaided"},
        
        # Hubballi/Dharwad - Textile and engineering
        "E265": {"name": "Jain College of Engineering Technology", "location": "Hubballi", "type": "Private-Unaided"},
        "E241": {"name": "KLE Technological University BV Bhoomraddi", "location": "Hubballi", "type": "Private-University"},
        
        # Mangalore/Coastal - Maritime influence
        "E144": {"name": "Srinivas Institute of Technology", "location": "Mangalore", "type": "Private-Unaided"},
        "E146": {"name": "Shreedevi Institute of Technology", "location": "Mangalore", "type": "Private-Unaided"},
        "E151": {"name": "Mangalore Institute of Technology", "location": "Mangalore", "type": "Private-Unaided"},
        "E159": {"name": "Karavali Institute of Technology", "location": "Mangalore", "type": "Private-Unaided"},
        
        # Hassan - Western ghats region
        "E024": {"name": "Malnad College of Engineering", "location": "Hassan", "type": "Government"},
        "E155": {"name": "Government Engineering College Hassan", "location": "Hassan", "type": "Government"},
        
        # Davangere - Government hub
        "E061": {"name": "University BDT College of Engineering", "location": "Davangere", "type": "Government"},
        "E062": {"name": "Bapuji Institute of Engineering", "location": "Davangere", "type": "Private-Unaided"},
        "E114": {"name": "GM Institute of Technology", "location": "Davangere", "type": "Private-Unaided"},
        
        # Tumkur - Industrial area
        "E016": {"name": "Siddaganga Institute of Technology", "location": "Tumkur", "type": "Private-Unaided"},
        "E130": {"name": "Shridevi Institute of Engineering", "location": "Tumkur", "type": "Private-Unaided"},
        
        # Chikkaballapur
        "E014": {"name": "SJC Institute of Technology", "location": "Chikkaballapur", "type": "Private-Unaided"},
        "E278": {"name": "Visvesvaraya Technological University", "location": "Chikkaballapur", "type": "Government"},
        
        # Gulbarga - Northern plateau
        "E041": {"name": "PDA College of Engineering", "location": "Gulbarga", "type": "Government"},
        "E128": {"name": "Sharnbasva University", "location": "Gulbarga", "type": "Private-University"},
        
        # Raichur - Eastern region
        "E046": {"name": "HKES Sir M Visveraya College of Engineering", "location": "Raichur", "type": "Private-Unaided"},
        "E162": {"name": "Government Engineering College Raichur", "location": "Raichur", "type": "Government"},
        "E176": {"name": "Navodaya Institute of Technology", "location": "Raichur", "type": "Private-Unaided"},
        
        # Ballari - Mining region
        "E045": {"name": "Rao Bahadur YM Engineering College", "location": "Ballari", "type": "Private-Unaided"},
        "E075": {"name": "Ballari Institute of Technology", "location": "Ballari", "type": "Private-Unaided"},
        
        # Kolar - Adjacent to Bangalore
        "E015": {"name": "Dr T Thimmaiah Institute of Technology", "location": "Kolar", "type": "Private-Unaided"},
        "E184": {"name": "C Byre Gowda Institute of Technology", "location": "Kolar", "type": "Private-Unaided"},
        
        # Mandya - Agricultural area
        "E023": {"name": "PES College of Engineering", "location": "Mandya", "type": "Government"},
        "E210": {"name": "G Madegowda Institute of Technology", "location": "Mandya", "type": "Private-Unaided"},
        
        # Gadag
        "E028": {"name": "Tontadarya College of Engineering", "location": "Gadag", "type": "Private-Unaided"},
        
        # Bidar
        "E044": {"name": "Bheemanna Khandre Institute of Technology", "location": "Bidar", "type": "Private-Unaided"},
        
        # Shivamogga
        "E065": {"name": "Jawaharlal Nehru National College of Engineering", "location": "Shivamogga", "type": "Private-Unaided"},
        "E150": {"name": "PES Institute of Technology and Management", "location": "Shivamogga", "type": "Private-Unaided"},
        
        # DK/Coastal
        "E054": {"name": "KVG College of Engineering", "location": "Sullia", "type": "Private-Unaided"},
        "E160": {"name": "Sahyadri College of Engineering", "location": "Mangalore", "type": "Private-Unaided"},
        "E165": {"name": "Yenepoya Institute of Technology", "location": "Mangalore", "type": "Private-Unaided"},
    }
    
    courses = {
        "CS": {"name": "Computer Science", "base_cut": 800},
        "IS": {"name": "Information Science", "base_cut": 1200},
        "EC": {"name": "Electronics and Communication", "base_cut": 1500},
        "ME": {"name": "Mechanical Engineering", "base_cut": 2000},
        "CE": {"name": "Civil Engineering", "base_cut": 2500},
        "AI": {"name": "Artificial Intelligence", "base_cut": 900},
        "DS": {"name": "Data Science", "base_cut": 1000},
        "BT": {"name": "Biotechnology", "base_cut": 1800},
    }
    
    mock_cutoffs = []
    
    # Generate cutoff data for all college-course combinations
    for college_code, college_info in colleges.items():
        for course_code, course_info in courses.items():
            # Vary cutoffs based on college type and course difficulty
            base_cutoff = course_info["base_cut"]
            if college_info["type"] == "Government":
                multiplier = 0.6  # Government colleges have lower cutoffs
            elif "University" in college_info["type"]:
                multiplier = 0.75  # Universities competitive
            else:
                multiplier = 1.0  # Private colleges maintain base cutoff
            
            # Add prestige variations
            if college_code in ["E001", "E003", "E021", "E022"]:  # Top colleges
                multiplier -= 0.15
            elif college_code in ["E006", "E009", "E149"]:  # Well-known colleges
                multiplier -= 0.05
            
            round1 = int(base_cutoff * multiplier)
            round2 = int(round1 * 1.25)
            round3 = int(round1 * 1.65)
            
            mock_cutoffs.append({
                "college_code": college_code,
                "college_name": college_info["name"],
                "location": college_info["location"],
                "college_type": college_info["type"],
                "course_code": course_code,
                "course_name": course_info["name"],
                "stream_group": "Engineering",
                "category": category,
                "round_1_cutoff": round1,
                "round_2_cutoff": round2,
                "round_3_cutoff": round3,
            })
    
    return mock_cutoffs[:limit]


def get_all_categories(db=None) -> List[str]:
    """Get all available student categories."""
    try:
        from data_loader import get_all_categories as _get_all_categories
    except ImportError:
        from .data_loader import get_all_categories as _get_all_categories
    return _get_all_categories()


def get_colleges(db=None) -> List[dict]:
    """Get all colleges. First tries real KEA 2025 data, then falls back to mock data."""
    real_colleges = get_real_colleges()
    if real_colleges:
        return [_ensure_college_location(dict(c)) for c in real_colleges]
    # Fallback: comprehensive college data from KCET 2026 seat matrix
    return [
        # Bangalore (15 colleges)
        {"college_code": "E001", "college_name": "UVCE Bangalore", "location": "Bangalore", "college_type": "Government"},
        {"college_code": "E002", "college_name": "SJCE Bangalore", "location": "Bangalore", "college_type": "Government"},
        {"college_code": "E003", "college_name": "BMS College of Engineering", "location": "Bangalore", "college_type": "Private-Aided"},
        {"college_code": "E004", "college_name": "Dr. Ambedkar Institute of Technology", "location": "Bangalore", "college_type": "Private-Aided"},
        {"college_code": "E005", "college_name": "RV College of Engineering", "location": "Bangalore", "college_type": "Private-Unaided"},
        {"college_code": "E006", "college_name": "MS Ramaiah Institute of Technology", "location": "Bangalore", "college_type": "Private-Unaided"},
        {"college_code": "E007", "college_name": "Dayananda Sagar College", "location": "Bangalore", "college_type": "Private-Unaided"},
        {"college_code": "E008", "college_name": "Bangalore Institute of Technology", "location": "Bangalore", "college_type": "Private-Unaided"},
        {"college_code": "E009", "college_name": "PES University", "location": "Bangalore", "college_type": "Private-Unaided"},
        {"college_code": "E010", "college_name": "Sir M.V Institute of Tech", "location": "Bangalore", "college_type": "Private-Unaided"},
        {"college_code": "E082", "college_name": "JSS Academy of Technical Education", "location": "Bangalore", "college_type": "Private-Unaided"},
        {"college_code": "E095", "college_name": "AMC Engineering College", "location": "Bangalore", "college_type": "Private-Unaided"},
        {"college_code": "E103", "college_name": "Global Academy of Technology", "location": "Bangalore", "college_type": "Private-Unaided"},
        {"college_code": "E145", "college_name": "Rajarajeswari College", "location": "Bangalore", "college_type": "Private-Unaided"},
        {"college_code": "E149", "college_name": "Cambridge Institute of Technology", "location": "Bangalore", "college_type": "Private-Unaided"},
        
        # Mysore (4 colleges)
        {"college_code": "E021", "college_name": "Sri Jayachamarajendra College of Engineering", "location": "Mysore", "college_type": "Government"},
        {"college_code": "E022", "college_name": "The National Institute of Engineering", "location": "Mysore", "college_type": "Government"},
        {"college_code": "E057", "college_name": "JSS Science and Technology University", "location": "Mysore", "college_type": "Private-University"},
        {"college_code": "E071", "college_name": "Vidya Vardhaka College of Engineering", "location": "Mysore", "college_type": "Private-Unaided"},
        
        # Belgaum (5 colleges)
        {"college_code": "E029", "college_name": "Maratha Mandal Engineering College", "location": "Belgaum", "college_type": "Private-Unaided"},
        {"college_code": "E036", "college_name": "KLE Technological University", "location": "Belgaum", "college_type": "Private-University"},
        {"college_code": "E037", "college_name": "KLS Gogte Institute of Technology", "location": "Belgaum", "college_type": "Private-Unaided"},
        {"college_code": "E175", "college_name": "SG Balekundri Institute of Technology", "location": "Belgaum", "college_type": "Private-Unaided"},
        {"college_code": "E185", "college_name": "Angadi Institute of Technology", "location": "Belgaum", "college_type": "Private-Unaided"},
        
        # Hubballi (2 colleges)
        {"college_code": "E265", "college_name": "Jain College of Engineering Technology", "location": "Hubballi", "college_type": "Private-Unaided"},
        {"college_code": "E241", "college_name": "KLE Technological University BV Bhoomraddi", "location": "Hubballi", "college_type": "Private-University"},
        
        # Mangalore (5 colleges)
        {"college_code": "E144", "college_name": "Srinivas Institute of Technology", "location": "Mangalore", "college_type": "Private-Unaided"},
        {"college_code": "E146", "college_name": "Shreedevi Institute of Technology", "location": "Mangalore", "college_type": "Private-Unaided"},
        {"college_code": "E151", "college_name": "Mangalore Institute of Technology", "location": "Mangalore", "college_type": "Private-Unaided"},
        {"college_code": "E159", "college_name": "Karavali Institute of Technology", "location": "Mangalore", "college_type": "Private-Unaided"},
        {"college_code": "E160", "college_name": "Sahyadri College of Engineering", "location": "Mangalore", "college_type": "Private-Unaided"},
        
        # Hassan (2 colleges)
        {"college_code": "E024", "college_name": "Malnad College of Engineering", "location": "Hassan", "college_type": "Government"},
        {"college_code": "E155", "college_name": "Government Engineering College Hassan", "location": "Hassan", "college_type": "Government"},
        
        # Davangere (3 colleges)
        {"college_code": "E061", "college_name": "University BDT College of Engineering", "location": "Davangere", "college_type": "Government"},
        {"college_code": "E062", "college_name": "Bapuji Institute of Engineering", "location": "Davangere", "college_type": "Private-Unaided"},
        {"college_code": "E114", "college_name": "GM Institute of Technology", "location": "Davangere", "college_type": "Private-Unaided"},
        
        # Tumkur (2 colleges)
        {"college_code": "E016", "college_name": "Siddaganga Institute of Technology", "location": "Tumkur", "college_type": "Private-Unaided"},
        {"college_code": "E130", "college_name": "Shridevi Institute of Engineering", "location": "Tumkur", "college_type": "Private-Unaided"},
        
        # Chikkaballapur (2 colleges)
        {"college_code": "E014", "college_name": "SJC Institute of Technology", "location": "Chikkaballapur", "college_type": "Private-Unaided"},
        {"college_code": "E278", "college_name": "Visvesvaraya Technological University", "location": "Chikkaballapur", "college_type": "Government"},
        
        # Gulbarga (2 colleges)
        {"college_code": "E041", "college_name": "PDA College of Engineering", "location": "Gulbarga", "college_type": "Government"},
        {"college_code": "E128", "college_name": "Sharnbasva University", "location": "Gulbarga", "college_type": "Private-University"},
        
        # Raichur (3 colleges)
        {"college_code": "E046", "college_name": "HKES Sir M Visveraya College of Engineering", "location": "Raichur", "college_type": "Private-Unaided"},
        {"college_code": "E162", "college_name": "Government Engineering College Raichur", "location": "Raichur", "college_type": "Government"},
        {"college_code": "E176", "college_name": "Navodaya Institute of Technology", "location": "Raichur", "college_type": "Private-Unaided"},
        
        # Ballari (2 colleges)
        {"college_code": "E045", "college_name": "Rao Bahadur YM Engineering College", "location": "Ballari", "college_type": "Private-Unaided"},
        {"college_code": "E075", "college_name": "Ballari Institute of Technology", "location": "Ballari", "college_type": "Private-Unaided"},
        
        # Kolar (2 colleges)
        {"college_code": "E015", "college_name": "Dr T Thimmaiah Institute of Technology", "location": "Kolar", "college_type": "Private-Unaided"},
        {"college_code": "E184", "college_name": "C Byre Gowda Institute of Technology", "location": "Kolar", "college_type": "Private-Unaided"},
        
        # Mandya (2 colleges)
        {"college_code": "E023", "college_name": "PES College of Engineering", "location": "Mandya", "college_type": "Government"},
        {"college_code": "E210", "college_name": "G Madegowda Institute of Technology", "location": "Mandya", "college_type": "Private-Unaided"},
        
        # Gadag (1 college)
        {"college_code": "E028", "college_name": "Tontadarya College of Engineering", "location": "Gadag", "college_type": "Private-Unaided"},
        
        # Bidar (1 college)
        {"college_code": "E044", "college_name": "Bheemanna Khandre Institute of Technology", "location": "Bidar", "college_type": "Private-Unaided"},
        
        # Shivamogga (2 colleges)
        {"college_code": "E065", "college_name": "Jawaharlal Nehru National College of Engineering", "location": "Shivamogga", "college_type": "Private-Unaided"},
        {"college_code": "E150", "college_name": "PES Institute of Technology and Management", "location": "Shivamogga", "college_type": "Private-Unaided"},
        
        # Sullia/DK (1 college)
        {"college_code": "E054", "college_name": "KVG College of Engineering", "location": "Sullia", "college_type": "Private-Unaided"},
    ]


def get_courses(db=None) -> List[dict]:
    """Get all courses. First tries real KEA 2025 data, then falls back to mock data."""
    real_courses = get_real_courses()
    if real_courses:
        return real_courses
    # Fallback
    return [
        {"course_code": "CS", "course_name": "Computer Science", "stream_group": "Engineering"},
        {"course_code": "IS", "course_name": "Information Science", "stream_group": "Engineering"},
        {"course_code": "EC", "course_name": "Electronics and Communication", "stream_group": "Engineering"},
        {"course_code": "ME", "course_name": "Mechanical Engineering", "stream_group": "Engineering"},
        {"course_code": "CE", "course_name": "Civil Engineering", "stream_group": "Engineering"},
        {"course_code": "AI", "course_name": "Artificial Intelligence", "stream_group": "Engineering"},
        {"course_code": "DS", "course_name": "Data Science", "stream_group": "Engineering"},
        {"course_code": "BT", "course_name": "Biotechnology", "stream_group": "Engineering"},
    ]
