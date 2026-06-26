# Developer Blueprint & Implementation Specification: KCET 2026 College Predictor & Option Entry Optimizer

This specification delivers the full development blueprint for building a production-grade, high-concurrency college prediction and choice optimization portal for students appearing in the **KCET 2026** counselling cycle. This system relies on programmatic evaluation of historical KEA (Karnataka Examinations Authority) cutoffs, multi-dimensional reservation matrices, and a programmatic "Sandwich Strategy" sorting engine.

---

## 1. System Architecture & Tech Stack

The architecture is designed to handle extreme traffic spikes during the brief 72-hour windows when KEA opens option entry. The backend must minimize processing overhead per request, leveraging pre-indexed database queries and in-memory caches.

```
       [ Client Browser (Next.js 14 SPA / Zustand State) ]
                                |
                                | (HTTPS REST / JSON)
                                v
               [ Reverse Proxy & Rate Limiter (Nginx) ]
                                |
                                v
             [ Backend Application Server (FastAPI / Python) ]
                    |                               |
                    | (Read-Only Cutoffs)           | (In-Memory Hot Data)
                    v                               v
         [ Database (PostgreSQL 16) ]      [ Cache Store (Redis) ]
```

### 1.1 Core Stack Componentry
*   **Frontend Framework:** Next.js 14 (App Router) using TypeScript. Styled with TailwindCSS and UI primitives from Shadcn UI.
*   **State Management:** Zustand with the `persist` middleware to save multi-choice arrays directly to the client's local storage, preventing data loss during network dropouts.
*   **Backend Framework:** FastAPI (Python 3.11+). Leverages asynchronous concurrency (`async/await`) and integrates natively with data handling packages (`Pandas`, `NumPy`, `Pydantic`).
*   **Database Engine:** PostgreSQL 16. Utilizes composite B-Tree indexes across multi-dimensional criteria (College, Course, Category, Round).
*   **Caching Layer:** Redis. Caches static lookup matrices (e.g., complete list of 2025 cutoff data structured by category) to bypass database calls entirely during runtime computations.

---

## 2. Database Schema (DDL) & Data Model

The PostgreSQL schema must be normalized to prevent redundancy, while storing cutoff metrics explicitly to allow rapid range scans. Run the following DDL script to initialize the persistence layer:

```sql
-- Enable UUID extension if required for secure session tracking
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Colleges Master Table
CREATE TABLE colleges (
    college_code VARCHAR(10) PRIMARY KEY, -- e.g., 'E005', 'E033'
    college_name VARCHAR(255) NOT NULL,
    location VARCHAR(100) NOT NULL,       -- Normalized city/district names
    college_type VARCHAR(50) NOT NULL,    -- 'Government', 'Aided', 'Private-Unaided', 'University'
    status ACTIVE BOOLEAN DEFAULT TRUE
);

-- 2. Courses Master Table
CREATE TABLE courses (
    course_code VARCHAR(10) PRIMARY KEY, -- e.g., 'CS', 'IS', 'EC', 'AI', 'DS'
    course_name VARCHAR(255) NOT NULL,
    stream_group VARCHAR(50) NOT NULL    -- 'Engineering', 'Architecture', 'Farm-Science'
);

-- 3. Multi-Round Historical Cutoffs Matrix (2025 Reference Data)
CREATE TABLE cutoffs_2025 (
    id SERIAL PRIMARY KEY,
    college_code VARCHAR(10) REFERENCES colleges(college_code) ON DELETE CASCADE,
    course_code VARCHAR(10) REFERENCES courses(course_code) ON DELETE CASCADE,
    category VARCHAR(15) NOT NULL,       -- e.g., 'GM', '2AR', '3BK', 'SCG', 'STK', 'GMEWS'
    round_no INT NOT NULL,               -- 1 (Round 1), 2 (Round 2), 3 (Second Extended Round)
    cutoff_rank INT NOT NULL,
    CONSTRAINT uniq_cutoff_node UNIQUE (college_code, course_code, category, round_no)
);

-- 4. Database Optimization Indexes
CREATE INDEX idx_cutoff_lookup ON cutoffs_2025 (category, cutoff_rank);
CREATE INDEX idx_college_location ON colleges (location);
CREATE INDEX idx_cutoff_composite_search ON cutoffs_2025 (category, round_no, cutoff_rank ASC);
```

---

## 3. Core Algorithmic Engines

The platform requires two fundamental engines: a **Chancing Engine** to compute statistical probabilities and an **Optimization Engine** to generate structured choice lists.

### 3.1 The Chancing Engine (Probability Classifier)
The backend calculates a numerical variance ratio by comparing the student's rank against historical trends, factoring in volatility buffers for subsequent rounds.

$$	ext{Variance Ratio } (\phi) = rac{R_{	ext{student}}}{C_{2025} 	imes eta_{	ext{round}}}$$

Where:
*   $R_{	ext{student}}$ is the candidate's verified rank.
*   $C_{2025}$ is the raw historical cutoff rank.
*   $eta_{	ext{round}}$ is the historical mobility multiplier ($	ext{Round 1} = 1.00$, $	ext{Round 2} = 1.05$, $	ext{Round 3} = 1.12$).

