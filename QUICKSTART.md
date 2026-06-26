# 🚀 KCET 2026 Portal - Quick Start Guide

## Option 1: Docker (Recommended for Quick Setup)

### Prerequisites
- Docker and Docker Compose installed

### Setup

```bash
# 1. Clone/navigate to project directory
cd KCET-Predictor

# 2. Start all services
docker-compose up -d

# 3. Wait for services to be ready (about 30 seconds)
docker-compose logs -f

# 4. Access the portal
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Stop Services
```bash
docker-compose down
```

---

## Option 2: Local Development Setup

### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env with your database credentials

# 5. Start server
python main.py
# Server runs on http://localhost:8000
```

### Frontend Setup (New Terminal)

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Create .env.local file
cp .env.local.example .env.local

# 4. Start development server
npm run dev
# Frontend runs on http://localhost:3000
```

### Database Setup (PostgreSQL)

```bash
# 1. Create database
psql -U postgres -c "CREATE DATABASE kcet_2026;"

# 2. Initialize schema
psql -U postgres -d kcet_2026 -f ../database/schema.sql

# 3. Verify
psql -U postgres -d kcet_2026 -c "SELECT count(*) FROM colleges;"
```

---

## Testing the Portal

### 1. Check Backend Health
```bash
curl http://localhost:8000/
# Should return: {"status":"online","service":"KCET 2026 Portal",...}
```

### 2. Get Available Categories
```bash
curl http://localhost:8000/api/categories
```

### 3. Generate Predictions
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "rank": 5000,
    "category": "GM",
    "preferred_locations": ["Bangalore"],
    "preferred_streams": ["Engineering"]
  }'
```

### 4. Access Frontend
Open http://localhost:3000 in your browser

---

## Troubleshooting

### Database Connection Failed
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start PostgreSQL if not running
sudo systemctl start postgresql

# Test connection
psql -U postgres -d kcet_2026 -c "SELECT 1;"
```

### Port Already in Use
```bash
# Change port in backend (main.py)
# Change port in docker-compose.yml or .env file

# Or kill existing process
# Windows: netstat -ano | findstr :8000
# Linux/Mac: lsof -i :8000 && kill -9 <PID>
```

### Frontend API Errors
```bash
# Verify API is running
curl http://localhost:8000/api/health

# Check NEXT_PUBLIC_API_URL in .env.local
# Should be: http://localhost:8000/api
```

---

## Next Steps

1. ✅ System is running
2. 📝 Enter your rank and category in the Predictor
3. 🎯 Review predicted colleges
4. 📊 Build your choice list by adding colleges
5. 📥 Reorder using drag-and-drop
6. 💾 Export to CSV when ready

---

## Portal Features

### 🏠 Home Page
- Overview of system features
- Quick start instructions

### 🎯 Predictor Page
- Student profile form
- Generates 100 optimized choices
- Real-time probability assessment

### 📋 My Choices Page
- Manage your college list
- Drag-and-drop reordering
- Export to CSV

---

## Key Algorithms

### Variance Ratio Formula
```
Ratio = Student Rank / (Cutoff Rank × Round Multiplier)
- Round 1: 1.00x multiplier
- Round 2: 1.05x multiplier  
- Round 3: 1.12x multiplier
```

### Sandwich Strategy (20-50-30)
- **20 Dream Options**: Ratio < 0.95 (High risk/reward)
- **50 Target Options**: Ratio 0.95-1.15 (Realistic)
- **30 Safety Options**: Ratio > 1.15 (Protection)

---

## Performance Notes

- Backend: ~200ms response time per prediction
- Database: Indexed queries for instant lookups
- Frontend: Instant UI updates with Zustand state
- Browser: Data persisted in localStorage

---

## File Structure

```
KCET-Predictor/
├── backend/              # FastAPI application
│   ├── main.py          # FastAPI app
│   ├── algorithms.py    # Prediction logic
│   └── database.py      # Database models
├── frontend/            # Next.js application
│   ├── src/app/         # Pages
│   ├── src/components/  # React components
│   └── src/store/       # Zustand store
├── database/            # PostgreSQL schema
└── docker-compose.yml   # Container orchestration
```

---

## Production Deployment

```bash
# Build Docker images
docker-compose build

# Deploy to server
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs <service>`
2. Verify database connection
3. Check environment variables
4. Review error messages in browser console

---

**Happy predicting! 🎓**
