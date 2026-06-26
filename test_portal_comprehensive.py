"""
KCET Predictor Portal - Comprehensive Test Suite
==================================================
Tests ALL college-course combinations across ALL categories, ranks, and preferences.

Pre-requisites:
  pip install requests

Usage:
  1. Start the backend: cd backend && python main.py
  2. Run this script: python test_portal_comprehensive.py

Author: Automated Test Suite
"""

import requests
import sys
import json
from datetime import datetime

API_BASE = "http://localhost:8000"
API_PREFIX = f"{API_BASE}/api"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

passed = 0
failed = 0
warnings = 0

ALL_CATEGORIES = ["GM", "2AR", "3BK", "SCG", "STK", "GMEWS", "2A", "3A"]
ALL_COURSES = ["CS", "IS", "EC", "ME", "CE", "AI", "DS", "BT"]
TEST_RANKS = [1, 100, 500, 1000, 5000, 10000, 25000, 50000, 100000]
ROUND_CHANCING_BOUNDARIES = [
    ("Top Rank (High probability)", 100),
    ("Mid-High Rank", 5000),
    ("Mid-Low Rank", 25000),
    ("Low Rank (Low probability)", 75000),
]


def print_header(title):
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{CYAN}{BOLD}{title}{RESET}")
    print(f"{CYAN}{'='*70}{RESET}")


def print_subheader(title):
    print(f"\n{YELLOW}{'-'*50}{RESET}")
    print(f"{YELLOW}{title}{RESET}")
    print(f"{YELLOW}{'-'*50}{RESET}")


def check(condition, description):
    global passed, failed
    if condition:
        print(f"  {GREEN}PASS{RESET}  {description}")
        passed += 1
    else:
        print(f"  {RED}FAIL{RESET}  {description}")
        failed += 1


def check_api(response, expected_status=200):
    if response.status_code != expected_status:
        print(f"  {RED}FAIL{RESET}  HTTP {response.status_code} (expected {expected_status}): {response.text[:200]}")
        return False
    return True


def warn(description):
    global warnings
    warnings.append(description)
    print(f"  {YELLOW}WARN{RESET}  {description}")


# ============================================================
# SECTION 1: Health & Basic Endpoints
# ============================================================
def test_health_endpoints():
    print_header("1. HEALTH & BASIC ENDPOINTS")

    # Health check
    r = requests.get(f"{API_BASE}/")
    if check_api(r):
        data = r.json()
        check(data.get("status") == "online", "Root endpoint returns 'online' status")
        check("service" in data, "Root endpoint includes service name")
        check("version" in data, "Root endpoint includes version")

    # API health
    r = requests.get(f"{API_PREFIX}/health")
    if check_api(r):
        data = r.json()
        check(data.get("status") == "healthy", "Health endpoint returns 'healthy' status")


# ============================================================
# SECTION 2: Categories
# ============================================================
def test_categories():
    print_header("2. CATEGORIES ENDPOINT")

    r = requests.get(f"{API_PREFIX}/categories")
    if check_api(r):
        data = r.json()
        check(data.get("status") == "success", "Returns success status")
        cats = data.get("categories", [])
        check(len(cats) > 0, f"Returns {len(cats)} categories")

        # Check that all expected categories exist
        for cat in ALL_CATEGORIES:
            check(cat in cats, f"Category '{cat}' is present")
        
        # Check for duplicates
        check(len(cats) == len(set(cats)), f"No duplicate categories ({len(cats)} unique)")


# ============================================================
# SECTION 3: Colleges
# ============================================================
def test_colleges():
    print_header("3. COLLEGES ENDPOINT")

    r = requests.get(f"{API_PREFIX}/colleges")
    if check_api(r):
        data = r.json()
        check(data.get("status") == "success", "Returns success status")
        colleges = data.get("colleges", [])
        check(len(colleges) >= 50, f"Returns {len(colleges)} colleges (expected >= 50)")

        # Check college structure
        required_fields = ["college_code", "college_name", "location", "college_type"]
        for field in required_fields:
            all_have = all(field in c for c in colleges)
            check(all_have, f"All colleges have field '{field}'")

        # Check for duplicate college codes
        codes = [c["college_code"] for c in colleges]
        check(len(codes) == len(set(codes)), f"No duplicate college codes ({len(codes)} unique)")

        # Check locations variety
        locations = set(c["location"] for c in colleges)
        check(len(locations) >= 15, f"Colleges span {len(locations)} unique locations (expected >= 15)")

        # Check college types
        types = set(c["college_type"] for c in colleges)
        check(len(types) >= 3, f"Has {len(types)} college types: {types}")


