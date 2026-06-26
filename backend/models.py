from pydantic import BaseModel
from typing import Dict, List, Literal, Optional

class StudentProfile(BaseModel):
    rank: int
    category: str
    preferred_locations: Optional[List[str]] = None
    preferred_courses: Optional[List[str]] = None

class PredictionNode(BaseModel):
    college_code: str
    college_name: str
    course_code: str
    course_name: str
    location: str
    college_type: str
    round_probabilities: Dict[int, Literal["High", "Medium", "Low", "Unlikely"]]
    base_cutoff: int

class ChoiceNode(BaseModel):
    priority_number: int
    college_code: str
    course_code: str
    college_name: str
    course_name: str
    location: str
    chancing: Dict[str, str]

class OptimizedChoiceList(BaseModel):
    total_choices: int
    dream_count: int
    target_count: int
    safety_count: int
    choices: List[ChoiceNode]

class CutoffData(BaseModel):
    college_code: str
    college_name: str
    course_code: str
    course_name: str
    location: str
    college_type: str
    round_1_cutoff: int
    round_2_cutoff: int
    round_3_cutoff: int
    category: str
