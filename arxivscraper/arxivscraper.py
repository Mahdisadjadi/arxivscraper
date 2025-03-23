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
from urllib.request import urlopen

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from constants import ARXIV, BASE, DEFAULT_RETRY_DELAY, DEFAULT_TIMEOUT, OAI
from record import Record


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
        filters: Dict[str, str] = {},
    ):
        self.cat = str(category)
        self.t = t
        self.timeout = timeout

        # Set the date range
        DateToday = datetime.date.today()
        if date_from is None:
            self.f = str(DateToday.replace(day=1))
        else:
            self.f = date_from
        if date_until is None:
            self.u = str(DateToday)
        else:
            self.u = date_until

        # Create URL
        self.url = (
            BASE
            + "from="
            + self.f
            + "&until="
            + self.u
            + "&metadataPrefix=arXiv&set=%s" % self.cat
        )

        self.filters = filters
        if not self.filters:
            self.append_all = True
        else:
            self.append_all = False
            self.keys = filters.keys()

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
