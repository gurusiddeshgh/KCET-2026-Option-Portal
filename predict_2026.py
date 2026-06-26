"""
KCET 2026 Prediction Engine
Uses 2025 cutoff data to predict 2026 college admissions
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal, Cutoff2025, College, Course
from models import StudentProfile
import json
from typing import Literal

def evaluate_chancing_logic(student_rank: int, cutoff_2025: int, round_no: int) -> Literal["High", "Medium", "Low", "Unlikely"]:
    """
    Evaluates the chancing probability using the Variance Ratio formula.
    
    Variance Ratio (φ) = R_student / (C_2025 × η_round)
    
    Where:
    - R_student: Student's verified rank
    - C_2025: Raw historical cutoff rank
    - η_round: Historical mobility multiplier (Round 1 = 1.00, Round 2 = 1.05, Round 3 = 1.12)
    """
    # Set historical buffer multipliers per round
    buffers = {1: 1.00, 2: 1.05, 3: 1.12}
    beta = buffers.get(round_no, 1.00)
    
    # Avoid division by zero
    if cutoff_2025 <= 0:
        return "Unlikely"
    
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

def get_all_cutoffs_for_category(db, category: str = "GM"):
    """Retrieve all cutoff data for a category"""
    query = db.query(Cutoff2025).filter_by(category=category)
    results = []
    
    for cutoff in query:
        college = db.query(College).filter_by(college_code=cutoff.college_code).first()
        course = db.query(Course).filter_by(course_code=cutoff.course_code).first()
        
        if not college or not course:
            continue
            
        results.append({
            "college_code": cutoff.college_code,
            "college_name": college.college_name,
            "course_code": cutoff.course_code,
            "course_name": course.course_name,
            "location": college.location,
            "college_type": college.college_type,
            "category": category,
            "round_no": cutoff.round_no,
            "cutoff_rank": cutoff.cutoff_rank
        })
    
    return results

def predict_2026_admission(student_rank: int, category: str = "GM", preferred_locations=None, limit=100):
    """
    Predict 2026 KCET admissions based on student rank and 2025 cutoff data
    
    Args:
        student_rank: Student's KCET rank
        category: Student category (GM, 2AR, 3BK, etc.)
        preferred_locations: List of preferred locations (optional)
        limit: Maximum predictions to return
    
    Returns:
        Prediction results with chancing probabilities
    """
    
    db = SessionLocal()
    
    try:
        print(f"\n{'='*70}")
        print(f"KCET 2026 PREDICTION ENGINE")
        print(f"{'='*70}")
        print(f"Student Rank: {student_rank}")
        print(f"Category: {category}")
        print(f"{'='*70}\n")
        
        # Get all cutoff data for this category
        cutoff_data = get_all_cutoffs_for_category(db, category)
        print(f"Found {len(cutoff_data)} cutoff records for {category} category\n")
        
        if not cutoff_data:
            print(f"No cutoff data available for category: {category}")
            return None
        
        # Create student profile
        profile = StudentProfile(
            rank=student_rank,
            category=category,
            preferred_locations=preferred_locations or [],
            preferred_courses=None
        )
        
        # Group cutoffs by college-course combination, keeping Round 2 as primary
        college_course_data = {}
        for cutoff in cutoff_data:
            key = f"{cutoff['college_code']}|{cutoff['course_code']}"
            
            if key not in college_course_data:
                college_course_data[key] = {
                    "college_code": cutoff['college_code'],
                    "college_name": cutoff['college_name'],
                    "course_code": cutoff['course_code'],
                    "course_name": cutoff['course_name'],
                    "location": cutoff['location'],
                    "college_type": cutoff['college_type'],
                    "cutoff_rank": cutoff['cutoff_rank'],  # Will use Round 2 if available
                    "round_1_cutoff": None,
                    "round_2_cutoff": None,
                    "round_3_cutoff": None,
                }
            
            # Store cutoffs by round
            if cutoff['round_no'] == 1:
                college_course_data[key]['round_1_cutoff'] = cutoff['cutoff_rank']
            elif cutoff['round_no'] == 2:
                college_course_data[key]['round_2_cutoff'] = cutoff['cutoff_rank']
                college_course_data[key]['cutoff_rank'] = cutoff['cutoff_rank']  # Use Round 2 as primary
            elif cutoff['round_no'] == 3:
                college_course_data[key]['round_3_cutoff'] = cutoff['cutoff_rank']
        
        print(f"Unique college-course combinations: {len(college_course_data)}\n")
        
        # Calculate predictions for each college-course combination
        predictions = []
        
        for key, item in college_course_data.items():
            # Skip if no Round 2 data (use it as the baseline)
            if not item['round_2_cutoff']:
                continue
            
            # Calculate variance ratio
            ratio = student_rank / item['round_2_cutoff']
            
            # Evaluate chancing for each round
            chancing = {
                "round_1": evaluate_chancing_logic(
                    student_rank, 
                    item['round_1_cutoff'] or item['round_2_cutoff'], 
                    1
                ),
                "round_2": evaluate_chancing_logic(
                    student_rank, 
                    item['round_2_cutoff'], 
                    2
                ),
                "round_3": evaluate_chancing_logic(
                    student_rank, 
                    item['round_3_cutoff'] or item['round_2_cutoff'], 
                    3
                )
            }
            
            predictions.append({
                "college_code": item['college_code'],
                "college_name": item['college_name'],
                "course_code": item['course_code'],
                "course_name": item['course_name'],
                "location": item['location'],
                "college_type": item['college_type'],
                "cutoff_rank_2025": item['round_2_cutoff'],
                "variance_ratio": round(ratio, 3),
                "chancing": chancing,
                "category": category,
                "predicted_cutoff_2026": round(item['round_2_cutoff'] * 0.98),  # Estimate 2% improvement
            })
        
        print(f"Calculated predictions for {len(predictions)} college-course combinations\n")
        
        # Filter by location if specified
        if preferred_locations:
            predictions = [p for p in predictions if p['location'].lower() in [loc.lower() for loc in preferred_locations]]
            print(f"After location filter: {len(predictions)} options\n")
        
        # Sort by variance ratio (closer to 1.0 is better for target matches)
        predictions.sort(key=lambda x: abs(x['variance_ratio'] - 1.0))
        
        # Categorize predictions
        dream_choices = [p for p in predictions if p['variance_ratio'] < 0.95]
        target_choices = [p for p in predictions if 0.95 <= p['variance_ratio'] <= 1.15]
        safety_choices = [p for p in predictions if p['variance_ratio'] > 1.15]
        
        print(f"PREDICTION DISTRIBUTION:")
        print(f"  Dream Pool (High Risk, High Reward):    {len(dream_choices)} options")
        print(f"  Target Pool (Realistic Targets):        {len(target_choices)} options")
        print(f"  Safety Pool (Safe Bets):               {len(safety_choices)} options")
        print(f"  Total Options:                          {len(predictions)} options\n")
        
        # Return top results
        top_predictions = predictions[:limit]
        
        # Print top 20 predictions
        print(f"TOP {min(20, len(top_predictions))} PREDICTIONS:\n")
        print(f"{'College':<30} {'Course':<20} {'2025 Cutoff':<12} {'Est 2026':<12} {'Best Round':<10}")
        print("-" * 85)
        
        for i, pred in enumerate(top_predictions[:20], 1):
            best_round = max(pred['chancing'].items(), key=lambda x: {'High': 3, 'Medium': 2, 'Low': 1, 'Unlikely': 0}[x[1]])
            print(f"{pred['college_name'][:28]:<30} {pred['course_name'][:18]:<20} {pred['cutoff_rank_2025']:<12} {pred['predicted_cutoff_2026']:<12} {best_round[0]:<10}")
        
        print(f"\n{'='*70}")
        print(f"PREDICTION SUMMARY")
        print(f"{'='*70}")
        print(f"Based on 2025 historical cutoff data from KEA")
        print(f"2026 estimates assume 1-2% improvement in competition\n")
        
        return {
            "student_rank": student_rank,
            "category": category,
            "predictions": top_predictions,
            "summary": {
                "dream_pool": len(dream_choices),
                "target_pool": len(target_choices),
                "safety_pool": len(safety_choices),
                "total_options": len(predictions)
            }
        }
        
    finally:
        db.close()

if __name__ == "__main__":
    # Test with a sample student
    # Change these values to test different scenarios
    
    student_rank = 5000  # Example: Rank 5000
    category = "GM"  # General Merit
    preferred_locations = None  # No location filter - see all options
    
    result = predict_2026_admission(student_rank, category, preferred_locations, limit=100)
    
    if result:
        print(f"\nSample Top 5 Predictions (JSON):")
        sample = result['predictions'][:5]
        print(json.dumps([{
            'college': p['college_name'],
            'course': p['course_name'],
            'cutoff_2025': p['cutoff_rank_2025'],
            'predicted_2026': p['predicted_cutoff_2026'],
            'chancing': p['chancing']
        } for p in sample], indent=2))