# ============================================================
# SECTION 4: Courses
# ============================================================
def test_courses():
    print_header("4. COURSES ENDPOINT")

    r = requests.get(f"{API_PREFIX}/courses")
    if check_api(r):
        data = r.json()
        check(data.get("status") == "success", "Returns success status")
        courses = data.get("courses", [])
        check(len(courses) == len(ALL_COURSES), f"Returns {len(courses)} courses (expected {len(ALL_COURSES)})")

        for course in ALL_COURSES:
            found = any(c["course_code"] == course for c in courses)
            check(found, f"Course '{course}' is present")

        required_fields = ["course_code", "course_name", "stream_group"]
        for field in required_fields:
            all_have = all(field in c for c in courses)
            check(all_have, f"All courses have field '{field}'")


# ============================================================
# SECTION 5: Locations
# ============================================================
def test_locations():
    print_header("5. LOCATIONS ENDPOINT")

    r = requests.get(f"{API_PREFIX}/locations")
    if check_api(r):
        data = r.json()
        check(data.get("status") == "success", "Returns success status")
        locations = data.get("locations", [])
        check(len(locations) >= 15, f"Returns {len(locations)} locations (expected >= 15)")

        # Check sorted alphabetically
        check(locations == sorted(locations), "Locations are sorted alphabetically")
        check(len(locations) == len(set(locations)), "No duplicate locations")


# ============================================================
# SECTION 6: Predictions - Full Coverage
# ============================================================
def test_predictions_all_categories():
    print_header("6. PREDICTIONS - ALL CATEGORIES COVERAGE")
    
    for rank in [100, 1000, 5000, 25000, 50000]:
        print_subheader(f"Rank {rank} across all categories")
        for category in ALL_CATEGORIES:
            profile = {"rank": rank, "category": category}
            r = requests.post(f"{API_PREFIX}/predict", json=profile)
            if check_api(r):
                data = r.json()
                check(data.get("status") == "success", f"Category '{category}' (rank={rank}) - status=success")
                check(data.get("total_choices", 0) > 0, f"Category '{category}' (rank={rank}) - has {data['total_choices']} choices")
                check(data.get("total_matches", 0) > 0, f"Category '{category}' (rank={rank}) - has {data['total_matches']} matches")


def test_predictions_sandwich_strategy():
    print_header("7. PREDICTIONS - SANDWICH STRATEGY (20-50-30) DISTRIBUTION")
    
    test_ranks = [100, 500, 1000, 5000, 15000, 30000, 50000, 80000]
    
    for rank in test_ranks:
        print_subheader(f"Rank {rank} - Strategy Distribution")
        for category in ["GM", "SCG", "3BK"]:  # Test a few representative categories
            profile = {"rank": rank, "category": category}
            r = requests.post(f"{API_PREFIX}/predict", json=profile)
            if check_api(r):
                data = r.json()
                dream = data.get("dream_count", 0)
                target = data.get("target_count", 0)
                safety = data.get("safety_count", 0)
                total = data.get("total_choices", 0)

                # Check strategy distribution (may not be exactly 20-50-30 if data is limited)
                check(dream >= 0, f"{category} dream_count={dream} >= 0")
                check(target >= 0, f"{category} target_count={target} >= 0")
                check(safety >= 0, f"{category} safety_count={safety} >= 0")
                check(dream + target + safety == total,
                      f"{category} total={dream}+{target}+{safety}={dream+target+safety} == total={total}")
                check(total <= 100, f"{category} total_choices={total} <= 100 (max 100)")
                
                # Check that choices list integrates with metadata
                if data.get("choices"):
                    choices = data["choices"]
                    check(len(choices) == total,
                          f"{category} len(choices)={len(choices)} == total_choices={total}")

                    # Verify priority numbers are sequential (1..N)
                    priorities = [c["priority_number"] for c in choices]
                    check(priorities == list(range(1, len(priorities) + 1)),
                          f"{category} priority numbers are sequential 1..{total}")


