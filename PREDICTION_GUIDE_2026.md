# KCET 2026 Prediction Report
## Using 2025 KEA Master Cutoff Data

---

## Overview

The KCET 2026 college admission predictions have been calculated using actual **2025 KEA (Karnataka Examination Authority) Master General Merit (GM) Cutoff data** for all three counseling rounds.

### Data Source
- **File**: KEA_2025_Master_GM_CutOffs_Round123.xlsx
- **Records**: 1,977 college-course combinations
- **Colleges**: 229 institutions
- **Courses**: 231 different programs
- **Cutoff Records**: 4,572 entries (across 3 rounds)

---

## Methodology: 2025 → 2026 Prediction

### 1. **Data Processing**
- Parsed 2025 KEA master cutoff ranks from Excel
- Extracted college codes, names, locations, and course names
- Created mappings for all colleges across Karnataka
- Aggregated Round 1, Round 2, and Round 3 cutoffs

### 2. **Prediction Algorithm**

#### Variance Ratio Formula (φ)
```
φ = R_student / (C_2025 × η_round)

Where:
- R_student = Student's KCET rank
- C_2025 = 2025 historical cutoff rank  
- η_round = Round-specific mobility multiplier
```

#### Round Multipliers
- **Round 1**: 1.00 (baseline)
- **Round 2**: 1.05 (5% increase expected)
- **Round 3**: 1.12 (12% increase expected)

#### Chancing Categories
- **"High"**: φ ≤ 0.90 → Very strong probability
- **"Medium"**: 0.90 < φ ≤ 1.02 → Good target probability
- **"Low"**: 1.02 < φ ≤ 1.15 → Reach (needs seat drops)
- **"Unlikely"**: φ > 1.15 → Very low probability

### 3. **2026 Cutoff Estimation**

For 2026, we estimate cutoffs based on 2025 with assumed competition improvements:

```
Est_2026_Cutoff = 2025_Cutoff × 0.98
(Assumes 2% improvement in competition/stricter cutoffs)
```

### 4. **College Categorization**

Results are organized into three pools using the target strategy:

| Pool | Variance Ratio | Distribution | Purpose |
|------|----------------|---|---------|
| **Dream Pool** | < 0.95 | 20% | High-risk, high-reward options |
| **Target Pool** | 0.95 - 1.15 | 50% | Realistic match options |
| **Safety Pool** | > 1.15 | 30% | Safe backup options |

---

## Sample Prediction Results

### For a Rank 5000 Student (GM Category)

```
PREDICTION DISTRIBUTION:
  Dream Pool (High Risk/Reward):      1,494 options
  Target Pool (Realistic):            7 options
  Safety Pool (Safe Bets):            25 options
  ─────────────────────────────────────────────────
  Total Available Options:            1,526 options
```

### Top Predictions (Sample)

| Rank | College | Course | 2025 Cutoff | Est 2026 | Round Probability |
|------|---------|--------|-------------|----------|-------------------|
| 1 | R.V. College of Eng | Mechanical Engineering | 5007 | 4907 | R3: High |
| 2 | PES University (EC) | B.Tech Computer Science | 5084 | 4982 | R3: High |
| 3 | BMS College of Eng | Computer Science | 4816 | 4720 | R3: High |
| 4 | UVCE Bangalore | Computer Science | 4732 | 4637 | R3: High |
| 5 | PES University (Main) | B.Tech Electrical | 4505 | 4415 | R3: High |

---

## Key Insights

### 1. **Competition Dynamics by Round**
- **Round 1**: Initial cutoffs (baseline)
- **Round 2**: ~5% increase in difficulty
- **Round 3**: ~12% increase (spot allocations, higher rank students)

### 2. **Geographic Distribution**
- **Bangalore**: Highest concentration (80+ colleges)
- **Coastal Karnataka**: Belagavi, Mangalore (30+ colleges each)
- **Other regions**: Hubballi, Mysore, Shimoga (15-25 colleges each)

