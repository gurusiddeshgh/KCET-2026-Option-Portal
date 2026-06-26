# KCET 2026 Portal - Complete Setup Guide

## Project Overview

This is a production-grade college prediction and choice optimization portal for KCET 2026 counselling cycle. The system uses historical cutoff analysis and a "Sandwich Strategy" algorithm to generate optimized college choice lists.

### Technology Stack

- **Frontend**: Next.js 14 with TypeScript, TailwindCSS, Zustand
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 16
- **Cache**: Redis (optional, for production)
- **Deployment**: Docker (optional)

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 16
- Git

---

## Backend Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Database

Create a `.env` file in the backend folder:

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/kcet_2026
ENVIRONMENT=development
DEBUG=True
```

### 4. Initialize Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE kcet_2026;

# Exit psql
\q

# Run schema initialization
psql -U postgres -d kcet_2026 -f ../database/schema.sql
```

### 5. Run Backend Server

```bash
python main.py
```

The FastAPI server will start at `http://localhost:8000`

**Available Endpoints:**
- `GET /` - Health check
- `GET /api/categories` - List all student categories
- `GET /api/colleges` - List all colleges
- `GET /api/courses` - List all courses
- `POST /api/predict` - Generate predictions
- `POST /api/evaluate-chance` - Evaluate single option chance
- `GET /api/health` - Health status

---

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### 3. Run Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
npm start
```

---

## Project Structure

```
KCET-Predictor/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── models.py               # Pydantic models
│   ├── algorithms.py           # Prediction algorithms
│   ├── database.py             # Database connection & models
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment template
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx        # Home page
│   │   │   ├── predictor/      # Predictor page
│   │   │   ├── choices/        # My Choices page
│   │   │   ├── layout.tsx      # Root layout
│   │   │   └── globals.css     # Global styles
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── StudentProfileForm.tsx
│   │   │   ├── PredictionResults.tsx
│   │   │   └── ChoiceList.tsx
│   │   ├── store/
│   │   │   └── optionEntry.ts  # Zustand store
│   │   └── services/
│   │       └── api.ts          # API client
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── .env.local.example
│
├── database/
│   └── schema.sql              # PostgreSQL DDL
│
├── kcet_2026_portal_blueprint.md  # Original blueprint
└── README.md
```

---

## Core Algorithms

### Chancing Engine

The system evaluates probability using the Variance Ratio formula:

$$\text{Variance Ratio} = \frac{R_{\text{student}}}{C_{2025} \times \eta_{\text{round}}}$$

**Ratings:**
- **High**: Ratio ≤ 0.90 (Deeply safe)
- **Medium**: 0.90 < Ratio ≤ 1.02 (Target boundary)
- **Low**: 1.02 < Ratio ≤ 1.15 (Reach, needs drops)
- **Unlikely**: Ratio > 1.15 (Extreme stretch)

### Sandwich Strategy (20-50-30)

Choices are distributed across risk categories:
1. **Dream Pool** (< 0.95 ratio): 20 options - High risk/reward
2. **Target Pool** (0.95-1.15 ratio): 50 options - Realistic
3. **Safety Pool** (> 1.15 ratio): 30 options - Safeguards

---

## API Request/Response Examples

### Get Predictions

**Request:**
```bash
POST http://localhost:8000/api/predict
Content-Type: application/json

{
  "rank": 5000,
  "category": "GM",
  "preferred_locations": ["Bangalore", "Belagavi"],
  "preferred_streams": ["Engineering"]
}
```

**Response:**
```json
{
  "status": "success",
  "student_rank": 5000,
  "category": "GM",
  "total_matches": 150,
  "total_choices": 100,
  "dream_count": 20,
  "target_count": 50,
  "safety_count": 30,
  "choices": [
    {
      "priority_number": 1,
      "college_code": "E006",
      "college_name": "NIT Karnataka",
      "course_code": "CS",
      "course_name": "Computer Science",
      "location": "Surathkal",
      "chancing": {
        "round_1": "High",
        "round_2": "High",
        "round_3": "Medium"
      }
    }
    // ... 99 more choices
  ]
}
```

---

## Frontend Features

### Student Profile Form
- Enter rank and category
- Select preferred locations
- Trigger prediction generation

### Prediction Results
- View all 100 predicted options
- See probability for each round
- Add options to personal list

### My Choices Page
- Drag-and-drop reordering
- Remove selections
- Export to CSV

---

## Data Export

The system exports choices as CSV in the following format:

```csv
Priority,College Code,College Name,Course Code,Course Name,Location,Round 1 Chancing,Round 2 Chancing,Round 3 Chancing
1,E006,NIT Karnataka,CS,Computer Science,Surathkal,High,High,Medium
2,E003,RV College,CS,Computer Science,Bangalore,High,Medium,Medium
...
```

This CSV can be directly entered into the official KEA portal.

---

## Performance Considerations

### Concurrency
- FastAPI uses async/await for handling multiple requests
- Connection pooling configured (20 connections, 40 max overflow)
- Database indexes on frequently queried columns

### Caching Strategy
- Zustand persists choices to browser localStorage
- Prevents data loss during network dropouts
- Backend can be extended with Redis for cutoff caching

### Database Optimization
- B-Tree indexes on (category, round_no, cutoff_rank)
- Composite indexes for multi-dimensional searches
- Normalized schema to prevent redundancy

---

## Deployment

### Docker Deployment

1. **Build containers:**
```bash
docker-compose up -d
```

2. **Initialize database:**
```bash
docker-compose exec backend psql -U postgres -d kcet_2026 -f ../database/schema.sql
```

### Production Environment Variables

**Backend (.env):**
```env
DATABASE_URL=postgresql://user:password@prod-db:5432/kcet_2026
ENVIRONMENT=production
DEBUG=False
```

**Frontend (.env.production):**
```env
NEXT_PUBLIC_API_URL=https://api.kcet.example.com/api
```

---

## Troubleshooting

### Database Connection Errors
```bash
# Verify PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Check if database exists
psql -U postgres -l | grep kcet_2026

# Recreate if needed
dropdb -U postgres kcet_2026
createdb -U postgres kcet_2026
psql -U postgres -d kcet_2026 -f ../database/schema.sql
```

### Backend Won't Start
```bash
# Check Python version
python --version

# Verify virtual environment
python -m pip list | grep fastapi

# Run with verbose output
python -u main.py
```

### Frontend API Errors
```bash
# Check CORS is enabled
curl -H "Origin: http://localhost:3000" http://localhost:8000/

# Verify API endpoint
curl http://localhost:8000/api/health
```

---

## Future Enhancements

- Real-time cutoff updates from KEA
- Student performance analytics
- College comparison tools
- Interview scheduling integration
- Multi-language support
- Mobile app (React Native)
- Advanced filtering (GPA, entrance score, internships)

---

## Support & Contact

For issues or suggestions, please create an issue in the repository.

---

**Last Updated**: June 2026
**Version**: 1.0.0
