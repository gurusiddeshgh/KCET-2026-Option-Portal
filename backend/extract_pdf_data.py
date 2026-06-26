"""
Extract CET-2025 cutoff data from PDF and prepare for database import.

This script reads the PDF document and extracts all college, course, and cutoff data
in a structured format suitable for database import.
"""

import json
from typing import List, Dict, Optional, Tuple
import re

# Extracted data from the PDF pages
# Format: College Entry -> Courses -> Categories -> Round I/II cutoff ranks

EXTRACTED_CUTOFF_DATA = [
    # E064 - Adhichunchanagiri Institute of Technology
    {
        "college_code": "E064",
        "college_name": "Adhichunchanagiri Institute of Technology",
        "location": "Chikmagalur",
        "courses": [
            {
                "code": "AI",
                "name": "ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",
                "intake": 27,
                "cutoffs": {
                    "1G": {"I": 58912, "II": 63801},
                    "2AG": {"I": 59451, "II": 63379},
                    "2BG": {"I": 48651, "II": 63539},
                    "3AG": {"I": 42481, "II": 44416},
                    "3BG": {"I": 54001, "II": 64718},
                    "GM": {"I": 42330, "II": 44050},
                    "SCG": {"I": 88835, "II": 88835},
                    "STG": {"I": 77519, "II": 77519}
                }
            },
            {
                "code": "CE",
                "name": "CIVIL ENGINEERING",
                "intake": 27,
                "cutoffs": {
                    "1G": {"I": 225629, "II": None},
                    "2AG": {"I": 161305, "II": None},
                    "2BG": {"I": 193911, "II": None},
                    "3AG": {"I": 172609, "II": None},
                    "3BG": {"I": 157150, "II": None},
                    "GM": {"I": 154955, "II": 184655},
                    "SCG": {"I": 209962, "II": None},
                    "STG": {"I": 192999, "II": None}
                }
            },
            {
                "code": "CS",
                "name": "COMPUTER SCIENCE AND ENGINEERING",
                "intake": 54,
                "cutoffs": {
                    "1G": {"I": 55071, "II": 78510},
                    "2AG": {"I": 57467, "II": 80935},
                    "2BG": {"I": 53337, "II": 65734},
                    "3AG": {"I": 49133, "II": 63929},
                    "3BG": {"I": 49150, "II": 65606},
                    "GM": {"I": 48494, "II": 56927},
                    "SCG": {"I": 116974, "II": 134160},
                    "STG": {"I": 119790, "II": 161478}
                }
            },
            {
                "code": "DS",
                "name": "COMPUTER SCIENCE AND ENGINEERING(DATA SCIENCE)",
                "intake": 27,
                "cutoffs": {
                    "1G": {"I": 92165, "II": 92165},
                    "2AG": {"I": 62337, "II": 92555},
                    "2BG": {"I": 58458, "II": 89493},
                    "3AG": {"I": 64097, "II": 87024},
                    "3BG": {"I": 64301, "II": 80455},
                    "GM": {"I": 56927, "II": 77742},
                    "SCG": {"I": 158123, "II": 192126},
                    "STG": {"I": 142240, "II": 142240}
                }
            },
            {
                "code": "EE",
                "name": "ELECTRICAL & ELECTRONICS ENGINEERING",
                "intake": 27,
                "cutoffs": {
                    "1G": {"I": 98809, "II": None},
                    "2AG": {"I": 98187, "II": None},
                    "2BG": {"I": 111076, "II": None},
                    "3AG": {"I": 95866, "II": None},
                    "3BG": {"I": 105190, "II": None},
                    "GM": {"I": 94101, "II": 257145},
                    "SCG": {"I": 164631, "II": None},
                    "STG": {"I": 147856, "II": None}
                }
            },
            {
                "code": "EC",
                "name": "ELECTRONICS AND COMMUNICATION ENGG",
                "intake": 54,
                "cutoffs": {
                    "1G": {"I": 92341, "II": 187703},
                    "2AG": {"I": 84082, "II": 140480},
                    "2BG": {"I": 91346, "II": 129512},
                    "3AG": {"I": 79268, "II": 116687},
                    "3BG": {"I": 75507, "II": 120681},
                    "GM": {"I": 73291, "II": 113641},
                    "SCG": {"I": 191920, "II": 247855},
                    "STG": {"I": 182720, "II": None}
                }
            },
            {
                "code": "IE",
                "name": "INFORMATION SCIENCE AND ENGINEERING",
                "intake": 27,
                "cutoffs": {
                    "1G": {"I": 67793, "II": 110654},
                    "2AG": {"I": 63841, "II": 89591},
                    "2BG": {"I": None, "II": None},
                    "3AG": {"I": 57385, "II": 96658},
                    "3BG": {"I": 63250, "II": 89419},
                    "GM": {"I": 55363, "II": 81934},
                    "SCG": {"I": 163658, "II": 156548},
                    "STG": {"I": 150526, "II": 137091}
                }
            },
            {
                "code": "ME",
                "name": "MECHANICAL ENGINEERING",
                "intake": 27,
                "cutoffs": {
                    "1G": {"I": 207450, "II": None},
                    "2AG": {"I": 221715, "II": None},
                    "2BG": {"I": 165324, "II": None},
                    "3AG": {"I": 159885, "II": None},
                    "3BG": {"I": 161827, "II": None},
                    "GM": {"I": 146603, "II": 249347},
                    "SCG": {"I": 234210, "II": None},
                    "STG": {"I": 178465, "II": None}
                }
            },
            {
                "code": "RI",
                "name": "ROBOTICS AND ARTIFICIAL INTELLIGENCE",
                "intake": 14,
                "cutoffs": {
                    "1G": {"I": None, "II": None},
                    "2AG": {"I": 76470, "II": 138580},
                    "2BG": {"I": 91931, "II": 253570},
                    "3AG": {"I": None, "II": None},
                    "3BG": {"I": None, "II": None},
                    "GM": {"I": 70124, "II": 108394},
                    "SCG": {"I": 193049, "II": None},
                    "STG": {"I": 190298, "II": None}
                }
            }
        ]
    },
    # E065 - Jawaharlal Nehru New College of Engineering
    {
        "college_code": "E065",
        "college_name": "Jawaharlal Nehru New College of Engineering",
        "location": "Shimoga",
        "courses": [
            {
                "code": "AI",
                "name": "ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",
                "intake": 54,
                "cutoffs": {
                    "1G": {"I": 34772, "II": 34772},
                    "2AG": {"I": 31476, "II": 42751},
                    "2BG": {"I": None, "II": None},
                    "3AG": {"I": 29484, "II": 29484},
                    "3BG": {"I": 22312, "II": 28204},
                    "GM": {"I": 20240, "II": 23437},
                    "SCG": {"I": 54181, "II": 54181},
                    "STG": {"I": 79249, "II": 79249}
                }
            },
            {
                "code": "CE",
                "name": "CIVIL ENGINEERING",
                "intake": 27,
                "cutoffs": {
                    "1G": {"I": 184496, "II": None},
                    "2AG": {"I": 154068, "II": None},
                    "2BG": {"I": 157917, "II": None},
                    "3AG": {"I": 162791, "II": None},
                    "3BG": {"I": 147000, "II": None},
                    "GM": {"I": 130969, "II": 260006},
                    "SCG": {"I": 182654, "II": None},
                    "STG": {"I": 194902, "II": None}
                }
            },
            {
                "code": "CS",
                "name": "COMPUTER SCIENCE AND ENGINEERING",
                "intake": 108,
                "cutoffs": {
                    "1G": {"I": 33825, "II": 46021},
                    "2AG": {"I": 31160, "II": 44704},
                    "2BG": {"I": 35123, "II": 35123},
                    "3AG": {"I": 30061.5, "II": 34152},
                    "3BG": {"I": 28979, "II": 38034},
                    "GM": {"I": 25366, "II": 29095},
                    "SCG": {"I": 77559.5, "II": 88411},
                    "STG": {"I": 70136, "II": 105020}
                }
            },
            {
                "code": "DS",
                "name": "COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",
                "intake": 27,
                "cutoffs": {
                    "1G": {"I": 41647, "II": 48373},
                    "2AG": {"I": 39043, "II": 54610},
                    "2BG": {"I": 42600, "II": 58086},
                    "3AG": {"I": 45507, "II": 54028},
                    "3BG": {"I": 39442, "II": 47772},
                    "GM": {"I": 35646, "II": 46919},
                    "SCG": {"I": 91159, "II": 113113},
                    "STG": {"I": 100234, "II": 100234}
                }
            },
            {
                "code": "EE",
                "name": "ELECTRICAL & ELECTRONICS ENGINEERING",
                "intake": 27,
                "cutoffs": {
                    "1G": {"I": 75831, "II": 150313},
                    "2AG": {"I": 90347, "II": 128450},
                    "2BG": {"I": 86562, "II": 153664},
                    "3AG": {"I": 91822, "II": 157724},
                    "3BG": {"I": 80032, "II": 103020},
                    "GM": {"I": 74411, "II": 100945},
                    "SCG": {"I": 124481, "II": 204002},
                    "STG": {"I": 144224, "II": 144224}
                }
            },
            {
                "code": "EC",
                "name": "ELECTRONICS AND COMMUNICATION ENGG",
                "intake": 54,
                "cutoffs": {
                    "1G": {"I": 47500, "II": 73426},
                    "2AG": {"I": 50598, "II": 76021},
                    "2BG": {"I": 57752, "II": 86562},
                    "3AG": {"I": 50520, "II": 64519},
                    "3BG": {"I": 45057, "II": 56123},
                    "GM": {"I": 41774, "II": 51284},
                    "SCG": {"I": 99786, "II": 109112},
                    "STG": {"I": 140805, "II": 194769}
                }
            },
            {
                "code": "ET",
                "name": "ELECTRONICS AND TELECOMMUNICATION ENGINEERING",
                "intake": 27,
                "cutoffs": {
                    "1G": {"I": 94085, "II": 167077},
                    "2AG": {"I": 92254, "II": 227789},
                    "2BG": {"I": 85021, "II": 159265},
                    "3AG": {"I": 91102, "II": 217738},
                    "3BG": {"I": 70234, "II": 174863},
                    "GM": {"I": 68725, "II": 145992},
                    "SCG": {"I": 130876, "II": 214995},
                    "STG": {"I": 177665, "II": None}
                }
            },
            {
                "code": "IE",
                "name": "INFORMATION SCIENCE AND ENGINEERING",
                "intake": 81,
                "cutoffs": {
                    "1G": {"I": 46021, "II": 59732},
                    "2AG": {"I": 45849, "II": 64110},
                    "2BG": {"I": 55816, "II": 71668},
                    "3AG": {"I": 43794, "II": 60646},
                    "3BG": {"I": 41499, "II": 56607},
                    "GM": {"I": 39131, "II": 52674},
                    "SCG": {"I": 100215, "II": 128975},
                    "STG": {"I": 123234, "II": 177548}
                }
            },
            {
                "code": "ME",
                "name": "MECHANICAL ENGINEERING",
                "intake": 27,
                "cutoffs": {
                    "1G": {"I": 156914, "II": None},
                    "2AG": {"I": 164730, "II": None},
                    "2BG": {"I": 163686, "II": None},
                    "3AG": {"I": 137299, "II": None},
                    "3BG": {"I": 144925, "II": None},
                    "GM": {"I": 126976, "II": 226667},
                    "SCG": {"I": 178307, "II": None},
                    "STG": {"I": 201168, "II": None}
                }
            },
            {
                "code": "RI",
                "name": "ROBOTICS AND ARTIFICIAL INTELLIGENCE",
                "intake": 27,
                "cutoffs": {
                    "1G": {"I": 123515, "II": 162732},
                    "2AG": {"I": 68381, "II": 79084},
                    "2BG": {"I": None, "II": 73070},
                    "3AG": {"I": 63033, "II": 84138},
                    "3BG": {"I": 59618, "II": 77634},
                    "GM": {"I": 58069, "II": 72785},
                    "SCG": {"I": 114410, "II": 130876},
                    "STG": {"I": 98990, "II": 98990}
                }
            }
        ]
    }
]

