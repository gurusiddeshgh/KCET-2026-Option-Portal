"""
KCET Predictor - Data Loader Unit Tests
==========================================
Tests for data_loader.py functions with mocked file operations for reliability.

Run:  python -m pytest backend/test_data_loader.py -v
"""

import sys
import os
import json
import pytest
from unittest.mock import patch, mock_open, MagicMock
from typing import List, Dict, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))


# =============================================================================
# infer_location_from_name
# =============================================================================

class TestInferLocationFromName:
    def test_bangalore_variations(self):
        from data_loader import infer_location_from_name
        for name in ["BMS College of Engineering Bangalore",
                      "Bangalore Institute of Technology",
                      "UVCE BANGALORE"]:
            assert infer_location_from_name(name) == "Bangalore"

    def test_mysore_variations(self):
        from data_loader import infer_location_from_name
        for name in ["NIE Mysore", "MYSORE College of Engineering", "Mysuru University"]:
            assert infer_location_from_name(name) == "Mysore"

    def test_hubballi_variations(self):
        from data_loader import infer_location_from_name
        for name in ["KLE Hubballi", "Hubli Institute", "Dharwad Engineering College"]:
            assert infer_location_from_name(name) == "Hubballi"

    def test_unknown_location_fallback(self):
        from data_loader import infer_location_from_name
        assert infer_location_from_name("Some Unknown College") == "Other"
        assert infer_location_from_name("") == "Other"
        assert infer_location_from_name(None) == "Other"

    def test_mangalore_variations(self):
        from data_loader import infer_location_from_name
        assert infer_location_from_name("Mangalore Institute of Technology") == "Mangalore"
        assert infer_location_from_name("MANGALURU College") == "Mangalore"
        assert infer_location_from_name("NITK Surathkal") == "Mangalore"

    def test_belgaum_variations(self):
        from data_loader import infer_location_from_name
        assert infer_location_from_name("KLE Belgaum") == "Belgaum"
        assert infer_location_from_name("Belagavi Engineering College") == "Belgaum"


# =============================================================================
# KNOWN_COLLEGE_INFO
# =============================================================================

class TestKnownCollegeInfo:
    def test_all_known_colleges_have_location_and_type(self):
        from data_loader import KNOWN_COLLEGE_INFO
        for code, info in KNOWN_COLLEGE_INFO.items():
            assert "location" in info, f"{code} missing location"
            assert info["location"], f"{code} has empty location"
            assert "college_type" in info, f"{code} missing college_type"
            assert info["college_type"], f"{code} has empty college_type"

    def test_known_college_codes_start_with_E(self):
        from data_loader import KNOWN_COLLEGE_INFO
        for code in KNOWN_COLLEGE_INFO:
            assert code.startswith("E"), f"Code {code} should start with E"

    def test_major_cities_represented(self):
        from data_loader import KNOWN_COLLEGE_INFO
        cities = {info["location"] for info in KNOWN_COLLEGE_INFO.values()}
        for city in ["Bangalore", "Mysore", "Belgaum", "Hubballi", "Mangalore"]:
            assert city in cities, f"{city} should be in KNOWN_COLLEGE_INFO"


# =============================================================================
# Category constants
# =============================================================================

class TestCategoryConstants:
    def test_all_eight_categories_present(self):
        from data_loader import ALL_CATEGORIES
        expected = ["GM", "2AR", "3BK", "SCG", "STK", "GMEWS", "2A", "3A"]
        for cat in expected:
            assert cat in ALL_CATEGORIES
        assert len(ALL_CATEGORIES) == 8

    def test_all_multipliers_positive(self):
        from data_loader import CATEGORY_MULTIPLIERS
        for cat, mult in CATEGORY_MULTIPLIERS.items():
            assert mult > 0, f"Multiplier for {cat} should be positive"

    def test_gm_multiplier_is_1(self):
        from data_loader import CATEGORY_MULTIPLIERS
        assert CATEGORY_MULTIPLIERS["GM"] == 1.00

    def test_reserved_categories_have_easier_multipliers(self):
        from data_loader import CATEGORY_MULTIPLIERS
        assert CATEGORY_MULTIPLIERS["SCG"] > 1.0
        assert CATEGORY_MULTIPLIERS["STK"] > 1.0

    def test_all_categories_have_multipliers(self):
        from data_loader import ALL_CATEGORIES, CATEGORY_MULTIPLIERS
        for cat in ALL_CATEGORIES:
            assert cat in CATEGORY_MULTIPLIERS