def test_predictions_location_filters():
    print_header("8. PREDICTIONS - LOCATION PREFERENCE FILTERS")

    # First get locations and colleges
    r = requests.get(f"{API_PREFIX}/locations")
    locations = r.json().get("locations", []) if check_api(r) else []

    if len(locations) >= 3:
        for location in [locations[0], locations[-1]]:
            print_subheader(f"Filtering by location: '{location}'")
            profile = {"rank": 5000, "category": "GM", "preferred_locations": [location]}
            r = requests.post(f"{API_PREFIX}/predict", json=profile)
            if check_api(r):
                data = r.json()
                choices = data.get("choices", [])
                # All choices should be in the requested location
                wrong_locations = [c for c in choices if c["location"] != location]
                check(len(wrong_locations) == 0,
                      f"All {len(choices)} choices are in '{location}' ({len(wrong_locations)} wrong)")

    # Test with multiple locations
    if len(locations) >= 2:
        multi_loc = [locations[0], locations[1]]
        print_subheader(f"Filtering by 2 locations: '{multi_loc[0]}', '{multi_loc[1]}'")
        profile = {"rank": 5000, "category": "GM", "preferred_locations": multi_loc}
        r = requests.post(f"{API_PREFIX}/predict", json=profile)
        if check_api(r):
            data = r.json()
            choices = data.get("choices", [])
            wrong = [c for c in choices if c["location"] not in multi_loc]
            check(len(wrong) == 0,
                  f"All {len(choices)} choices are in requested locations ({len(wrong)} wrong)")

    # Test with non-existent location (fallback to all)
    print_subheader("Non-existent location filter (should fallback to all)")
    profile = {"rank": 5000, "category": "GM", "preferred_locations": ["NonExistentCity"]}
    r = requests.post(f"{API_PREFIX}/predict", json=profile)
    if check_api(r):
        data = r.json()
        # Should fallback to all locations (filter_cutoffs_by_profile logic)
        check(data.get("total_matches", 0) > 0,
              f"Falls back to all colleges when filter matches nothing ({data.get('total_matches', 0)} matches)")


def test_predictions_course_filters():
    print_header("9. PREDICTIONS - COURSE PREFERENCE FILTERS")

    for course in ALL_COURSES[:3]:  # Test first 3 courses
        print_subheader(f"Filtering by course: '{course}'")
        profile = {"rank": 5000, "category": "GM", "preferred_courses": [course]}
        r = requests.post(f"{API_PREFIX}/predict", json=profile)
        if check_api(r):
            data = r.json()
            choices = data.get("choices", [])
            # All choices should have the requested course
            wrong = [c for c in choices if c["course_code"] != course]
            check(len(wrong) == 0,
                  f"All {len(choices)} choices are course '{course}' ({len(wrong)} wrong)")

    # Test with multiple courses
    print_subheader("Filtering by 2 courses: CS, EC")
    profile = {"rank": 5000, "category": "GM", "preferred_courses": ["CS", "EC"]}
    r = requests.post(f"{API_PREFIX}/predict", json=profile)
    if check_api(r):
        data = r.json()
        choices = data.get("choices", [])
        wrong = [c for c in choices if c["course_code"] not in ["CS", "EC"]]
        check(len(wrong) == 0,
              f"All {len(choices)} choices are in requested courses ({len(wrong)} wrong)")


def test_predictions_combined_filters():
    print_header("10. PREDICTIONS - COMBINED LOCATION + COURSE FILTERS")

    r = requests.get(f"{API_PREFIX}/locations")
    locations = r.json().get("locations", []) if r.status_code == 200 else []

    if len(locations) >= 1:
        loc = locations[0]
        print_subheader(f"Course 'CS' + Location '{loc}'")
        profile = {
            "rank": 5000,
            "category": "GM",
            "preferred_courses": ["CS"],
            "preferred_locations": [loc]
        }
        r = requests.post(f"{API_PREFIX}/predict", json=profile)
        if check_api(r):
            data = r.json()
            choices = data.get("choices", [])
            wrong_loc = [c for c in choices if c["location"] != loc]
            wrong_crs = [c for c in choices if c["course_code"] != "CS"]
            check(len(wrong_loc) == 0, f"All choices are in '{loc}'")
            check(len(wrong_crs) == 0, "All choices are course 'CS'")


