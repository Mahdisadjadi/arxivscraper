import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import arxivscraper


def test_main():
    """Test main function. The output should 97 entries."""
    scraper = arxivscraper.Scraper(
        category="physics:cond-mat", date_from="2017-05-27", date_until="2017-05-30"
    )

    output = scraper.scrape()
    assert len(output) == 97, "Result is not 97!"
    assert type(output) == list, "Result is not a list!"