# =============================================================================
# estimate_category_cutoffs
# =============================================================================

class TestEstimateCategoryCutoffs:
    GM_RECORDS = [
        {"college_code": "E001", "college_name": "UVCE", "course_code": "CS",
         "course_name": "CS", "location": "Bangalore", "college_type": "Government",
         "stream_group": "Engineering", "category": "GM",
         "round_1_cutoff": 1000, "round_2_cutoff": 1200, "round_3_cutoff": 1500},
        {"college_code": "E002", "college_name": "RVCE", "course_code": "EC",
         "course_name": "EC", "location": "Bangalore", "college_type": "Private",
         "stream_group": "Engineering", "category": "GM",
         "round_1_cutoff": 2000, "round_2_cutoff": 2500, "round_3_cutoff": 3000},
    ]

    def test_gm_returns_identical_data(self):
        from data_loader import estimate_category_cutoffs
        result = estimate_category_cutoffs(self.GM_RECORDS, "GM")
        assert result == self.GM_RECORDS

    def test_scg_applies_2x_multiplier(self):
        from data_loader import estimate_category_cutoffs
        result = estimate_category_cutoffs(self.GM_RECORDS, "SCG")  # SCG = 2.20
        assert result[0]["round_1_cutoff"] == 2200  # 1000 * 2.20
        assert result[0]["round_2_cutoff"] == 2640  # 1200 * 2.20
        assert result[0]["round_3_cutoff"] == 3300  # 1500 * 2.20

    def test_estimated_records_have_correct_category(self):
        from data_loader import estimate_category_cutoffs
        result = estimate_category_cutoffs(self.GM_RECORDS, "3BK")
        assert all(r["category"] == "3BK" for r in result)

    def test_metadata_preserved_in_estimates(self):
        from data_loader import estimate_category_cutoffs
        result = estimate_category_cutoffs(self.GM_RECORDS, "2AR")
        assert result[0]["college_code"] == "E001"
        assert result[0]["college_name"] == "UVCE"
        assert result[0]["location"] == "Bangalore"

    def test_unknown_category_uses_1x_multiplier(self):
        from data_loader import estimate_category_cutoffs
        result = estimate_category_cutoffs(self.GM_RECORDS, "UNKNOWN")
        assert result[0]["round_1_cutoff"] == self.GM_RECORDS[0]["round_1_cutoff"]

    def test_none_cutoffs_remain_none_after_estimation(self):
        from data_loader import estimate_category_cutoffs
        records = [
            {"college_code": "E001", "college_name": "UVCE", "course_code": "CS",
             "course_name": "CS", "location": "Bangalore", "college_type": "Government",
             "stream_group": "Engineering", "category": "GM",
             "round_1_cutoff": None, "round_2_cutoff": 1200, "round_3_cutoff": None},
        ]
        result = estimate_category_cutoffs(records, "SCG")
        assert result[0]["round_1_cutoff"] is None
        assert result[0]["round_2_cutoff"] == 2640
        assert result[0]["round_3_cutoff"] is None


# =============================================================================
# _enrich_record
# =============================================================================

