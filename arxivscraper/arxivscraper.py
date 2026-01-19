"""
A python program to retreive recrods from ArXiv.org in given
categories and specific date range.

Author: Mahdi Sadjadi (sadjadi.seyedmahdi[AT]gmail[DOT]com).
"""

from __future__ import print_function

import datetime
import sys
import time
import xml.etree.ElementTree as ET
from typing import Dict, List

PYTHON3 = sys.version_info[0] == 3
if PYTHON3:
    from urllib.error import HTTPError
    from urllib.parse import urlencode
    from urllib.request import urlopen
else:
    from urllib import urlencode
    from urllib2 import HTTPError, urlopen

from .constants import ARXIV, BASE, OAI, cats, subcats


class Record(object):
    """
    A class to hold a single record from ArXiv
    Each records contains the following properties:

    object should be of xml.etree.ElementTree.Element.
    """

    def __init__(self, xml_record):
        """if not isinstance(object,ET.Element):
        raise TypeError("")"""
        self.xml = xml_record
        self.id = self._get_text(ARXIV, "id")
        self.url = "https://arxiv.org/abs/" + self.id
        self.title = self._get_text(ARXIV, "title")
        self.abstract = self._get_text(ARXIV, "abstract")
        self.cats = self._get_text(ARXIV, "categories")
        self.created = self._get_text(ARXIV, "created")
        self.updated = self._get_text(ARXIV, "updated")
        self.doi = self._get_text(ARXIV, "doi")
        self.authors = self._get_authors()
        self.affiliation = self._get_affiliation()

    def _get_text(self, namespace: str, tag: str) -> str:
        """Extracts text from an xml field"""
        try:
            return (
                self.xml.find(namespace + tag).text.strip().lower().replace("\n", " ")
            )
        except:
            return ""

    def _get_name(self, parent, attribute) -> str:
        """Extracts author name from an xml field"""
        try:
            return parent.find(ARXIV + attribute).text.lower()
        except:
            return "n/a"

    def _get_authors(self) -> List:
        """Extract name of authors"""
        authors_xml = self.xml.findall(ARXIV + "authors/" + ARXIV + "author")
        last_names = [self._get_name(author, "keyname") for author in authors_xml]
        first_names = [self._get_name(author, "forenames") for author in authors_xml]
        full_names = [a + " " + b for a, b in zip(first_names, last_names)]
        return full_names

    def _get_affiliation(self) -> str:
        """Extract affiliation of authors"""
        authors = self.xml.findall(ARXIV + "authors/" + ARXIV + "author")
        try:
            affiliation = [
                author.find(ARXIV + "affiliation").text.lower() for author in authors
            ]
            return affiliation
        except:
            return []

    def output(self) -> Dict:
        """Data for each paper record"""
        d = {
            "title": self.title,
            "id": self.id,
            "abstract": self.abstract,
            "categories": self.cats,
            "doi": self.doi,
            "created": self.created,
            "updated": self.updated,
            "authors": self.authors,
            "affiliation": self.affiliation,
            "url": self.url,
        }
        return d


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
        Waiting time between subsequent calls to API, triggred by Error 503.
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
        date_from: str = None,
        date_until: str = None,
        t: int = 30,
        timeout: int = 300,
        filters: Dict[str, str] = {},
    ):
        self.cat = str(category)
        self._validate_category(self.cat)
        self.t = t
        self.timeout = timeout
        DateToday = datetime.date.today()
        if date_from is None:
            self.f = str(DateToday.replace(day=1))
        else:
            self.f = date_from
        if date_until is None:
            self.u = str(DateToday)
        else:
            self.u = date_until
        
        # Format category for OAI-PMH API
        # Convert cs:SE or cs.SE to cs:cs:SE format required by arXiv OAI-PMH API
        oai_category = self._format_category_for_oai(self.cat)
        
        self.url = (
            BASE
            + "from="
            + self.f
            + "&until="
            + self.u
            + "&metadataPrefix=arXiv&set=%s" % oai_category
        )
        self.filters = filters
        if not self.filters:
            self.append_all = True
        else:
            self.append_all = False
            self.keys = filters.keys()

    def _validate_category(self, category: str) -> None:
        """Validate that the category is a valid arXiv category.
        
        Accepts formats:
        - Base categories: 'cs', 'cond-mat', 'physics', etc.
        - Subcategories: 'cs.SE', 'cs:SE', 'cond-mat.soft', etc.
        - Legacy format: 'physics:cond-mat', 'physics:astro-ph', etc.
        """
        # Check if it's just a base category (no separator)
        if category in cats:
            return
        
        # Handle legacy physics: format (e.g., physics:cond-mat, physics:astro-ph)
        if category.startswith("physics:"):
            subcat = category[8:]  # Remove "physics:" prefix
            # Check if it's a valid physics-related base category
            physics_related = {
                'astro-ph', 'cond-mat', 'gr-qc', 'hep-ex', 'hep-lat', 'hep-ph',
                'hep-th', 'math-ph', 'nlin', 'nucl-ex', 'nucl-th', 'quant-ph'
            }
            if subcat in physics_related:
                return
        
        # Check if it's a subcategory with colon or dot separator
        for base in cats:
            if category.startswith(base + "."):
                subcat_full = category[len(base) + 1:]
                subcat_name = base + "." + subcat_full
                valid_subcats = subcats.get(base, [])
                if subcat_name in valid_subcats:
                    return
            elif category.startswith(base + ":"):
                subcat_full = category[len(base) + 1:]
                # Check with dot notation (arXiv stores as base.subcat)
                subcat_name = base + "." + subcat_full
                valid_subcats = subcats.get(base, [])
                if subcat_name in valid_subcats:
                    return
        
        # If we get here, the category is invalid
        available = ", ".join(sorted(cats))
        raise ValueError(
            f"Invalid category: '{category}'. "
            f"Valid base categories are: {available}. "
            f"Use format 'category', 'category:subcategory', 'category.subcategory', or legacy 'physics:subcategory'."
        )
    
    def _format_category_for_oai(self, category: str) -> str:
        """Format category for arXiv OAI-PMH API.
        
        Converts user-friendly format (cs.SE or cs:SE) to OAI-PMH format.
        - Base category in main fields (cs, math, etc.) -> base_category:base_category
        - Physics subcategories (astro-ph, cond-mat, etc.) -> physics:subcategory
        - Legacy physics format (physics:cond-mat) -> already formatted, return as-is
        - Other subcategories (cs.SE) -> base:base:subcat
        """
        # Special handling for physics-related base categories that need physics: prefix
        physics_related = {
            'astro-ph': 'physics:astro-ph',
            'cond-mat': 'physics:cond-mat',
            'gr-qc': 'physics:gr-qc',
            'hep-ex': 'physics:hep-ex',
            'hep-lat': 'physics:hep-lat',
            'hep-ph': 'physics:hep-ph',
            'hep-th': 'physics:hep-th',
            'math-ph': 'physics:math-ph',
            'nlin': 'physics:nlin',
            'nucl-ex': 'physics:nucl-ex',
            'nucl-th': 'physics:nucl-th',
            'quant-ph': 'physics:quant-ph',
        }
        
        if category in physics_related:
            return physics_related[category]
        
        # Handle legacy physics: format (already correct for OAI-PMH)
        if category.startswith("physics:"):
            return category
        
        # Base categories like cs, math, stat, etc. need category:category format
        if category in cats:
            return f"{category}:{category}"
        
        # Handle colon or dot separated subcategories
        for base in cats:
            if category.startswith(base + "."):
                subcat = category[len(base) + 1:]
                return f"{base}:{base}:{subcat}"
            elif category.startswith(base + ":"):
                subcat = category[len(base) + 1:]
                return f"{base}:{base}:{subcat}"
        
        # Fallback (shouldn't reach here if _validate_category passed)
        return category

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
                    to = int(e.hdrs.get("retry-after", 30))
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
                return ds
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


def search_all(df, col, *words):
    """
    Return a sub-DataFrame of those rows whose Name column match all the words.
    source: https://stackoverflow.com/a/22624079/3349443
    """
    import numpy as np

    return df[np.logical_and.reduce([df[col].str.contains(word) for word in words])]
