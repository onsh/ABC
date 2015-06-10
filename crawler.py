#!/use/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from pprint import pprint
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import sys
import re
import lxml
import time
import json
import random


def read_html(filename):
    with open(filename) as f:
        page = f.read()
    soup = BeautifulSoup(page)
    return soup


def clean_html(url):
    req = Request(url)
    req.add_header('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.78.2 (KHTML, like Gecko) Version/6.1.6 Safari/537.78.2')
    try:
        response = urlopen(req)
    except URLError as e:
        if hasattr(e, 'reason'):
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        elif hasattr(e, 'code'):
            print('The server could\'t fulfill the request.')
            print('Error code: ', e.code)
    else:
        # everything is fine
        page = response.read()
        soup = BeautifulSoup(page, "lxml")
        page.close()
    return soup
        

def get_next_page_url(soup, base_url):
    next_page_link = soup.find("a", class_="next-results-link")
    if next_page_link is None:
        next_page_url = None
    else:
        next_page_url = base_url + next_page_link.get("href")
    return next_page_url


def get_article_links(soup, base_url):
    '''
    Retrieve article links to prepare for
    getting more detail info of each articles.
    If the article has not an abstract page link,
    we get a reference page instead.
    '''
    
    article_links_list = []
    articles = soup.find_all('li', class_='results-cit')
    for article in articles:
        if article.find('a', rel='abstract'):
            abstract_link = article.find('a', rel='abstract')
            article_links_list.append(urljoin(base_url, abstract_link.get('href')))
        elif article.find('a', rel='references-only'):
            reference_link = article.find('a', rel='references-only')
            article_links_list.append(urljoin(base_url, reference_link.get('href')))
    # pprint(article_links_list)
    return article_links_list


def get_title(soup):
    ''' Get a title from an article '''
    
    h1_tag = soup.find('h1', id='article-title-1')
    title = h1_tag.string
    print(title)
    return title


def get_authors(soup):
    ''' Get authors list from an article '''
    
    authors_list = []
    for author in soup.find_all('a', class_='name-search'):
        author = author.string
        authors_list.append(author)
    
    for collab in soup.find_all('span', class_='collab'):
        collab = collab.string
        authors_list.append(collab)
        
    print(authors_list)
    return authors_list
        

def get_affiliation(soup):
    ''' Get authors' affiliations from an article '''
    
    aff_list = []
    for aff in soup.find_all(id=re.compile('^aff-')):
        num = aff.next_sibling.sup.string
        address = aff.next_sibling.contents[1].strip()
        aff_data = {'num' : int(num), 'address' : address}
        aff_list.append(json.dumps(aff_data))
    pprint(aff_list)
    return aff_list
    

def get_received_date(soup):
    ''' Get a received date of an article '''
    
    received = soup.find('li', class_='received')
    split_received = re.split(r'[,.\s]\s*', received.contents[1])
    month, date, year = split_received[:3]
    received_date ={'month': month,
                    'date': int(date),
                    'year': int(year)}
    print(json.dumps(received_date))
    return received_date


def get_abstract(soup):
    ''' Get an abstract of an article '''
    
    abstract = soup.find('p', id='p-1')
    abstract = abstract.string
    print(abstract)
    return abstract


def get_other_info(soup):
    ''' Get other article info of an article '''
    
    vol = soup.find('span', class_='slug-vol').string
    issue = soup.find('span', class_='slug-issue').string
    pages = soup.find('span', class_='slug-pages').string
    doi = soup.find('span', class_='slug-doi').string
    article_type = soup.find('a', class_='tocsection-search').string
    info = {'vol': vol.strip(),
            'issue': issue.strip(),
            'pages': pages.strip(),
            'doi': doi.strip(),
            'type': article_type.strip()}
    print(info)
    return info


def isAlphabetical(a0, a1):
    return a0.split()[-1].lower() < a1.split()[-1].lower()

   
def save2db(data):
    ''' Connect to MongoDB '''
    try:
        client = MongoClient('localhost', 27017)
    except ConnectionFailure as e:
        sys.stderr.write("Could not connect to MongoDB: {0}".format(e))
        sys.exit(1)

    # Get a Database handle to a database named "PTP"
    db = client.PTP
    # bulk insert
    db.articles.insert_many(data)


def main():
    base_url  = 'http://ptp.oxfordjournals.org/'
    url = "http://ptp.oxfordjournals.org/search?submit=yes&pubdate_year=&volume=&firstpage=&doi=&author1=&author2=&title=&andorexacttitle=and&titleabstract=&andorexacttitleabs=and&fulltext=&andorexactfulltext=and&journalcode=ptp&fmonth=&fyear=&tmonth=&tyear=&flag=&format=standard&hits=125&sortspec=reverse-date&submit=yes&submit=Search"


    # page = read_html('.html')
    page = clean_html(url)
    
    counter = 1
    continue_scrapping = True
    while continue_scrapping:
        next_page_link = get_next_page_url(page, base_url)
        if next_page_link is None:
            continue_scrapping = False
        else:
            article_links = get_article_links(page, base_url)
            for link in article_links:
                article = clean_html(link)
                article_info = {
                    'title' : get_title(article),
                    'authors' : get_authors(article),
                    'affiliation' : get_affiliation(article),
                    'date' : get_received_date(article),
                    'abstract' : get_abstract(article),
                    'info' : get_other_info(article)
                }
                print(json.dumps(article_info))
                time.sleep(10)
            page = clean_html(next_page_link)
            print('Dumped article number:', counter*125)
            counter += 1
            rndm = random.randint(20, 40)
            time.sleep(rndm)

    # for authors in authorsList:
    #     isABC = all(authorsLess(*a) for a in zip(authors[:-1], authors[1:]))
    #     print(isABC, len(authors), authors)

if __name__ == '__main__':
    main()

