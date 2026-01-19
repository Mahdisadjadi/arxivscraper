[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.889853.svg)](https://doi.org/10.5281/zenodo.889853)
![](https://github.com/mahdisadjadi/arxivscraper/workflows/CI/badge.svg)
![](https://github.com/mahdisadjadi/arxivscraper/workflows/Publish%20to%20PyPi/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# arXivScraper
An ArXiV scraper to retrieve records from given categories and date range.

## Install

Use `pip` (or `pip3` for python3):

```bash
$ pip install arxivscraper
```

or download the source and use `setup.py`:

```bash
$ python setup.py install
```

To update the module using `pip`:
```bash
pip install arxivscraper --upgrade
```

## Usage

### Basic Example

Import `arxivscraper` and create a scraper to fetch preprints from a category within a date range:

```python
import arxivscraper

scraper = arxivscraper.Scraper(
    category='cond-mat',
    date_from='2017-05-27',
    date_until='2017-06-07'
)
output = scraper.scrape()
```

### Parameters

The `Scraper` class accepts the following parameters:

- `category` (str): The arXiv category code (e.g., `'cs'`, `'math'`, `'cond-mat'`, `'stat'`, etc.). Supports both base categories and subcategories in multiple formats:
  - Base categories: `'cs'`, `'math'`, `'stat'`, etc.
  - Subcategories with dot notation: `'cs.AI'`, `'cs.SE'`, etc.
  - Subcategories with colon notation: `'cs:AI'`, `'stat:ML'`, etc.
  - Physics legacy format: `'physics:cond-mat'`, `'physics:astro-ph'`, etc.

- `date_from` (str, optional): Starting date in format `'YYYY-MM-DD'`. Defaults to the first day of the current month.

- `date_until` (str, optional): End date in format `'YYYY-MM-DD'`. Defaults to today's date.

- `t` (int, optional): Waiting time in seconds between retries on HTTP 503 errors. Default: `30`.

- `timeout` (int, optional): Maximum time in seconds for the entire scraping operation. Default: `300`.

- `filters` (dict, optional): Dictionary to filter results. Keys can be: `'title'`, `'abstract'`, `'author'`, `'categories'`, or `'affiliation'`. Values are lists of words to match (logical OR). Default: `{}` (no filtering).

### Output

The `scrape()` method returns a list of dictionaries. Each dictionary represents a paper with the following fields:

- `id`: arXiv ID
- `title`: Paper title
- `abstract`: Paper abstract
- `categories`: arXiv categories
- `authors`: List of author names
- `affiliation`: List of author affiliations
- `doi`: Digital Object Identifier
- `created`: Creation date
- `updated`: Last updated date
- `url`: URL to the paper on arXiv

Example with pandas DataFrame:

```python
import pandas as pd

output = scraper.scrape()
df = pd.DataFrame(output)
```

### Filtering Results

To filter results based on specific criteria, pass a `filters` dictionary. Filters use logical OR, so records matching any of the specified words in a filter key will be included:

```python
scraper = arxivscraper.Scraper(
    category='stat',
    date_from='2017-08-01',
    date_until='2017-08-10',
    filters={
        'categories': ['stat.ml'],
        'abstract': ['learning']
    }
)
output = scraper.scrape()
```

This will return papers in the Statistics category where either the category includes `'stat.ml'` OR the abstract contains `'learning'`.

## Contributing
Ideas/bugs/comments? Please open an issue or submit a pull request on Github.

## How to cite
If `arxivscraper` was useful in your work/research, please consider to cite it as :
```
Mahdi Sadjadi (2017). arxivscraper: Zenodo. http://doi.org/10.5281/zenodo.889853
```

or
```
@misc{msadjadi,
  author       = {Mahdi Sadjadi},
  title        = {arxivscraper},
  year         = 2017,
  doi          = {10.5281/zenodo.889853},
  url          = {https://doi.org/10.5281/zenodo.889853}
}
```

## Author
* **Mahdi Sadjadi**, 2017.

* Website: [mahdisadjadi.com](http://mahdisadjadi.com)

* Twitter: [@mahdisadjadi](http://twitter.com/MahdiSadjadi)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Categories
Here is a list of all categories available on ArXiv. For a complete list of subcategories, see [categories_v2.md](categories_v2.md).
To generate this table, see `arxivscraper/util/create_arxiv_category_markdown_table`.

| Category Code | Category |
|------|----------|
| `cs` | Computer Science |
| `econ` | Economics |
| `eess` | Electrical Engineering and Systems Science |
| `math` | Mathematics |
| `astro-ph` | Astrophysics |
| `cond-mat` | Condensed Matter |
| `gr-qc` | General Relativity and Quantum Cosmology |
| `hep-ex` | High Energy Physics - Experiment |
| `hep-lat` | High Energy Physics - Lattice |
| `hep-ph` | High Energy Physics - Phenomenology |
| `hep-th` | High Energy Physics - Theory |
| `math-ph` | Mathematical Physics |
| `nlin` | Nonlinear Sciences |
| `nucl-ex` | Nuclear Experiment |
| `nucl-th` | Nuclear Theory |
| `physics` | Physics (Other) |
| `quant-ph` | Quantum Physics |
| `q-bio` | Quantitative Biology |
| `q-fin` | Quantitative Finance |
| `stat` | Statistics |

## Start History

[![Star History Chart](https://api.star-history.com/svg?repos=Mahdisadjadi/arxivscraper&type=Date)](https://www.star-history.com/#Mahdisadjadi/arxivscraper&Date)