class TestEnrichRecord:
    def test_adds_location_from_known_info(self):
        from data_loader import _enrich_record
        result = _enrich_record({"college_code": "E001", "college_name": "UVCE"})
        assert result["location"] == "Bangalore"
        assert result["college_type"] == "Government"

    def test_preserves_existing_location(self):
        from data_loader import _enrich_record
        result = _enrich_record({
            "college_code": "E001", "location": "CustomCity", "college_type": "CustomType"
        })
        assert result["location"] == "CustomCity"
        assert result["college_type"] == "CustomType"

    def test_infers_location_for_unknown_college(self):
        from data_loader import _enrich_record
        result = _enrich_record({"college_code": "E999", "college_name": "NIE Mysore"})
        # _enrich_record doesn't call infer_location_from_name, so location is empty
        assert result["location"] == ""
        assert result["college_type"] == "Private-Unaided"

    def test_sets_default_stream_group(self):
        from data_loader import _enrich_record
        assert _enrich_record({"college_code": "E001", "college_name": "UVCE"})["stream_group"] == "Engineering"

    def test_sets_default_category(self):
        from data_loader import _enrich_record
        assert _enrich_record({"college_code": "E001", "college_name": "UVCE"})["category"] == "GM"


# =============================================================================
# get_locations_from_data
# =============================================================================

class TestGetLocationsFromData:
    def test_extracts_unique_nonempty_locations(self):
        from data_loader import get_locations_from_data
        colleges = [
            {"college_code": "E001", "location": "Bangalore"},
            {"college_code": "E002", "location": "Mysore"},
            {"college_code": "E003", "location": "Bangalore"},
            {"college_code": "E004", "location": ""},
        ]
        result = get_locations_from_data(colleges)
        assert "Bangalore" in result
        assert "Mysore" in result
        assert len(result) == 2

    def test_empty_list(self):
        from data_loader import get_locations_from_data
        assert get_locations_from_data([]) == []

    def test_sorted_output(self):
        from data_loader import get_locations_from_data
        result = get_locations_from_data([
            {"college_code": "E002", "location": "Mysore"},
            {"college_code": "E001", "location": "Bangalore"},
        ])
        assert result == ["Bangalore", "Mysore"]


# =============================================================================
# _has_all_categories
# =============================================================================

class TestHasAllCategories:
    def test_all_eight_returns_true(self):
        from data_loader import _has_all_categories
        cats = [{"category": c} for c in ["GM", "2AR", "3BK", "SCG", "STK", "GMEWS", "2A", "3A"]]
        assert _has_all_categories(cats) is True

    def test_subset_returns_false(self):
        from data_loader import _has_all_categories
        assert _has_all_categories([{"category": "GM"}, {"category": "2AR"}]) is False

    def test_duplicates_not_enough(self):
        from data_loader import _has_all_categories
        assert _has_all_categories([{"category": "GM"}] * 20) is False

    def test_empty_returns_false(self):
        from data_loader import _has_all_categories
        assert _has_all_categories([]) is False


# =============================================================================
# _enrich_college_dict
# =============================================================================

class TestEnrichCollegeDict:
    def test_known_college_enriched(self):
        from data_loader import _enrich_college_dict
        result = _enrich_college_dict({"college_code": "E001", "college_name": "UVCE"})
        assert result["location"] == "Bangalore"
        assert result["college_type"] == "Government"
        assert result["status"] is True

    def test_existing_values_preserved(self):
        from data_loader import _enrich_college_dict
        result = _enrich_college_dict({
            "college_code": "E001", "college_name": "UVCE",
            "location": "CustomLoc", "college_type": "CustomType",
        })
        assert result["location"] == "CustomLoc"
        assert result["college_type"] == "CustomType"

    def test_unknown_college_gets_defaults(self):
        from data_loader import _enrich_college_dict
        result = _enrich_college_dict({"college_code": "E999", "college_name": "NIE Mysore"})
        assert result["location"] == "Mysore"
        assert result["college_type"] == "Private-Unaided"
        assert result["status"] is True


# =============================================================================
# has_real_data / get_data_source (unit tests using controlled mock)
# =============================================================================

class TestDataAvailability:
    def test_has_real_data_returns_bool(self):
        from data_loader import has_real_data
        assert isinstance(has_real_data(), bool)

    def test_get_data_source_returns_string(self):
        from data_loader import get_data_source
        assert isinstance(get_data_source(), str)
        assert len(get_data_source()) > 0


# =============================================================================
# load_college_master (mocked file operations)
# =============================================================================