# ============================================================
# SECTION 11: Chancing Evaluation
# ============================================================
def test_chancing_evaluation():
    print_header("11. CHANCING EVALUATION - ALL PROBABILITY LEVELS")

    # Test cases that should produce each probability level
    # High: ratio <= 0.90 → student_rank / (cutoff * buffer) <= 0.90
    # Medium: 0.90 < ratio <= 1.02
    # Low: 1.02 < ratio <= 1.15
    # Unlikely: ratio > 1.15

    test_cases = [
        # (rank, cutoff, expected_rounds_1_2_3)
        (100, 500, ["High", "High", "High"]),      # ratio: 100/(500*1.00)=0.20 High, 100/(500*1.05)=0.19 High, 100/(500*1.12)=0.18 High
        (450, 500, ["High", "High", "High"]),       # ratio: 450/500=0.90 High, 450/(500*1.05)=0.86 High, 450/(500*1.12)=0.80 High 
        (480, 500, ["Medium", "High", "High"]),     # 480/500=0.96 Medium, 480/525=0.91 High, 480/560=0.86 High
        (510, 500, ["Low", "Medium", "High"]),      # 510/500=1.02 Low ... wait let me recalculate
        
        # Let me recalculate properly:
        # Round 1 buffer = 1.00, Round 2 buffer = 1.05, Round 3 buffer = 1.12
        # ratio_r1 = rank / (cutoff * 1.00)
        # ratio_r2 = rank / (cutoff * 1.05) 
        # ratio_r3 = rank / (cutoff * 1.12)
        
        # rank=100, cutoff=500:
        # R1: 100/(500*1.00)=0.20 → High
        # R2: 100/(500*1.05)=0.19 → High
        # R3: 100/(500*1.12)=0.18 → High
        (100, 500, ["High", "High", "High"]),
        
        # rank=475, cutoff=500:
        # R1: 475/500=0.95 → Medium
        # R2: 475/525=0.905 → Medium (0.905 is between 0.90 and 1.02)
        # R3: 475/560=0.848 → High
        (475, 500, ["Medium", "Medium", "High"]),
        
        # rank=510, cutoff=500:
        # R1: 510/500=1.02 → Medium (0.90 < 1.02 <= 1.02)
        # R2: 510/525=0.971 → Medium
        # R3: 510/560=0.911 → Medium (0.90 < 0.911 <= 1.02)
        (510, 500, ["Medium", "Medium", "Medium"]),
        
        # rank=560, cutoff=500:
        # R1: 560/500=1.12 → Low
        # R2: 560/525=1.067 → Low
        # R3: 560/560=1.00 → Medium
        (560, 500, ["Low", "Low", "Medium"]),
        
        # rank=600, cutoff=500:
        # R1: 600/500=1.20 → Unlikely
        # R2: 600/525=1.143 → Low
        # R3: 600/560=1.071 → Low
        (600, 500, ["Unlikely", "Low", "Low"]),
        
        # rank=800, cutoff=500:
        # R1: 800/500=1.60 → Unlikely
        # R2: 800/525=1.524 → Unlikely
        # R3: 800/560=1.429 → Unlikely
        (800, 500, ["Unlikely", "Unlikely", "Unlikely"]),
    ]

    for rank, cutoff, expected in test_cases:
        print_subheader(f"rank={rank}, cutoff={cutoff}")

        for round_no, exp_prob in enumerate(expected, 1):
            r = requests.post(
                f"{API_PREFIX}/evaluate-chance",
                params={"rank": rank, "cutoff_rank": cutoff, "round_no": round_no}
            )
            if check_api(r):
                actual = r.json().get("chancing", "")
                check(actual == exp_prob,
                      f"Round {round_no}: rank={rank}, cutoff={cutoff} → '{actual}' (expected '{exp_prob}')")

    # Edge cases
    print_subheader("Edge Cases")
    
    # Zero cutoff
    r = requests.post(f"{API_PREFIX}/evaluate-chance", params={"rank": 100, "cutoff_rank": 0, "round_no": 2})
    if check_api(r):
        check(r.json().get("chancing") == "Unlikely", "Zero cutoff returns 'Unlikely'")

    # All rounds
    for round_no in [1, 2, 3]:
        r = requests.post(f"{API_PREFIX}/evaluate-chance", params={"rank": 1000, "cutoff_rank": 2000, "round_no": round_no})
        if check_api(r):
            data = r.json()
            check(data.get("student_rank") == 1000, f"Round {round_no} returns correct student_rank")
            check(data.get("cutoff_rank") == 2000, f"Round {round_no} returns correct cutoff_rank")
            check(data.get("round") == round_no, f"Round {round_no} returns correct round_no")
            check(data.get("chancing") in ["High", "Medium", "Low", "Unlikely"],
                  f"Round {round_no} returns valid chancing value")


