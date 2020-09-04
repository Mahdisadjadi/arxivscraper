"""
A python program to retreive recrods from ArXiv.org in given
categories and specific date range.

Author: Mahdi Sadjadi (sadjadi.seyedmahdi[AT]gmail[DOT]com).
"""
from __future__ import print_function
import xml.etree.ElementTree as ET
import datetime
import time
import sys
PYTHON3 = sys.version_info[0] == 3
if PYTHON3:
    from urllib.parse import urlencode
    from urllib.request import urlopen
    from urllib.error import HTTPError
else:
    from urllib import urlencode
    from urllib2 import HTTPError, urlopen
OAI = '{http://www.openarchives.org/OAI/2.0/}'
ARXIV = '{http://arxiv.org/OAI/arXiv/}'
BASE = 'http://export.arxiv.org/oai2?verb=ListRecords&'

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
        self.id = self._get_text(ARXIV, 'id')
        self.url = 'https://arxiv.org/abs/' + self.id
        self.title = self._get_text(ARXIV, 'title')
        self.abstract = self._get_text(ARXIV, 'abstract')
        self.cats = self._get_text(ARXIV, 'categories')
        self.created = self._get_text(ARXIV, 'created')
        self.updated = self._get_text(ARXIV, 'updated')
        self.doi = self._get_text(ARXIV, 'doi')
        self.authors = self._get_authors()
        self.affiliation = self._get_affiliation()

    def _get_text(self, namespace, tag):
        """Extracts text from an xml field"""
        try:
            return self.xml.find(namespace + tag).text.strip().lower().replace('\n', ' ')
        except:
            return ''
        
    def _get_name(self, parent, attribute):
        try: 
            return parent.find(ARXIV + attribute).text.lower()
        except:
            return "n/a"

    def _get_authors(self):
        authors_xml = self.xml.findall('./metadata/*/' + ARXIV + 'authors/' + ARXIV + 'author')
        last_names = [self._get_name(author, 'keyname') for author in authors_xml]
        first_names = [self._get_name(author, 'forenames') for author in authors_xml]
        full_names = [a+' '+b for a,b in zip(first_names, last_names)]
        return full_names

    def _get_affiliation(self):
        authors = self.xml.findall(ARXIV + 'authors/' + ARXIV + 'author')
        try:
            affiliation = [author.find(ARXIV + 'affiliation').text.lower() for author in authors]
            return affiliation
        except:
            return []

    def output(self):
        d = {
            'title': self.title,
            'id': self.id,
            'abstract': self.abstract,
            'categories': self.cats,
            'doi': self.doi,
            'created': self.created,
            'updated': self.updated,
            'authors': self.authors,
            'affiliation': self.affiliation,
            'url': self.url
             }
        return d


class Scraper(object):
    """
    A class to hold info about attributes of scraping,
    such as date range, categories, and number of returned
    records. If `from` is not provided, the first day of
    the current month will be used. If `until` is not provided,
    the current day will be used.

    Paramters
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
    Returning all eprints from

    ```
        import arxivscraper.arxivscraper as ax
        scraper = ax.Scraper(category='stat',date_from='2017-12-23',date_until='2017-12-25',t=10,
                 filters={'affiliation':['facebook'],'abstract':['learning']})
        output = scraper.scrape()
    ```
    """

    def __init__(self, category, date_from=None, date_until=None, t=30, timeout=300, filters={}):
        self.cat = str(category)
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
        self.url = BASE + 'from=' + self.f + '&until=' + self.u + '&metadataPrefix=arXiv&set=%s' % self.cat
        self.filters = filters
        if not self.filters:
            self.append_all = True
        else:
            self.append_all = False
            self.keys = filters.keys()

    def scrape(self):
        t0 = time.time()
        tx = time.time()
        elapsed = 0.0
        url = self.url
        ds = []
        k = 1
        while True:

            print('fetching up to ', 1000 * k, 'records...')
            try:
                response = urlopen(url)
            except HTTPError as e:
                if e.code == 503:
                    to = int(e.hdrs.get('retry-after', 30))
                    print('Got 503. Retrying after {0:d} seconds.'.format(self.t))
                    time.sleep(self.t)
                    continue
                else:
                    raise
            k += 1
            xml = response.read()
            root = ET.fromstring(xml)
            records = root.findall(OAI + 'ListRecords/' + OAI + 'record')
            for record in records:
                meta = record.find(OAI + 'metadata').find(ARXIV + 'arXiv')
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
                token = root.find(OAI + 'ListRecords').find(OAI + 'resumptionToken')
            except:
                return 1
            if token is None or token.text is None:
                break
            else:
                url = BASE + 'resumptionToken=%s' % token.text

            ty = time.time()
            elapsed += (ty-tx)
            if elapsed >= self.timeout:
                break
            else:
                tx = time.time()

        t1 = time.time()
        print('fetching is completed in {0:.1f} seconds.'.format(t1 - t0))
        print ('Total number of records {:d}'.format(len(ds)))
        return ds


