# Make a markdown table from categories and subcategories of Arxiv.org
# originally posted as a gist
# https://gist.github.com/Mahdisadjadi/96970b043fcd94b8e5109fe8a7dbbd5e

from bs4 import BeautifulSoup
import requests
# url to scrape
cat_url = 'https://arxiv.org/'
subcat_url = 'https://arxiv.org/archive/'

def return_soup(url):
    url = requests.get(url).content
    soup = BeautifulSoup(url,"html.parser")
    return soup
    
def get_namespace(x):
    name = x.find('a').text
    tag = x.find('b').text
    return name, tag

def convert_to_markdown(*args):
    print (('|'+a for a in args))

    
main_page = return_soup(cat_url).find_all('li')    
    
print ('| Category | Code |  Subcategories | Subcode |\n| --- | --- | --- | --- |')
for x in main_page[0:]:
    try:
        xname,xtag = get_namespace(x)
        string = '| ' + xname + ' | `' + xtag + '` | '
        print (string)
        subcat_page = return_soup(subcat_url + xtag).find_all('ul')[-1].find_all('b')
        for y in subcat_page:
            subs = y.text.split(' - ')
            print ('| | | '+ subs[1] + ' | `' +  subs[0] + '`')
    except:
        pass