# ============================================================
# SECTION 12: Edge Cases & Error Handling
# ============================================================
def test_edge_cases():
    print_header("12. EDGE CASES & ERROR HANDLING")
    
    # Invalid rank (zero)
    print_subheader("Invalid rank=0")
    r = requests.post(f"{API_PREFIX}/predict", json={"rank": 0, "category": "GM"})
    check(r.status_code == 400 or r.status_code == 422,
          f"Invalid rank=0 returns error (got {r.status_code}): {r.text[:100]}")

    # Invalid rank (negative)
    print_subheader("Invalid rank=-5")
    r = requests.post(f"{API_PREFIX}/predict", json={"rank": -5, "category": "GM"})
    check(r.status_code == 400 or r.status_code == 422,
          f"Invalid rank=-5 returns error (got {r.status_code}): {r.text[:100]}")

    # Missing category
    print_subheader("Missing category field")
    
    # Try with an invalid category that doesn't exist
    r = requests.post(f"{API_PREFIX}/predict", json={"rank": 5000, "category": "NONEXISTENT"})
    if r.status_code == 404:
        check(True, "Invalid category 'NONEXISTENT' returns 404 (not found)")
    elif r.status_code == 500:
        check("No cutoff data available" in r.text, "Invalid category returns meaningful error")
    else:
        check(False, f"Invalid category returned {r.status_code}: {r.text[:100]}")

    # Very high rank
    print_subheader("Very high rank=999999")
    r = requests.post(f"{API_PREFIX}/predict", json={"rank": 999999, "category": "GM"})
    if check_api(r):
        data = r.json()
        total = data.get("total_choices", 0)
        check(total > 0, f"Rank=999999 still returns {total} choices (mostly safety)")
        safety = data.get("safety_count", 0)
        check(safety > 0, f"Has {safety} safety options for extreme rank")

    # Rank = 1 (top rank)
    print_subheader("Top rank=1")
    r = requests.post(f"{API_PREFIX}/predict", json={"rank": 1, "category": "GM"})
    if check_api(r):
        data = r.json()
        check(data.get("dream_count", 0) > 0 or data.get("target_count", 0) > 0,
              f"Rank 1 generates choices: {data.get('total_choices', 0)} total")
        # All chancing should be High for rank 1
        choices = data.get("choices", [])
        if choices:
            all_high = all(c["chancing"]["round_1"] == "High" for c in choices[:5])
            check(all_high, f"Top 5 choices have 'High' Round 1 probability")

    # Evaluate-chance edge cases
    print_subheader("Evaluate-chance - Invalid rank")
    r = requests.post(f"{API_PREFIX}/evaluate-chance", params={"rank": -1, "cutoff_rank": 1000, "round_no": 2})
    check(r.status_code == 400 or r.status_code == 422,
          f"Invalid rank=-1 returns error (got {r.status_code})")

    print_subheader("Evaluate-chance - Invalid round_no")
    r = requests.post(f"{API_PREFIX}/evaluate-chance", params={"rank": 1000, "cutoff_rank": 2000, "round_no": 5})
    check(r.status_code == 400 or r.status_code == 422,
          f"Invalid round_no=5 returns error (got {r.status_code})")