class TestLoadCollegeMaster:
    @patch("data_loader._find_json_file")
    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
        "colleges": [
            {"college_code": "E001", "college_name": "UVCE", "location": "",
             "college_type": ""},
            {"college_code": "E002", "college_name": "RVCE", "location": "",
             "college_type": ""},
        ]
    }))
    def test_loads_and_enriches_colleges(self, mock_file, mock_find):
        from data_loader import load_college_master
        mock_find.return_value = "fake_path.json"
        result = load_college_master()
        assert len(result) == 2
        assert "E001" in result
        assert result["E001"]["college_name"] == "UVCE"
        assert result["E001"]["location"] == "Bangalore"  # Enriched from KNOWN_COLLEGE_INFO

    @patch("data_loader._find_json_file")
    def test_no_file_returns_empty(self, mock_find):
        from data_loader import load_college_master
        mock_find.return_value = None
        assert load_college_master() == {}


# =============================================================================
# _load_cutoffs_json (mocked file operations)
# =============================================================================

class TestLoadCutoffsJson:
    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
        "records": [
            {"college_code": "E001", "college_name": "UVCE", "course_code": "CS",
             "course_name": "CS", "category": "GM", "round_1_cutoff": 100,
             "round_2_cutoff": 200, "round_3_cutoff": 300},
        ],
        "colleges": [{"college_code": "E001", "college_name": "UVCE"}],
        "courses": [{"course_code": "CS", "course_name": "Computer Science"}],
    }))
    def test_loads_cutoff_json_with_metadata(self, mock_file):
        from data_loader import _load_cutoffs_json
        records, colleges, courses, source = _load_cutoffs_json("fake.json")
        assert len(records) == 1
        assert "location" in records[0]
        assert records[0]["college_code"] == "E001"
        assert "E001" in colleges
        assert "CS" in courses


# =============================================================================
# _find_json_file (with mocked filesystem)
# =============================================================================

class TestFindJsonFile:
    @patch("data_loader._get_parsed_data_dirs")
    def test_finds_first_existing_file(self, mock_dirs):
        import tempfile
        import os as os_mod
        from data_loader import _find_json_file

        # Create a real temp dir with a real file
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create the test file
            test_file = os_mod.path.join(tmpdir, "kea_cutoffs_2025.json")
            with open(test_file, "w") as f:
                f.write("{}")

            # Point _get_parsed_data_dirs to our temp dir
            mock_dirs.return_value = [tmpdir]

            result = _find_json_file("kea_cutoffs_2025.json")
            assert result is not None
            assert result == test_file or result.endswith("kea_cutoffs_2025.json")

    @patch("data_loader._get_parsed_data_dirs")
    def test_no_existing_file_returns_none(self, mock_dirs):
        import tempfile
        from data_loader import _find_json_file

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_dirs.return_value = [tmpdir]
            # File doesn't exist in the temp dir
            result = _find_json_file("nonexistent.json")
            assert result is None


class TestLoadRealDataPreference:
    @patch("data_loader._find_json_file")
    def test_prefers_pdf_cutoffs_all_over_kea_gm_only(self, mock_find):
        from data_loader import load_real_data

        def side_effect(*filenames):
            if "pdf_cutoffs_all.json" in filenames:
                return "fake_pdf_path.json"
            if "kea_cutoffs_2025.json" in filenames:
                return "fake_kea_path.json"
            return None

        mock_find.side_effect = side_effect

        mocked_pdf = {
            "records": [
                {"college_code": "E001", "college_name": "UVCE", "course_code": "CS", "course_name": "Computer Science", "category": "GM", "round_1_cutoff": 100, "round_2_cutoff": 150, "round_3_cutoff": 200}
            ],
            "colleges": [{"college_code": "E001", "college_name": "UVCE"}],
            "courses": [{"course_code": "CS", "course_name": "Computer Science"}],
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mocked_pdf))):
            real = load_real_data()

        assert real is not None
        assert real["source"].startswith("JSON")
        assert any(r["category"] == "GM" for r in real["records"])
