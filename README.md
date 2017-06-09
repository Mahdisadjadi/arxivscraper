# arxivscraper
An ArXiV scraper to retrieve records from given categories and date range

## Install

Use pip:

```bash
$ pip3 install arxivscraper
```

or download the source and use `setup.py`:

```bash
$ python setup.py install
```

or if you do not want to install, you can copy `arxivscraper.py` into your working
directory.

## Usage

### In script

You can directly use `arxivscraper` in your scripts. Let's import `arxivscraper`
and create a scraper to fetch all eprints in condensed matter physics category
from 27 May 2017 until 7 June 2017:

```python
import arxivscraper
scraper = arxivscraper.Scraper(category='physics:cond-mat', date_from='2017-05-27',date_until='2017-06-07',t=30)
```
Once we built an instance of the scraper, we can start the scraping:

```python
output = scraper.scrape()
```
While scraper is running, it prints its status:

```
fetching up to  1000 records...
fetching up to  2000 records...
Got 503. Retrying after 30 seconds.
fetching up to  3000 records...
fetching is complete.
```

Finally you can save the output in your favorite format or readily convert it into a pandas dataframe:
```python
import pandas as pd
cols = ('id', 'title', 'categories', 'abstract', 'doi', 'created', 'updated', 'authors')
df = pd.DataFrame(output,columns=cols)
```

## Author
Mahdi Sadjadi, 2017.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
