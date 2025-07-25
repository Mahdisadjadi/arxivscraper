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

## Examples

### Without filtering

You can directly use `arxivscraper` in your scripts. Let's import `arxivscraper`
and create a scraper to fetch all preprints in condensed matter physics category
from 27 May 2017 until 7 June 2017 (for other categories, see below):

```python
import arxivscraper
scraper = arxivscraper.Scraper(category='physics:cond-mat', date_from='2017-05-27',date_until='2017-06-07')
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

### With filtering
To have more control over the output, you could supply a dictionary to filter out the results. As an example, let's collect all preprints related to machine learning. This subcategory (`stat.ML`) is part of the statistics (`stat`) category. In addition, we want those preprints that word `learning` appears in their abstract.

```python
import arxivscraper.arxivscraper as ax
scraper = ax.Scraper(category='stat',date_from='2017-08-01',date_until='2017-08-10',t=10, filters={'categories':['stat.ml'],'abstract':['learning']})
output = scraper.scrape()
```

> In addition to `categories` and `abstract`, other available keys for `filters` are: `author` and `title`.

> Note that filters are based on logical OR and not mutually exclusive. So if the specified word appears in the abstract,
the record will be saved even if it doesn't have the specified categories.

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
| `physics` | Physics |
| `physics:astro-ph` | Astrophysics |
| `physics:cond-mat` | Condensed Matter |
| `physics:gr-qc` | General Relativity and Quantum Cosmology |
| `physics:hep-ex` | High Energy Physics - Experiment |
| `physics:hep-lat` | High Energy Physics - Lattice |
| `physics:hep-ph` | High Energy Physics - Phenomenology |
| `physics:hep-th` | High Energy Physics - Theory |
| `physics:math-ph` | Mathematical Physics |
| `physics:nlin` | Nonlinear Sciences |
| `physics:nucl-ex` | Nuclear Experiment |
| `physics:nucl-th` | Nuclear Theory |
| `physics:physics` | Physics (Other) |
| `physics:quant-ph` | Quantum Physics |
| `q-bio` | Quantitative Biology |
| `q-fin` | Quantitative Finance |
| `stat` | Statistics |

## Start History

[![Star History Chart](https://api.star-history.com/svg?repos=Mahdisadjadi/arxivscraper&type=Date)](https://www.star-history.com/#Mahdisadjadi/arxivscraper&Date)
