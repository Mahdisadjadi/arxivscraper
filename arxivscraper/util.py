# %%

import time
import urllib.request
import xml.etree.ElementTree as ET
from urllib.error import HTTPError, URLError


def get_oai_url(verb):
    """
    Returns the base URL for the OAI-PMH API

    Parameters
    ---------
    verb: str
        The OAI-PMH verb to use

    Returns
    -------
    str
        The base URL for the OAI-PMH API

    """
    return "http://export.arxiv.org/oai2?verb={verb}&".format(verb=verb)


def get_arxiv_sets():
    """
    Retrieves the sets from the arXiv OAI-PMH endpoint using urllib.

    Parameters:
    -----------


    Returns:
    --------
    sets: list of dict or None
        A list of dictionaries, where each dictionary represents a set
        and contains keys like 'setSpec' and 'setName', or None if an error occurs.
    """

    # Construct the URL
    url = get_oai_url("ListSets")

    try:
        with urllib.request.urlopen(url) as response:
            # Check for HTTP errors
            if response.getcode() != 200:
                print(f"HTTP Error: {response.getcode()} - {response.reason}")
                return None

            # Read the response content
            response_content = response.read()

        # Parse the XML response
        root = ET.fromstring(response_content)

        sets = []
        for set_element in root.findall(".//{http://www.openarchives.org/OAI/2.0/}set"):
            set_data = {}
            for child in set_element:
                # Extract the tag name without the namespace
                tag = child.tag.split("}")[-1]
                set_data[tag] = child.text
            sets.append(set_data)

        return sets

    except URLError as e:
        print(f"Error during URL retrieval: {e}")
        return None
    except HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        return None
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None


def check_category_supported(category):
    """
    Checks if a given category is supported by the arXiv API.

    Parameters:
    -----------
    category: str
        The category to check.

    Returns:
    --------
    bool
        True if the category is supported, False otherwise.
    """

    data = get_arxiv_sets()

    if data is None:
        return False

    # Check if the category is in the list of supported categories
    for item in data:
        if item.get("setSpec") == category:
            return True

    return False


def create_arxiv_category_markdown_table():
    """
    Generates a markdown table from a list of dictionaries.

    Parameters:
    -----------

    Returns:
    --------
    str
        A string containing the markdown table.
    """

    data = get_arxiv_sets()

    # Initialize the table header
    table = "| Code | Category |\n"
    table += "|------|----------|\n"

    # Add rows for each item in the data
    for item in data:
        code = item.get("setSpec", "")  # Handle potential missing keys
        category = item.get("setName", "")
        table += f"| `{code}` | {category} |\n"

    return table


# %%
