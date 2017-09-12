"""\
Provides a python package to get data of academic papers
posted at arXiv.org in a specific date range and category.

Collected data:

        Title,
        ID,
        Authors,
        Abstract,
        Subcategories,
        DOI,
        Created (date),
        Updated (date)
"""

import sys
try:
    from setuptools import setup
except ImportError:
    sys.exit("""Error: Setuptools is required for installation.
 -> http://pypi.python.org/pypi/setuptools""")

setup(
    name = "arxivscraper",
    version = "0.0.2",
    description = "Get arXiv.org metadate within a date range and category",
    author = "Mahdi Sadjadi",
    author_email = "sadjadi.seyedmahdi@gmail.com",
    url = "https://github.com/Mahdisadjadi/arxivscraper",
    download_url = 'https://github.com/Mahdisadjadi/arxivscraper/archive/0.0.2.tar.gz',
    py_modules = [""],
    keywords = ["arxiv", "scraper", "api", "citation"],
    license = "MIT",
    classifiers = [
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Text Processing :: Markup :: LaTeX",
        ],
)
