# CET-2025 Cutoff Data Integration - Setup Guide

## Overview
This guide documents the integration of CET-2025 (admission year 2026-27) cutoff data from the official K.E.A. PDF into the KCET-2026 Predictor database.

## What Was Done

### 1. Data Extraction ✅
- **Source**: CET-2025 General Cutoff Ranks PDF (Pages 21-40)
- **Colleges Imported**: 2 (E064, E065 as examples)
- **Courses per College**: 8-10 engineering disciplines
- **Categories Covered**: 1G, 2AG, 2BG, 3AG, 3BG, GM, SCG, STG
- **Rounds**: Round I and Round II cutoff data
- **Total Records**: 254 cutoff entries

### 2. Data Structure

#### College Information
```
College Code (E064)
├── Name: Adhichunchanagiri Institute of Technology
├── Location: Chikmagalur
├── Type: PUA (Private Unaided)
└── University: VTU
```

#### Course Information
```
Course (AI - Artificial Intelligence & Machine Learning)
├── Intake: 27 seats
├── Stream: Engineering
└── Cutoffs by Category & Round
    ├── 1G Round I: 58912
    ├── 1G Round II: 63801
    ├── 2AG Round I: 59451
    └── ... (8 categories × 2 rounds = 16 cutoff values)
```

#### Database Schema
```sql
colleges (college_code PRIMARY KEY)
├── college_name
├── location
├── college_type
└── status

courses (course_code PRIMARY KEY)
├── course_name
└── stream_group

cutoffs_2025 (id PRIMARY KEY)
├── college_code (FK → colleges)
├── course_code (FK → courses)
├── category (1G, 2AG, 2BG, 3AG, 3BG, GM, SCG, STG)
├── round_no (1 or 2)
└── cutoff_rank (integer)
```

## Accessing the Data

### Backend API Endpoints

#### 1. Get All Categories
```bash
curl http://localhost:8000/api/categories

Response:
{
  "status": "success",
  "count": 8,
  "categories": ["1G", "2AG", "2BG", "3AG", "3BG", "GM", "SCG", "STG"]
}
```

#### 2. Get All Colleges
```bash
curl http://localhost:8000/api/colleges

Response:
{
  "status": "success",
  "count": 2,
  "colleges": [
    {
      "college_code": "E064",
      "college_name": "Adhichunchanagiri Institute of Technology",
      "location": "Chikmagalur",
      "college_type": "PUA"
    },
    ...
  ]
}
```

#### 3. Get All Courses
```bash
curl http://localhost:8000/api/courses

Response:
{
  "status": "success",
  "count": 10,
  "courses": [
    {
      "course_code": "AI",
      "course_name": "ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",
      "stream_group": "Engineering"
    },
    ...
  ]
}
```

#### 4. Predict Colleges for a Student
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "rank": 50000,
    "category": "GM",
    "preferred_locations": ["Bangalore", "Mysore"],
    "preferred_streams": ["Engineering"]
  }'

Response:
{
  "status": "success",
  "student_rank": 50000,
  "category": "GM",
  "total_matches": 2,
  "total_choices": 100,
  "dream_count": 25,
  "target_count": 50,
  "safety_count": 25,
  "choices": [
    {
      "choice_number": 1,
      "college_code": "E064",
      "college_name": "Adhichunchanagiri Institute of Technology",
      "course_code": "AI",
      "course_name": "ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",
      "cutoff_rank": 42330,
      "probability": "Dream",
      "reason": "Strong match with significant rank difference"
    },
    ...
  ]
}
```

## Running the System

### 1. Start the Backend
```bash
cd backend
python main.py
# Server runs on http://localhost:8000
```

### 2. Start the Frontend (in another terminal)
```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:3000
```

### 3. Import Additional Data (if needed)
```bash
cd backend

# To import more colleges from PDF:
python run_import.py

# To view extracted data:
python extract_pdf_data.py
```

## Data Files

### Backend
- `database.py` - SQLAlchemy models and database connection
- `import_pdf_cutoffs.py` - PDF data import functions (template)
- `extract_pdf_data.py` - PDF data extraction and flattening
- `run_import.py` - Master import script
- `main.py` - FastAPI server
- `models.py` - Pydantic models for API
- `algorithms.py` - Prediction algorithms
- `kcet_2026.db` - SQLite database (generated)

### Frontend
- `src/app/page.tsx` - Home page
- `src/app/predictor/page.tsx` - Prediction page
- `src/components/StudentProfileForm.tsx` - Student input form
- `src/components/PredictionResults.tsx` - Results display
- `src/services/api.ts` - Backend API calls

## Integration Notes

### Categories Explained
- **1G (1st General)**: Open category, all merit
- **2AG (2nd A General)**: Backward class category
- **2BG (2nd B General)**: Backward class category
- **3AG (3rd A General)**: Most backward class category
- **3BG (3rd B General)**: Most backward class category
- **GM (General - Merit)**: Merit based for general category
- **SCG (SC General)**: Scheduled Caste candidates
- **STG (ST General)**: Scheduled Tribe candidates

### Prediction Algorithm (Sandwich Strategy)
1. **Dream Tier (25%)**: Colleges with cutoff >> student rank
2. **Target Tier (50%)**: Colleges with cutoff ≈ student rank
3. **Safety Tier (25%)**: Colleges with cutoff << student rank

### Probability Calculation
```
Probability = 1 - ((cutoff_rank - student_rank) / cutoff_rank)
If Probability > 0.8: Very Likely
If Probability > 0.5: Likely
If Probability > 0.2: Possible
If Probability ≤ 0.2: Safety
```

## Future Enhancements

### To Import Full Dataset
1. Scan remaining PDF pages (41-82)
2. Extract all 101 colleges
3. Parse all course combinations
4. Validate and clean data
5. Run comprehensive import

### To Extend Functionality
1. Add filter by engineering branch
2. Add city preferences with distance calculation
3. Add college fee structure comparison
4. Add placement statistics
5. Add year-on-year rank trends
6. Add college ranking comparisons
7. Add student reviews/ratings integration

## Troubleshooting

### Backend Won't Start
```bash
# Check if port 8000 is in use
netstat -ano | findstr ":8000"

# Kill the process using port 8000
taskkill /F /PID <PID>
```

### Database Issues
```bash
# Reset database (WARNING: deletes all data)
rm backend/kcet_2026.db

# Reimport data
python backend/run_import.py
```

### API Returns 404
- Verify backend is running on http://localhost:8000
- Check /api/categories returns data
- Verify database import was successful

## Support & Maintenance

### Data Updates
- Update source PDF annually
- Run import script after each K.E.A. announcement
- Validate data with official cutoff lists
- Archive previous year's data

### Monitoring
- Track API response times
- Monitor database size
- Log all predictions for analysis
- Validate prediction accuracy post-counselling

---

**Last Updated**: 2026-06-24  
**Data Version**: CET-2025 (2026-27 Admission)  
**Total Imported**: 254 cutoff records from 2 colleges, 10 courses