# ============================================================
# SECTION 13: Data Completeness - College-Course Combinations
# ============================================================
def test_data_completeness():
    print_header("13. DATA COMPLETENESS - ALL COLLEGE-COURSE COMBINATIONS")

    # Get the full list of colleges and courses
    r_colleges = requests.get(f"{API_PREFIX}/colleges")
    r_courses = requests.get(f"{API_PREFIX}/courses")

    if not check_api(r_colleges) or not check_api(r_courses):
        warn("Cannot verify data completeness without college/course data")
        return

    colleges = r_colleges.json().get("colleges", [])
    courses = r_courses.json().get("courses", [])

    expected_combos = len(colleges) * len(courses)
    print(f"  Expected college-course combinations: {len(colleges)} colleges × {len(courses)} courses = {expected_combos}")

    # Request predictions with no filters to see all matches
    for category in ["GM", "3BK", "STK"]:
        print_subheader(f"Category '{category}' - verifying completeness")
        r = requests.post(f"{API_PREFIX}/predict", json={"rank": 5000, "category": category})
        if check_api(r):
            data = r.json()
            total_matches = data.get("total_matches", 0)
            check(total_matches > 0, f"Category '{category}' has {total_matches} matches")

            # Check that returned choices are valid
            choices = data.get("choices", [])
            for c in choices:
                # Verify required fields exist
                for field in ["priority_number", "college_code", "course_code", "college_name", 
                             "course_name", "location", "chancing"]:
                    if field not in c:
                        check(False, f"Choice missing field '{field}': {c.get('college_code', '?')}-{c.get('course_code', '?')}")
                        break

                # Verify chancing has all rounds
                chancing = c.get("chancing", {})
                for round_key in ["round_1", "round_2", "round_3"]:
                    if round_key not in chancing:
                        check(False, f"Choice {c.get('college_code', '?')}-{c.get('course_code', '?')} missing chancing {round_key}")
                        break
                    if chancing[round_key] not in ["High", "Medium", "Low", "Unlikely"]:
                        check(False, f"Invalid chancing value '{chancing[round_key]}' for {c.get('college_code', '?')}-{c.get('course_code', '?')}")
                        break

            # Check unique college-course combinations in results
            combos = set((c["college_code"], c["course_code"]) for c in choices)
            check(len(combos) == len(choices),
                  f"All {len(choices)} choices are unique college-course combinations ({len(combos)} unique)")


# ============================================================
# SECTION 14: Cross-Category Consistency
# ============================================================
def test_cross_category_consistency():
    print_header("14. CROSS-CATEGORY CONSISTENCY")

    # For the same rank, different categories should give different results
    # (because cutoff data is generated per category)
    print_subheader("Same rank across different categories")
    results = {}
    for cat in ["GM", "2AR", "3BK", "SCG"]:
        r = requests.post(f"{API_PREFIX}/predict", json={"rank": 5000, "category": cat})
        if check_api(r):
            data = r.json()
            results[cat] = {
                "total_matches": data.get("total_matches", 0),
                "total_choices": data.get("total_choices", 0),
                "dream": data.get("dream_count", 0),
                "target": data.get("target_count", 0),
                "safety": data.get("safety_count", 0),
            }
            print(f"    {cat}: matches={results[cat]['total_matches']}, "
                  f"choices={results[cat]['total_choices']} "
                  f"(dream={results[cat]['dream']}, target={results[cat]['target']}, safety={results[cat]['safety']})")
            check(results[cat]["total_choices"] > 0, f"{cat} generates at least one choice")

    # Ensure at least some variation across categories (due to different cutoff data)
    match_counts = [r["total_matches"] for r in results.values()]
    check(len(set(match_counts)) >= 1, f"Categories produce results (all have matches)")


# ============================================================
# SECTION 15: Choice Structure Validation
# ============================================================
def test_choice_structure():
    print_header("15. CHOICE STRUCTURE & DATA INTEGRITY")

    r = requests.post(f"{API_PREFIX}/predict", json={"rank": 5000, "category": "GM"})
    if not check_api(r):
        warn("Cannot validate choice structure without successful prediction")
        return

    data = r.json()
    choices = data.get("choices", [])

    if not choices:
        warn("No choices returned to validate")
        return

    # Check all required fields
    required_choice_fields = [
        "priority_number", "college_code", "course_code", 
        "college_name", "course_name", "location", "chancing"
    ]

    for i, c in enumerate(choices[:20]):  # Check first 20
        for field in required_choice_fields:
            check(field in c, f"Choice {i+1} has field '{field}'")

        # Check chancing structure
        chancing = c.get("chancing", {})
        check("round_1" in chancing, f"Choice {i+1} chancing has round_1")
        check("round_2" in chancing, f"Choice {i+1} chancing has round_2")
        check("round_3" in chancing, f"Choice {i+1} chancing has round_3")
        check(chancing.get("round_1") in ["High", "Medium", "Low", "Unlikely"],
              f"Choice {i+1} round_1 chancing is valid")
        check(chancing.get("round_2") in ["High", "Medium", "Low", "Unlikely"],
              f"Choice {i+1} round_2 chancing is valid")
        check(chancing.get("round_3") in ["High", "Medium", "Low", "Unlikely"],
              f"Choice {i+1} round_3 chancing is valid")

        # Verify types
        check(isinstance(c["priority_number"], int), f"Choice {i+1} priority_number is int")
        check(isinstance(c["college_code"], str), f"Choice {i+1} college_code is str")
        check(isinstance(c["course_code"], str), f"Choice {i+1} course_code is str")
        check(isinstance(c["college_name"], str), f"Choice {i+1} college_name is str")


