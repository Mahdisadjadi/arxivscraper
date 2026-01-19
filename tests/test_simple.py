import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import arxivscraper


def test_main():
    """Test main function. Should return results as a list."""
    scraper = arxivscraper.Scraper(
        category="cs.SE", date_from="2025-01-01", date_until="2025-01-05"
    )

    output = scraper.scrape()
    assert len(output) == 22, "Result should not be empty!"
    assert type(output) == list, "Result is not a list!"

    # Check that output contains the expected fields
    assert "title" in output[0]
    assert "id" in output[0]
    assert "abstract" in output[0]