#### Python Core Implementation Block:
```python
from pydantic import BaseModel
from typing import Dict, Literal

class StudentProfile(BaseModel):
    rank: int
    category: str
    preferred_locations: list[str]
    preferred_streams: list[str]

class PredictionNode(BaseModel):
    college_code: str
    college_name: str
    course_code: str
    location: str
    round_probabilities: Dict[int, Literal["High", "Medium", "Low", "Unlikely"]]
    base_cutoff: int

def evaluate_chancing_logic(student_rank: int, cutoff_2025: int, round_no: int) -> str:
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
```

### 3.2 The 100 Option Entry Sandwich Optimizer
To guarantee maximum protection for the student, choices must be laid out in a cascading order of risk. This ensures students do not risk missing out on a seat by only listing top-tier options, while still keeping them in running for higher-preference positions if cutoffs drop.

```python
def generate_optimized_100_list(profile: StudentProfile, cutoff_dataset: list[dict]) -> list[dict]:
    """
    Processes a list of valid choices and generates an ordered list of 100 choices 
    based on the systematic Sandwich Strategy.
    """
    dream_pool = []    # High risk / High reward (Ratio < 0.95)
    target_pool = []   # Realistic targets (Ratio 0.95 to 1.15)
    safety_pool = []   # Failure safeguards (Ratio > 1.15)
    
    for item in cutoff_dataset:
        # Evaluate using Round 2 data as the realistic pricing benchmark
        r2_cutoff = item["round_2_cutoff"]
        ratio = profile.rank / r2_cutoff
        
        node = {
            "college_code": item["college_code"],
            "college_name": item["college_name"],
            "course_code": item["course_code"],
            "location": item["location"],
            "chancing": {
                "round_1": evaluate_chancing_logic(profile.rank, item["round_1_cutoff"], 1),
                "round_2": evaluate_chancing_logic(profile.rank, item["round_2_cutoff"], 2),
                "round_3": evaluate_chancing_logic(profile.rank, item["round_3_cutoff"], 3)
            }
        }
        
        if ratio < 0.95:
            dream_pool.append(node)
        elif 0.95 <= ratio <= 1.15:
            target_pool.append(node)
        else:
            safety_pool.append(node)
            
    # Sort pools internally by academic preference & popularity metrics
    dream_pool.sort(key=lambda x: x["college_code"]) 
    target_pool.sort(key=lambda x: x["college_code"])
    safety_pool.sort(key=lambda x: x["college_code"])
    
    # Slice arrays based on the 20-50-30 distribution model
    final_sequence = dream_pool[:20] + target_pool[:50] + safety_pool[:30]
    
    # Enforce priority indices
    for idx, choice in enumerate(final_sequence):
        choice["priority_number"] = idx + 1
        
    return final_sequence[:100]
```

---

## 4. Frontend State Engineering (Zustand Specification)

The front-end must maintain a performant client-side state machine. This enables smooth drag-and-drop interactions and instant UI updates when a user re-orders options on their choice worksheet.

```typescript
import create from 'zustand';
import { persist } from 'zustand/middleware';

interface ChoiceNode {
  priorityNumber: number;
  collegeCode: string;
  courseCode: string;
  collegeName: string;
  chancing: { round1: string; round2: string; round3: string; };
}

interface OptionEntryState {
  choices: ChoiceNode[];
  addChoice: (node: Omit<ChoiceNode, 'priorityNumber'>) => void;
  removeChoice: (collegeCode: string, courseCode: string) => void;
  reorderChoices: (startIndex: number, endIndex: number) => void;
  clearList: () => void;
}

export const useOptionEntryStore = create<OptionEntryState>()(
  persist(
    (set) => ({
      choices: [],
      addChoice: (node) => set((state) => {
        if (state.choices.some(c => c.collegeCode === node.collegeCode && c.courseCode === node.courseCode)) {
          return state; // Block duplicate entries
        }
        const updated = [...state.choices, { ...node, priorityNumber: state.choices.length + 1 }];
        return { choices: updated };
      }),
      removeChoice: (collegeCode, courseCode) => set((state) => {
        const filtered = state.choices.filter(c => !(c.collegeCode === collegeCode && c.courseCode === courseCode));
        const reindexed = filtered.map((c, index) => ({ ...c, priorityNumber: index + 1 }));
        return { choices: reindexed };
      }),
      reorderChoices: (startIndex, endIndex) => set((state) => {
        const result = Array.from(state.choices);
        const [removed] = result.splice(startIndex, 1);
        result.splice(endIndex, 0, removed);
        const reindexed = result.map((c, index) => ({ ...c, priorityNumber: index + 1 }));
        return { choices: reindexed };
      }),
      clearList: () => set({ choices: [] })
    }),
    { name: 'kcet-2026-choice-workspace' }
  )
);
```

---

## 5. End-to-End Execution Flow

1. **User Profiling:** The student enters their rank, category, and preferences into the UI.
2. **Backend Query Processing:** FastAPI runs an optimized `SELECT` query against `cutoffs_2025` using the combined category mapping (e.g., `3A` + `Rural` $ightarrow$ `3AR`).
3. **Array Classification:** The database payload returns to the backend, where the `generate_optimized_100_list` script segments entries into Dream, Target, and Safety pools.
4. **Hydration & Interactivity:** The frontend hydrates the Zustand engine with the computed top 100 choices. This enables zero-latency manual adjustments via drag-and-drop.
5. **Data Export:** The finalized sequence exports cleanly to a structured CSV file, ready for data entry into the official KEA portal.
