import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import arxivscraper


class TestCategoryValidation:
    """Test category validation in Scraper initialization."""

    def test_valid_base_category(self):
        """Test that valid base categories are accepted."""
        valid_categories = ["cs", "physics", "math", "stat", "econ", "eess"]
        for cat in valid_categories:
            # Should not raise an error
            scraper = arxivscraper.Scraper(
                category=cat, date_from="2025-01-01", date_until="2025-01-02"
            )
            assert scraper.cat == cat

    def test_valid_subcategory(self):
        """Test that valid subcategories are accepted."""
        valid_subcats = [
            "cs:SE",
            "cs.SE",
            "cond-mat:soft",
            "cond-mat.soft",
            "stat.ML",
            "econ.EM",
            "eess.SY",
        ]
        for subcat in valid_subcats:
            # Should not raise an error
            scraper = arxivscraper.Scraper(
                category=subcat, date_from="2025-01-01", date_until="2025-01-02"
            )
            assert scraper.cat == subcat

    def test_invalid_category_raises_error(self):
        """Test that invalid categories raise ValueError."""
        invalid_categories = ["cs:INVALID", "foo", "cs.INVALID", "invalid:cat"]
        for cat in invalid_categories:
            with pytest.raises(ValueError) as exc_info:
                arxivscraper.Scraper(
                    category=cat, date_from="2025-01-01", date_until="2025-01-02"
                )
            assert "Invalid category" in str(exc_info.value)

    def test_cs_se_category_specifically(self):
        """Test that cs:SE (the category from the issue) is now recognized."""
        # This should not raise an error
        scraper = arxivscraper.Scraper(
            category="cs:SE", date_from="2025-01-01", date_until="2025-01-02"
        )
        assert scraper.cat == "cs:SE"

    def test_error_message_helpful(self):
        """Test that error message lists available categories."""
        with pytest.raises(ValueError) as exc_info:
            arxivscraper.Scraper(
                category="invalid_cat",
                date_from="2025-01-01",
                date_until="2025-01-02",
            )
        error_msg = str(exc_info.value)
        # Should mention valid categories
        assert "Valid base categories" in error_msg
        assert "cs" in error_msg
        assert "math" in error_msg
