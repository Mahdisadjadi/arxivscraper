from typing import Dict, List

from .constants import ARXIV


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

    def _get_authors(self) -> List[str]:
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
