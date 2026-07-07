from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
from typing import List

try:
    from .models import StudentProfile, OptimizedChoiceList, ChoiceNode
    from .database import get_db, get_cutoffs_by_category, get_all_categories, get_colleges, get_courses
    from .algorithms import generate_optimized_100_list, filter_cutoffs_by_profile, evaluate_chancing_logic
except ImportError:
    from models import StudentProfile, OptimizedChoiceList, ChoiceNode
    from database import get_db, get_cutoffs_by_category, get_all_categories, get_colleges, get_courses
    from algorithms import generate_optimized_100_list, filter_cutoffs_by_profile, evaluate_chancing_logic

# Initialize FastAPI app
app = FastAPI(
    title="KCET 2026 College Predictor & Option Entry Optimizer",
    description="High-concurrency college prediction and choice optimization portal",
    version="1.0.0"
)

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "KCET 2026 Portal",
        "version": "1.0.0"
    }


@app.get("/api/categories")
async def get_categories():
    """
    Retrieve all available student categories.
    Example: GM, 2AR, 3BK, SCG, STK, GMEWS
    """
    try:
        categories = get_all_categories()
        return {
            "status": "success",
            "count": len(categories),
            "categories": categories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/colleges")
async def get_colleges_list():
    """
    Retrieve all available colleges with basic information.
    """
    try:
        colleges = get_colleges()
        return {
            "status": "success",
            "count": len(colleges),
            "colleges": colleges
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/courses")
async def get_courses_list():
    """
    Retrieve all available courses across all colleges.
    """
    try:
        courses = get_courses()
        return {
            "status": "success",
            "count": len(courses),
            "courses": courses
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/predict")
async def predict_colleges(profile: StudentProfile, db: Session = Depends(get_db)):
    """
    Generate optimized college choice list based on student profile.
    
    Request body:
    {
        "rank": 5000,
        "category": "GM",
        "preferred_locations": ["Bangalore", "Belagavi"],
        "preferred_streams": ["Engineering"]
    }
    
    Response: List of 100 optimized choices with probability predictions
    """
    try:
        # Validate input
        if profile.rank <= 0:
            raise HTTPException(status_code=400, detail="Rank must be positive")
        if not profile.category:
            raise HTTPException(status_code=400, detail="Category is required")
        
        # Fetch cutoff data for the category
        cutoff_data = get_cutoffs_by_category(db, profile.category)
        
        if not cutoff_data:
            raise HTTPException(
                status_code=404, 
                detail=f"No cutoff data available for category: {profile.category}"
            )
        
        # Filter based on student preferences
        filtered_cutoffs = filter_cutoffs_by_profile(cutoff_data, profile)
        
        if not filtered_cutoffs:
            raise HTTPException(
                status_code=404,
                detail="No colleges match your criteria. Try expanding your search."
            )
        
        # Generate optimized list using Sandwich Strategy
        result = generate_optimized_100_list(profile, filtered_cutoffs)
        
        return {
            "status": "success",
            "student_rank": profile.rank,
            "category": profile.category,
            "total_matches": len(filtered_cutoffs),
            "total_choices": result["total_choices"],
            "dream_count": result["dream_count"],
            "target_count": result["target_count"],
            "safety_count": result["safety_count"],
            "choices": [choice.dict() for choice in result["choices"]]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/evaluate-chance")
async def evaluate_chance(rank: int, cutoff_rank: int, round_no: int = 2):
    """
    Evaluate chancing probability for a specific college-course-round combination.
    
    Query parameters:
    - rank: Student's rank
    - cutoff_rank: Historical cutoff rank for the college-course
    - round_no: Round number (1, 2, or 3)
    
    Response: Probability assessment (High, Medium, Low, Unlikely)
    """
    try:
        if rank <= 0 or cutoff_rank <= 0:
            raise HTTPException(status_code=400, detail="Rank values must be positive")
        if round_no not in [1, 2, 3]:
            raise HTTPException(status_code=400, detail="Round number must be 1, 2, or 3")
        
        chancing = evaluate_chancing_logic(rank, cutoff_rank, round_no)
        
        return {
            "status": "success",
            "student_rank": rank,
            "cutoff_rank": cutoff_rank,
            "round": round_no,
            "chancing": chancing
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "service": "KCET 2026 Portal API"
    }


@app.get("/api/locations")
async def get_all_locations():
    """
    Retrieve all unique locations where colleges are available in Karnataka.
    Sorted alphabetically for easy dropdown display.
    """
    try:
        colleges = get_colleges()
        locations = sorted({
            college["location"]
            for college in colleges
            if college.get("location") and college["location"] != "Other"
        })
        return {
            "status": "success",
            "count": len(locations),
            "locations": locations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/predict/2026")
async def predict_2026_admissions(rank: int, category: str = "GM", location: str = None, db: Session = Depends(get_db)):
    """
    Predict 2026 KCET college admissions using 2025 historical cutoff data.
    
    Query parameters:
    - rank: Student's KCET rank (required)
    - category: Student category (default: "GM" - General Merit)
    - location: Filter results to specific location (optional)
    
    Response: Ranked list of colleges with 2026 predictions and chancing probabilities
    
    Example:
    GET /api/predict/2026?rank=5000&category=GM&location=Bangalore
    """
    try:
        # Validate input
        if rank <= 0:
            raise HTTPException(status_code=400, detail="Rank must be a positive integer")
        
        # Import required models
        from database import Cutoff2025, College, Course
        
        # Fetch all cutoff data for this category
        cutoff_query = db.query(Cutoff2025).filter_by(category=category)
        
        if cutoff_query.count() == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No cutoff data available for category: {category}"
            )
        
        # Group cutoffs by college-course combination
        college_course_data = {}
        
        for cutoff in cutoff_query:
            key = f"{cutoff.college_code}|{cutoff.course_code}"
            
            if key not in college_course_data:
                college = db.query(College).filter_by(college_code=cutoff.college_code).first()
                course = db.query(Course).filter_by(course_code=cutoff.course_code).first()
                
                if not college or not course:
                    continue
                
                college_course_data[key] = {
                    "college_code": cutoff.college_code,
                    "college_name": college.college_name,
                    "course_code": cutoff.course_code,
                    "course_name": course.course_name,
                    "location": college.location,
                    "college_type": college.college_type,
                    "round_1_cutoff": None,
                    "round_2_cutoff": None,
                    "round_3_cutoff": None,
                }
            
            # Store cutoffs by round
            if cutoff.round_no == 1:
                college_course_data[key]['round_1_cutoff'] = cutoff.cutoff_rank
            elif cutoff.round_no == 2:
                college_course_data[key]['round_2_cutoff'] = cutoff.cutoff_rank
            elif cutoff.round_no == 3:
                college_course_data[key]['round_3_cutoff'] = cutoff.cutoff_rank
        
        # Calculate predictions
        predictions = []
        
        for key, item in college_course_data.items():
            # Skip if no Round 2 data
            if not item['round_2_cutoff']:
                continue
            
            # Apply location filter if specified
            if location and location.lower() not in item['location'].lower():
                continue
            
            # Calculate variance ratio
            ratio = rank / item['round_2_cutoff']
            
            # Evaluate chancing for each round
            chancing = {
                "round_1": evaluate_chancing_logic(rank, item['round_1_cutoff'] or item['round_2_cutoff'], 1),
                "round_2": evaluate_chancing_logic(rank, item['round_2_cutoff'], 2),
                "round_3": evaluate_chancing_logic(rank, item['round_3_cutoff'] or item['round_2_cutoff'], 3)
            }
            
            # Determine pool
            if ratio < 0.95:
                pool = "dream"
            elif 0.95 <= ratio <= 1.15:
                pool = "target"
            else:
                pool = "safety"
            
            predictions.append({
                "college_code": item['college_code'],
                "college_name": item['college_name'],
                "course_code": item['course_code'],
                "course_name": item['course_name'],
                "location": item['location'],
                "college_type": item['college_type'],
                "cutoff_rank_2025_round2": item['round_2_cutoff'],
                "predicted_cutoff_2026": round(item['round_2_cutoff'] * 0.98),
                "variance_ratio": round(ratio, 3),
                "pool": pool,
                "chancing": chancing,
            })
        
        # Sort by variance ratio (closest to 1.0 for targets)
        predictions.sort(key=lambda x: abs(x['variance_ratio'] - 1.0))
        
        # Count pools
        dream_pool = [p for p in predictions if p['pool'] == 'dream']
        target_pool = [p for p in predictions if p['pool'] == 'target']
        safety_pool = [p for p in predictions if p['pool'] == 'safety']
        
        return {
            "status": "success",
            "student_rank": rank,
            "category": category,
            "location_filter": location,
            "summary": {
                "total_options": len(predictions),
                "dream_pool": len(dream_pool),
                "target_pool": len(target_pool),
                "safety_pool": len(safety_pool),
            },
            "top_20_predictions": [p for p in predictions[:20]],
            "all_predictions": predictions
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