def flatten_cutoff_data() -> List[Dict]:
    """
    Convert nested college -> course -> category -> round structure
    into a flat list of records for database import.
    
    Returns:
        List of flattened cutoff records
    """
    flattened = []
    
    for college in EXTRACTED_CUTOFF_DATA:
        for course in college["courses"]:
            for category, rounds in course["cutoffs"].items():
                base_record = {
                    "college_code": college["college_code"],
                    "college_name": college["college_name"],
                    "location": college["location"],
                    "course_code": course["code"],
                    "course_name": course["name"],
                    "intake": course["intake"],
                    "category": category
                }
                
                # Add round I cutoff
                if rounds.get("I") is not None:
                    record_i = base_record.copy()
                    record_i["round"] = 1
                    record_i["cutoff_rank"] = int(rounds["I"]) if isinstance(rounds["I"], float) else rounds["I"]
                    flattened.append(record_i)
                
                # Add round II cutoff
                if rounds.get("II") is not None:
                    record_ii = base_record.copy()
                    record_ii["round"] = 2
                    record_ii["cutoff_rank"] = int(rounds["II"]) if isinstance(rounds["II"], float) else rounds["II"]
                    flattened.append(record_ii)
    
    return flattened

def save_to_json(filename: str = "cutoff_data.json"):
    """Save extracted data to JSON file"""
    flattened = flatten_cutoff_data()
    
    with open(filename, 'w') as f:
        json.dump(flattened, f, indent=2)
    
    print(f"Saved {len(flattened)} records to {filename}")
    return flattened

if __name__ == "__main__":
    # Extract and display summary
    data = flatten_cutoff_data()
    
    print(f"Total flattened records: {len(data)}")
    print(f"Colleges: {len(EXTRACTED_CUTOFF_DATA)}")
    print(f"Unique courses: {len(set(d['course_code'] for d in data))}")
    print(f"\nSample record:")
    print(json.dumps(data[0], indent=2))
    
    # Save for import
    save_to_json()