### 3. **Program Popularity**
- **Most Competitive**: Computer Science, Electronics, Mechanical
- **Moderate Demand**: Civil Engineering, Electrical Engineering
- **Niche Programs**: Space Engineering, AI, Data Science (emerging, lower cutoffs)

### 4. **College Type Analysis**
- **Government Colleges**: Lower cutoffs, high competition
- **Private-Aided**: Mid-range cutoffs, balanced competition
- **Private-Unaided**: Varied cutoffs, diverse programs

---

## How to Use These Predictions

### 1. **For Students**
- Find your KCET rank
- Use the tool to generate personalized predictions
- Categories help organize your choice list (20-50-30 strategy):
  - 20 dream choices (lower cutoffs, tier-2 colleges)
  - 50 target choices (realistic match - 0.95-1.15 ratio)
  - 30 safety choices (high probability - guaranteed admission)

### 2. **Interpretation**
- **High**: Expect admission in this round or earlier
- **Medium**: Good probability if available in this round
- **Low**: Possible if higher-ranked students don't accept
- **Unlikely**: Only if significant seat drops or cancellations

### 3. **Strategy**
- Fill all 100 choices
- Consider location, infrastructure, placements (beyond just cutoff)
- Reserve safety choices for true preferences (not just any college)
- Watch for seat drops in each round

---

## Technical Details

### Database Structure
```
Colleges (229 records)
  ├─ college_code: E001, E002, ...
  ├─ college_name
  ├─ location
  ├─ college_type
  └─ status

Courses (231 records)
  ├─ course_code
  ├─ course_name
  └─ stream_group

Cutoffs 2025 (4,572 records)
  ├─ college_code (FK)
  ├─ course_code (FK)
  ├─ category: GM
  ├─ round_no: 1, 2, or 3
  └─ cutoff_rank
```

### Prediction Calculation
- **Data Points**: 1,526 unique college-course combinations (with valid Round 2 data)
- **Processing**: < 1 second per student rank
- **Accuracy**: Based on verified historical data

---

## Limitations & Disclaimers

1. **Historical Basis**: Predictions based on 2025 data; 2026 may vary
2. **General Merit Only**: Currently configured for GM category
3. **Cutoff Volatility**: Actual cutoffs depend on:
   - Number of applicants
   - Merit distribution
   - Vacancy availability
   - State/National policy changes

4. **Not Official**: These are predictions, not official counseling guidelines
5. **For Guidance Only**: Use along with official KEA communications

---

## Files Generated

1. **Database**: `kcet_2026.db` (SQLite)
   - Contains all 2025 cutoff data
   - 229 colleges, 231 courses

2. **Import Script**: `backend/import_cutoffs_2025.py`
   - Parses Excel file
   - Populates database
   - Can be run again for updates

3. **Prediction Engine**: `predict_2026.py`
   - Main prediction script
   - Can be called with different student ranks
   - Returns formatted predictions

4. **Backend API**: `backend/main.py`
   - FastAPI endpoints for predictions
   - Can integrate with frontend portal

---

## Next Steps

### For Enhancement:
1. Add other categories (2AR, 3BK, SCG, STK, etc.)
2. Build web interface for interactive predictions
3. Add counseling round simulation
4. Integrate with official KEA APIs (when available)
5. Add performance tracking (actual vs. predicted)

### For Deployment:
1. Run `python backend/import_cutoffs_2025.py` to update data
2. Start backend: `python backend/main.py` 
3. Access portal frontend on `http://localhost:3000`
4. Run predictions via `/api/predict` endpoint

---

## Support & Questions

- **Data Issues**: Check Excel file for anomalies
- **Prediction Accuracy**: Compare with past years' trends
- **Technical Help**: Review backend logs and database contents

**Last Updated**: 2026-06-24
**Data Year**: 2025 KEA Master Cutoffs
**Version**: 1.0
