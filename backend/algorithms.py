from typing import Dict, List, Literal, Optional
try:
    from .models import StudentProfile, ChoiceNode, CutoffData
except ImportError:
    from models import StudentProfile, ChoiceNode, CutoffData

def evaluate_chancing_logic(student_rank: int, cutoff_2025: Optional[int], round_no: int) -> Literal["High", "Medium", "Low", "Unlikely"]:
    """
    Evaluates the chancing probability using the Variance Ratio formula.
    
    Variance Ratio (φ) = R_student / (C_2025 × η_round)
    
    Where:
    - R_student: Student's verified rank
    - C_2025: Raw historical cutoff rank
    - η_round: Historical mobility multiplier (Round 1 = 1.00, Round 2 = 1.05, Round 3 = 1.12)
    """
    # Avoid division by zero and NoneType values
    if cutoff_2025 is None or cutoff_2025 <= 0:
        return "Unlikely"

    # Set historical buffer multipliers per round
    buffers = {1: 1.00, 2: 1.05, 3: 1.12}
    beta = buffers.get(round_no, 1.00)
    
    # Calculate the variance ratio
    variance_ratio = student_rank / (cutoff_2025 * beta)
    
    if variance_ratio <= 0.90:
        return "High"      # Deeply safe bracket
    elif 0.90 < variance_ratio <= 1.02:
        return "Medium"    # Target boundary
    elif 1.02 < variance_ratio <= 1.15:
        return "Low"       # Reach bracket (needs seat drops)
    else:
        return "Unlikely"  # Extreme stretch


def generate_optimized_100_list(profile: StudentProfile, cutoff_dataset: List[Dict]) -> Dict:
    """
    Processes a list of valid choices and generates an ordered list of 100 choices 
    based on the systematic Sandwich Strategy (20-50-30 distribution).
    
    - Dream Pool: High risk / High reward (Ratio < 0.95) - 20 choices
    - Target Pool: Realistic targets (Ratio 0.95 to 1.15) - 50 choices
    - Safety Pool: Failure safeguards (Ratio > 1.15) - 30 choices
    """
    dream_pool = []    # High risk / High reward
    target_pool = []   # Realistic targets
    safety_pool = []   # Failure safeguards
    
    # Process each cutoff entry
    for item in cutoff_dataset:
        r2_val = item.get("round_2_cutoff")
        if r2_val is None:
            r2_val = item.get("cutoff_rank")
        if r2_val is None:
            r2_val = item.get("round_1_cutoff") or item.get("round_3_cutoff") or 1
            
        r2_cutoff = r2_val
        if r2_cutoff <= 0:
            continue
            
        ratio = profile.rank / r2_cutoff
        
        # Robustly determine fallbacks for R1 and R3
        r1_val = item.get("round_1_cutoff")
        r1_cutoff = r1_val if r1_val is not None else r2_cutoff
        
        r3_val = item.get("round_3_cutoff")
        r3_cutoff = r3_val if r3_val is not None else r2_cutoff
        
        # Create a choice node
        node = {
            "college_code": item["college_code"],
            "college_name": item["college_name"],
            "course_code": item["course_code"],
            "course_name": item.get("course_name", item["course_code"]),
            "location": item["location"],
            "college_type": item.get("college_type", "Unknown"),
            "chancing": {
                "round_1": evaluate_chancing_logic(profile.rank, r1_cutoff, 1),
                "round_2": evaluate_chancing_logic(profile.rank, r2_cutoff, 2),
                "round_3": evaluate_chancing_logic(profile.rank, r3_cutoff, 3)
            },
            "ratio": ratio
        }
        
        # Classify into pools
        if ratio < 0.95:
            dream_pool.append(node)
        elif 0.95 <= ratio <= 1.15:
            target_pool.append(node)
        else:
            safety_pool.append(node)
    
    # Sort pools internally by college code (proxy for popularity)
    dream_pool.sort(key=lambda x: x["college_code"])
    target_pool.sort(key=lambda x: x["college_code"])
    safety_pool.sort(key=lambda x: x["college_code"])
    
    # Apply 20-50-30 distribution model
    dream_slice = dream_pool[:20]
    target_slice = target_pool[:50]
    safety_slice = safety_pool[:30]
    
    # Combine in order: Dream -> Target -> Safety
    final_sequence = dream_slice + target_slice + safety_slice
    
    # Enforce priority indices
    final_choices = []
    for idx, choice in enumerate(final_sequence):
        final_choice = ChoiceNode(
            priority_number=idx + 1,
            college_code=choice["college_code"],
            course_code=choice["course_code"],
            college_name=choice["college_name"],
            course_name=choice["course_name"],
            location=choice["location"],
            chancing=choice["chancing"]
        )
        final_choices.append(final_choice)
    
    # Prepare response metadata
    return {
        "total_choices": len(final_choices),
        "dream_count": len(dream_slice),
        "target_count": len(target_slice),
        "safety_count": len(safety_slice),
        "choices": final_choices
    }


def filter_cutoffs_by_profile(all_cutoffs: List[Dict], profile: StudentProfile) -> List[Dict]:
    """
    Filters cutoff data based on student preferences (location, course).
    If no preferences specified, returns all cutoffs.
    """
    filtered = all_cutoffs
    
    # Filter by preferred courses if specified
    if profile.preferred_courses:
        filtered = [c for c in filtered if c.get("course_code") in profile.preferred_courses]
    
    # Filter by preferred locations if specified
    if profile.preferred_locations:
        filtered = [c for c in filtered if c.get("location") in profile.preferred_locations]
    
    # If no colleges match after preference filters, return all original cutoffs
    # This ensures we always have colleges to show, even for edge cases
    if not filtered:
        filtered = all_cutoffs
    
    return filtered
