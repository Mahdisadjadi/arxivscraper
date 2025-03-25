"""
This module provides a class `Scraper` to scrape ArXiv.org
for eprints in a specific category and date range. The
scraper can also filter the results based on the title,
abstract, authors, and affiliations. The results are
returned as a list of dictionaries.

Author: Mahdi Sadjadi (sadjadi.seyedmahdi[AT]gmail[DOT]com).
Last update: March 2025
"""

import argparse
import datetime
import os
import sys
import time
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

from .constants import (
    ARXIV,
    BASE,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    OAI,
)
from .record import Record
from .util import check_category_supported


class Scraper(object):
    """
    A class to hold info about attributes of scraping,
    such as date range, categories, and number of returned
    records. If `from` is not provided, the first day of
    the current month will be used. If `until` is not provided,
    the current day will be used.

    Parameters
    ---------
    category: str
        The category of scraped records
    data_from: str
        starting date in format 'YYYY-MM-DD'. Updated eprints are included even if
        they were created outside of the given date range. Default: first day of current month.
    date_until: str
        final date in format 'YYYY-MM-DD'. Updated eprints are included even if
        they were created outside of the given date range. Default: today.
    t: int
        Waiting time between subsequent calls to API, triggered by Error 503.
    timeout: int
        Timeout in seconds after which the scraping stops. Default: 300s
    retry_attempts: int
        Number of retry attempts in case of an error. Default: 5
    filter: dictionary
        A dictionary where keys are used to limit the saved results. Possible keys:
        subcats, author, title, abstract. See the example, below.

    Example:
    Returning all eprints from `stat` category:

    ```
        import arxivscraper.arxivscraper as ax
        scraper = ax.Scraper(category='stat',date_from='2017-12-23',date_until='2017-12-25',t=10,
                 filters={'affiliation':['facebook'],'abstract':['learning']})
        output = scraper.scrape()
    ```
    """

    def __init__(
        self,
        category: str,
        date_from: Optional[str] = None,
        date_until: Optional[str] = None,
        t: int = DEFAULT_RETRY_DELAY,
        timeout: int = DEFAULT_TIMEOUT,
        retry_attempts: int = DEFAULT_RETRY_ATTEMPTS,
        filters: Dict[str, List[str]] = {},
    ):

        self.cat = str(category)
        self.t = t
        self.retry_delay = t
        self.timeout = timeout
        self.retry_attempts = retry_attempts

        if not check_category_supported(category):
            raise ValueError(
                f"The category `{category}` doesn't exist in arXiv taxonomy."
            )

        # Set the date range
        DateToday = datetime.date.today()
        self.f = date_from if date_from else str(DateToday.replace(day=1))
        self.u = date_until if date_until else str(DateToday)

        # Create URL
        query_params = {
            "from": self.f,
            "until": self.u,
            "metadataPrefix": "arXiv",
            "set": self.cat,
        }
        self.url = f"{BASE}{urlencode(query_params)}"

        self.filters = filters
        # all record should be appended?
        self.append_all = not self.filters
        self.keys = filters.keys() if filters else []

    def _fetch_xml(self, url: str) -> str:
        """Fetches the XML from the given URL with retry mechanism."""
        for attempt in range(self.retry_attempts):
            try:
                response = urlopen(url)
                return response.read()
            except HTTPError as e:
                if e.code == 503:
                    to = int(
                        e.hdrs.get("retry-after", self.retry_delay)
                    )  # Use retry_delay here
                    print("Got 503. Retrying after {0:d} seconds.".format(to))
                    time.sleep(to)  # Wait for the "retry-after" value
                    continue
                else:
                    print(
                        f"HTTP Error {e.code} during attempt {attempt + 1}/{self.retry_attempts}: {e}"
                    )
                    if attempt == self.retry_attempts - 1:
                        raise  # Re-raise the exception
                    sleep_time = self.retry_delay * (2**attempt)  # exponential backoff
                    print(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
            except Exception as e:  # Catch other potential errors
                print(f"Error during attempt {attempt + 1}/{self.retry_attempts}: {e}")
                if attempt == self.retry_attempts - 1:
                    raise
                sleep_time = self.retry_delay * (2**attempt)  # exponential backoff
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
        return ""  # Should not reach here, but added to avoid warning

    def _parse_records(self, xml_string: str) -> List[Dict]:
        """Parses the XML and extracts records."""
        try:
            root = ET.fromstring(xml_string)
            records = root.findall(OAI + "ListRecords/" + OAI + "record")
            extracted_records = []
            for record in records:
                meta = record.find(OAI + "metadata").find(ARXIV + "arXiv")
                if meta is None:
                    continue  # Skip records without arXiv metadata
                record_data = Record(meta).output()
                if self.append_all:
                    extracted_records.append(record_data)
                else:
                    if self._apply_filters(record_data):
                        extracted_records.append(record_data)
            return extracted_records
        except ET.ParseError as e:
            print(f"XML parsing error: {e}")
            return []

    def _apply_filters(self, record: Dict) -> bool:
        """Applies the filters to a single record."""
        for key in self.keys:
            if key not in record:
                continue  # Skip if the key isn't present in the record

            record_value = record[key]
            if not isinstance(record_value, str) and not isinstance(record_value, list):
                continue  # Filter only string or list attributes

            if isinstance(record_value, str):
                record_value = [record_value]  # make strings filterable

            for word in self.filters[key]:
                if any(word.lower() in val.lower() for val in record_value):
                    return True
        return False

    def _get_next_url(self, xml_string: str) -> Optional[str]:
        """Extracts the resumption token to get the next page of results."""
        try:
            root = ET.fromstring(xml_string)
            token = root.find(OAI + "ListRecords").find(OAI + "resumptionToken")
            if token is not None and token.text:
                return BASE + "?resumptionToken=%s" % token.text
            return None
        except ET.ParseError:
            return None

    def _scrape(self) -> List[Dict]:
        """Scrapes records from ArXiv."""
        t0 = time.time()
        all_records = []
        url = self.url

        while url:
            print(f"Fetching records from: {url}")
            try:
                xml_string = self._fetch_xml(url)
                if not xml_string:
                    print("No XML data received.")
                    break  # Exit if no data is received
                records = self._parse_records(xml_string)
                all_records.extend(records)
                url = self._get_next_url(xml_string)  # Get next page
            except Exception as e:
                print(f"Error during scraping: {e}")
                break  # Exit on error

        t1 = time.time()
        print(f"Fetching is completed in {t1 - t0:.1f} seconds.")
        print(f"Total number of records: {len(all_records)}")
        return all_records

    def scrape(self) -> List[Dict]:
        t0 = time.time()
        tx = time.time()
        elapsed = 0.0
        url = self.url
        ds = []
        k = 1
        while True:

            print("fetching up to ", 1000 * k, "records...")
            try:
                response = urlopen(url)
            except HTTPError as e:
                if e.code == 503:
                    to = int(e.hdrs.get("retry-after", DEFAULT_RETRY_DELAY))
                    print("Got 503. Retrying after {0:d} seconds.".format(self.t))
                    time.sleep(self.t)
                    continue
                else:
                    raise
            k += 1
            xml = response.read()
            root = ET.fromstring(xml)
            records = root.findall(OAI + "ListRecords/" + OAI + "record")
            for record in records:
                meta = record.find(OAI + "metadata").find(ARXIV + "arXiv")
                record = Record(meta).output()
                if self.append_all:
                    ds.append(record)
                else:
                    save_record = False
                    for key in self.keys:
                        for word in self.filters[key]:
                            if word.lower() in record[key]:
                                save_record = True

                    if save_record:
                        ds.append(record)

            try:
                token = root.find(OAI + "ListRecords").find(OAI + "resumptionToken")
            except:
                return 1
            if token is None or token.text is None:
                break
            else:
                url = BASE + "resumptionToken=%s" % token.text

            ty = time.time()
            elapsed += ty - tx
            if elapsed >= self.timeout:
                break
            else:
                tx = time.time()

        t1 = time.time()
        print("fetching is completed in {0:.1f} seconds.".format(t1 - t0))
        print("Total number of records {:d}".format(len(ds)))
        return ds


def get_arguments():
    parser = argparse.ArgumentParser(description="Scrape ArXiv for eprints")
    parser.add_argument(
        "--category",
        type=str,
        help="The category of scraped records",
        required=True,
    )
    parser.add_argument(
        "--date_from",
        type=str,
        help="starting date in format 'YYYY-MM-DD'",
        required=False,
        default=None,
    )
    parser.add_argument(
        "--date_until",
        type=str,
        help="final date in format 'YYYY-MM-DD'",
        required=False,
        default=None,
    )
    parser.add_argument(
        "--t",
        type=int,
        help="Waiting time between subsequent calls to API, triggered by Error 503",
        required=False,
        default=DEFAULT_RETRY_DELAY,
    )
    parser.add_argument(
        "--timeout",
        type=int,
        help="Timeout in seconds after which the scraping stops",
        required=False,
        default=DEFAULT_TIMEOUT,
    )
    parser.add_argument(
        "--filters",
        type=dict,
        help="A dictionary where keys are used to limit the saved results",
        required=False,
        default={},
    )
    return parser.parse_args()


# if __name__ == "__main__":
#     args = get_arguments()
#     scraper = Scraper(
#         category=args.category,
#         date_from=args.date_from,
#         date_until=args.date_until,
#         t=args.t,
#         timeout=args.timeout,
#         filters=args.filters,
#     )
#     output = scraper.scrape()
#     print(output)