def search_all(df, col, *words):
    """
    Return a sub-DataFrame of those rows whose Name column match all the words.
    source: https://stackoverflow.com/a/22624079/3349443
    """
    return df[np.logical_and.reduce([df[col].str.contains(word) for word in words])]


cats = [
 'astro-ph', 'cond-mat', 'gr-qc', 'hep-ex', 'hep-lat', 'hep-ph', 'hep-th',
 'math-ph', 'nlin', 'nucl-ex', 'nucl-th', 'physics', 'quant-ph', 'math', 'CoRR', 'q-bio',
 'q-fin', 'stat']
subcats = {'cond-mat': ['cond-mat.dis-nn', 'cond-mat.mtrl-sci', 'cond-mat.mes-hall',
              'cond-mat.other', 'cond-mat.quant-gas', 'cond-mat.soft', 'cond-mat.stat-mech',
              'cond-mat.str-el', 'cond-mat.supr-con'],
 'hep-th': [],'hep-ex': [],'hep-ph': [],
 'gr-qc': [],'quant-ph': [],'q-fin': ['q-fin.CP', 'q-fin.EC', 'q-fin.GN',
           'q-fin.MF', 'q-fin.PM', 'q-fin.PR', 'q-fin.RM', 'q-fin.ST', 'q-fin.TR'],

 'nucl-ex': [],'CoRR': [],'nlin': ['nlin.AO', 'nlin.CG', 'nlin.CD', 'nlin.SI',
          'nlin.PS'],
 'physics': ['physics.acc-ph', 'physics.app-ph', 'physics.ao-ph',
             'physics.atom-ph', 'physics.atm-clus', 'physics.bio-ph', 'physics.chem-ph',
             'physics.class-ph', 'physics.comp-ph', 'physics.data-an', 'physics.flu-dyn',
             'physics.gen-ph', 'physics.geo-ph', 'physics.hist-ph', 'physics.ins-det',
             'physics.med-ph', 'physics.optics', 'physics.ed-ph', 'physics.soc-ph',
             'physics.plasm-ph', 'physics.pop-ph', 'physics.space-ph'],
 'math-ph': [],
 'math': ['math.AG', 'math.AT', 'math.AP', 'math.CT', 'math.CA', 'math.CO',
          'math.AC', 'math.CV', 'math.DG', 'math.DS', 'math.FA', 'math.GM', 'math.GN',
          'math.GT', 'math.GR', 'math.HO', 'math.IT', 'math.KT', 'math.LO', 'math.MP',
          'math.MG', 'math.NT', 'math.NA', 'math.OA', 'math.OC', 'math.PR', 'math.QA',
          'math.RT', 'math.RA', 'math.SP', 'math.ST', 'math.SG'],
 'q-bio': ['q-bio.BM',
           'q-bio.CB', 'q-bio.GN', 'q-bio.MN', 'q-bio.NC', 'q-bio.OT', 'q-bio.PE', 'q-bio.QM',
           'q-bio.SC', 'q-bio.TO'],
 'nucl-th': [],'stat': ['stat.AP', 'stat.CO', 'stat.ML',
          'stat.ME', 'stat.OT', 'stat.TH'],
 'hep-lat': [],'astro-ph': ['astro-ph.GA',
              'astro-ph.CO', 'astro-ph.EP', 'astro-ph.HE', 'astro-ph.IM', 'astro-ph.SR']
 }
