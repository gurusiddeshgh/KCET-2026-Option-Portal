# KCET-2026 Predictor - Quick Reference Card

## 🚀 Start System (2 Terminals)

### Terminal 1: Backend
```bash
cd c:\Personal\KCET-Predictor\backend
python main.py
```
✅ Should show: `INFO: Uvicorn running on http://0.0.0.0:8000`

### Terminal 2: Frontend  
```bash
cd c:\Personal\KCET-Predictor\frontend
npm run dev
```
✅ Should show: `▲ Local: http://localhost:3000`

---

## 🧪 Test API Endpoints (PowerShell)

### Check if Backend is Running
```powershell
(Invoke-RestMethod -Uri "http://localhost:8000/api/categories").count
# Should return: 8
```

### Get All Colleges (First 3)
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/colleges"
$response.colleges | Select-Object -First 3
```

### Predict for Student (Rank 15000, Category GM)
```powershell
$body = @{
    rank = 15000
    category = "GM"
    preferred_locations = @("Bangalore", "Mysore")
    preferred_streams = @("Engineering")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/predict" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

---

## 📊 System Status at a Glance

| Component | Status | Details |
|-----------|--------|---------|
| Backend | ✅ Running | http://localhost:8000 |
| Frontend | ⏳ Ready | http://localhost:3000 |
| Database | ✅ 56 colleges | 2500+ cutoff records |
| API Docs | ✅ Available | http://localhost:8000/docs |
| Data | ✅ Current | CET-2025 (2026-27 admission) |

---

## 🎯 Key API Endpoints

```
GET  /api/categories          → Student categories (8 total)
GET  /api/colleges            → Engineering colleges (56 total)
GET  /api/courses             → Engineering courses (100+ total)
POST /api/predict             → Generate college choice list
POST /api/evaluate-chance     → Calculate admission probability
POST /api/option-entry        → Optimize choice sequence
```

---

## 📁 Important Files & Directories

```
c:\Personal\KCET-Predictor\
├── backend/
│   ├── main.py                   ← Start here (FastAPI app)
│   ├── kcet_2026.db              ← Database (SQLite)
│   ├── extract_pdf_data.py       ← PDF data extraction
│   ├── run_import.py             ← Batch import script
│   └── requirements.txt           ← Python dependencies
│
├── frontend/
│   ├── src/app/page.tsx          ← Home page
│   ├── src/app/predictor/page.tsx ← Prediction page
│   └── package.json              ← Node dependencies
│
├── COMPLETE_SETUP_GUIDE.md       ← Full documentation
├── CUTOFF_DATA_INTEGRATION_GUIDE.md ← Data import guide
└── QUICK_REFERENCE.md            ← This file
```

---

## ⚡ Common Tasks

### Import CET-2025 Cutoff Data
```bash
cd backend
python run_import.py
```

### Test Prediction with Real Data
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"rank":15000,"category":"GM"}'
```

### Reset Database
```bash
# Delete and reimport
rm backend\kcet_2026.db
python backend\run_import.py
```

### Backup Database
```bash
copy backend\kcet_2026.db backup\kcet_2026_$(Get-Date -f 'yyyy-MM-dd').db
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 in use | `taskkill /F /PID <PID>` |
| Database locked | Delete `kcet_2026.db` and re-import |
| Frontend can't connect | Check backend running on port 8000 |
| API returns 500 error | Check backend terminal for error message |
| Node modules missing | Run `npm install` in frontend directory |

---

## 📈 Current Database Status

- **Total Colleges**: 56
- **Total Courses**: 100+
- **Total Cutoff Records**: 2500+
- **Database Size**: ~3 MB
- **Data Period**: CET-2025 (2026-27 admission)
- **Categories Covered**: 1G, 2AG, 2BG, 3AG, 3BG, GM, SCG, STG
- **Rounds Covered**: Round I & Round II

---

## 🎓 Understanding the Prediction

### Input
```json
{
  "rank": 15000,           // Your CET merit rank
  "category": "GM",         // Your category (1G, 2AG, etc.)
  "preferred_locations": ["Bangalore"],  // City preferences
  "preferred_streams": ["Engineering"]   // Course preferences
}
```

### Output
- **100 Optimized Choices** (college-course combinations)
- **Probability for Each** (likelihood of admission)
- **Risk Distribution** (25% Dream, 50% Target, 25% Safety)
- **College Details** (name, location, course info)

### Probability Scoring
- **> 80%**: Very Likely ✅ (Strong Chance)
- **50-80%**: Likely ⚠️ (Good Chance)
- **20-50%**: Possible 🤔 (Worth Trying)
- **< 20%**: Safety 🛡️ (Backup Option)

---

## 📞 When Something Goes Wrong

1. **Backend won't start?**
   - Check port 8000: `netstat -ano | findstr ":8000"`
   - Kill process: `taskkill /F /PID <PID>`
   - Restart: `python backend/main.py`

2. **API returning errors?**
   - Read error message in backend terminal
   - Check if database file exists: `ls backend/kcet_2026.db`
   - Verify database is initialized

3. **Frontend can't connect?**
   - Verify backend is running: `curl http://localhost:8000/api/categories`
   - Check network connectivity
   - Review browser console for CORS errors

4. **Data looks wrong?**
   - Verify source PDF data
   - Check database content: `SELECT COUNT(*) FROM cutoffs_2025`
   - Rerun import: `python backend/run_import.py`

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `COMPLETE_SETUP_GUIDE.md` | Full system setup and operations |
| `CUTOFF_DATA_INTEGRATION_GUIDE.md` | Data import and API usage |
| `PREDICTION_GUIDE_2026.md` | Prediction algorithm explanation |
| `CONFIG_GUIDE.md` | Configuration options |
| `QUICK_REFERENCE.md` | This quick reference card |
| `README.md` | Project overview |

---

## 🔗 Useful URLs

```
Backend API:        http://localhost:8000
API Documentation:  http://localhost:8000/docs
Frontend App:       http://localhost:3000
K.E.A. Website:     https://www.kea.kar.nic.in
CET Official:       https://cetonline.karnataka.gov.in
```

---

## ✅ Verification Checklist

Before using in production:

```
☑ Backend running on port 8000
☑ API /api/categories returns 8 results
☑ API /api/colleges returns 56+ results
☑ API /api/courses returns 100+ results
☑ Database backup created
☑ Frontend ready to start
☑ Network connectivity verified
☑ Error logs reviewed
```

---

**Last Updated**: June 24, 2026  
**Version**: 1.0.0  
**Status**: ✅ Production Ready

For detailed help, see `COMPLETE_SETUP_GUIDE.md`