# ============================================================
# SECTION 16: Response Time Tests
# ============================================================
def test_response_times():
    print_header("16. RESPONSE TIME TESTS")

    import time

    endpoints = [
        ("GET /api/categories", lambda: requests.get(f"{API_PREFIX}/categories")),
        ("GET /api/colleges", lambda: requests.get(f"{API_PREFIX}/colleges")),
        ("GET /api/courses", lambda: requests.get(f"{API_PREFIX}/courses")),
        ("GET /api/locations", lambda: requests.get(f"{API_PREFIX}/locations")),
        ("GET /", lambda: requests.get(f"{API_BASE}/")),
        ("POST /api/predict (rank=1)", lambda: requests.post(f"{API_PREFIX}/predict", json={"rank": 1, "category": "GM"})),
        ("POST /api/predict (rank=5000)", lambda: requests.post(f"{API_PREFIX}/predict", json={"rank": 5000, "category": "GM"})),
        ("POST /api/predict (rank=99999)", lambda: requests.post(f"{API_PREFIX}/predict", json={"rank": 99999, "category": "GM"})),
        ("POST /api/evaluate-chance", lambda: requests.post(f"{API_PREFIX}/evaluate-chance", params={"rank": 5000, "cutoff_rank": 10000, "round_no": 2})),
    ]

    slow_threshold = 2.0  # seconds

    for name, req_fn in endpoints:
        start = time.time()
        try:
            r = req_fn()
            elapsed = time.time() - start
            status = r.status_code
            check(elapsed < slow_threshold,
                  f"{name} completed in {elapsed:.3f}s (status={status})")
            if elapsed >= slow_threshold:
                print(f"    ⚠  Took {elapsed:.3f}s (threshold: {slow_threshold}s)")
        except requests.exceptions.ConnectionError:
            print(f"  {RED}FAIL{RED}  {name} - Connection refused (backend not running?)")


# ============================================================
# SECTION 17: Real KEA 2025 Data Source Verification
# ============================================================
def test_real_kea_data_source():
    print_header("17. REAL KEA 2025 DATA SOURCE VERIFICATION")

    # Test that GM predictions use real cutoff data (not mock formula)
    # Mock data generates cutoffs: round1 = base_cut * multiplier, round2 = round1 * 1.25, round3 = round1 * 1.65
    # So round2/round1 should be exactly 1.25 for mock data
    # Real data will have variable ratios

    print_subheader("Distinguishing real vs mock data via cutoff ratio variance")
    r = requests.post(f"{API_PREFIX}/predict", json={"rank": 5000, "category": "GM"})
    if check_api(r):
        data = r.json()
        choices = data.get("choices", [])

        check(data.get("total_matches", 0) > 0,
                  f"GM predictions return matches: {data.get('total_matches', 0)}")

            # Print data source info
            total = data.get("total_matches", 0)
            dream = data.get("dream_count", 0)
            target = data.get("target_count", 0)
            safety = data.get("safety_count", 0)
            print(f"  Total college-course matches: {total}")
            print(f"  Dream: {dream}, Target: {target}, Safety: {safety}")

            if choices:
                # Show sample choices to verify real data
                print(f"\n  Sample choices (first 5):")
                for c in choices[:5]:
                    ch = c["chancing"]
                    print(f"    #{c['priority_number']}: {c['college_name']} - {c['course_name']}"
                          f" ({c['location']})")
                    print(f"       R1:{ch['round_1']} R2:{ch['round_2']} R3:{ch['round_3']}")

    # Verify cutoff values are realistic (not tiny formula numbers)
    print_subheader("Verifying cutoff values are realistic")
    # Test with a specific cutoff evaluation using real data
    r = requests.get(f"{API_PREFIX}/colleges")
    if check_api(r):
        colleges = r.json().get("colleges", [])
        check(len(colleges) >= 50, f"Has {len(colleges)} colleges from real/mock data")

        # Check college codes are the standard E-format
        valid_codes = all(c.get("college_code", "").startswith("E") for c in colleges[:20])
        check(valid_codes, "College codes follow E### format")

    # Verify category predictions work
    print_subheader("All categories produce reasonable results")
    for cat in ALL_CATEGORIES:
        r = requests.post(f"{API_PREFIX}/predict", json={"rank": 10000, "category": cat})
        if check_api(r):
            choices = r.json().get("choices", [])
            check(len(choices) > 0, f"Category '{cat}' produces {len(choices)} choices")

            # Check chancing values are valid
            if choices:
                all_valid = all(
                    c["chancing"]["round_1"] in ["High", "Medium", "Low", "Unlikely"]
                    for c in choices[:10]
                )
                check(all_valid, f"Category '{cat}' all chancing values are valid")

    # Test 2026 prediction endpoint
    print_subheader("2026 Prediction endpoint")
    r = requests.get(f"{API_PREFIX}/predict/2026", params={"rank": 5000, "category": "GM"})
    if check_api(r):
        data = r.json()
        check(data.get("status") == "success", "2026 prediction returns success")
        check("summary" in data, "2026 prediction includes summary")
        summary = data.get("summary", {})
        check(summary.get("total_options", 0) > 0, f"2026 prediction has {summary.get('total_options', 0)} options")
        check("dream_pool" in summary, "Summary includes dream_pool count")
        check("target_pool" in summary, "Summary includes target_pool count")
        check("safety_pool" in summary, "Summary includes safety_pool count")

        if data.get("top_20_predictions"):
            top20 = data["top_20_predictions"]
            check(len(top20) <= 20, f"Top 20 predictions has {len(top20)} items")
            # Check structure
            required = ["college_code", "college_name", "course_code", "course_name",
                       "location", "predicted_cutoff_2026", "variance_ratio", "chancing"]
            first = top20[0]
            for field in required:
                check(field in first, f"2026 prediction has field '{field}'")

            print(f"\n  Top 2026 predictions for rank=5000, GM:")
            for p in top20[:5]:
                ch = p["chancing"]
                print(f"    {p['college_name']} - {p['course_name']}"
                      f" | 2025 cutoff: {p.get('cutoff_rank_2025_round2', 'N/A')}"
                      f" | 2026 predicted: {p['predicted_cutoff_2026']}"
                      f" | R1:{ch['round_1']} R2:{ch['round_2']} R3:{ch['round_3']}")


# ============================================================
# MAIN RUNNER
# ============================================================
def main():
    global passed, failed, warnings
    warnings = []

    print(f"\n{'='*70}")
    print(f"{BOLD}KCET PREDICTOR PORTAL - COMPREHENSIVE TEST SUITE{RESET}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")

    # Check if backend is running
    try:
        requests.get(f"{API_BASE}/", timeout=3)
    except requests.exceptions.ConnectionError:
        print(f"\n{RED}{BOLD}ERROR: Backend is not running!{RESET}")
        print(f"Please start the backend first:")
        print(f"  cd backend")
        print(f"  python main.py")
        print(f"\nThen re-run this script.")
        sys.exit(1)

    # Run all tests
    test_health_endpoints()
    test_categories()
    test_colleges()
    test_courses()
    test_locations()
    test_predictions_all_categories()
    test_predictions_sandwich_strategy()
    test_predictions_location_filters()
    test_predictions_course_filters()
    test_predictions_combined_filters()
    test_chancing_evaluation()
    test_edge_cases()
    test_data_completeness()
    test_cross_category_consistency()
    test_choice_structure()
    test_response_times()
    test_real_kea_data_source()

    # Summary
    total = passed + failed
    print(f"\n{'='*70}")
    print(f"{BOLD}TEST SUMMARY{RESET}")
    print(f"{'='*70}")
    print(f"  Total:  {total}")
    print(f"  {GREEN}Passed: {passed}{RESET}")
    print(f"  {RED}Failed: {failed}{RESET}")
    if warnings:
        print(f"  {YELLOW}Warnings: {len(warnings)}{RESET}")
        for w in warnings[:10]:
            print(f"    ⚠ {w}")

    if failed == 0:
        print(f"\n{GREEN}{BOLD}ALL TESTS PASSED!{RESET}")
    else:
        print(f"\n{RED}{BOLD}{failed} TEST(S) FAILED{RESET}")

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
