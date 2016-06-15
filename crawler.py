#!/use/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from pprint import pprint
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from contextlib import contextmanager
import sys
import re
import lxml
import time
import json
import random
import unicodedata


# Test for local environment
def read_html(filename):
    with open(filename) as f:
        page = f.read()
    soup = BeautifulSoup(page)
    return soup


@contextmanager
def fetch_url(url, max_times=5, wait_period=5):
    retry_count = 0
    header_list = ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.78.2 (KHTML, like Gecko) Version/6.1.6 Safari/537.78.2', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31', 'Googlebot/2.1 (+http://www.google.com/bot.html)']
    while True:
        try:
            req = Request(url)
            req.add_header('User-agent', random.choice(header_list))
            f = urlopen(req)
            if f.getcode() == 200 or retry_count > max_times:
                yield f
                break
            retry_count += 1
            time.sleep(wait_period * retry_count * retry_count * 2)  # 10, 40, 90, 160, 250 sec.
        finally:
            print('We couldn\'t access to the following URL:', url)
            f.close()


def make_soup(response):
    dashi = response.read()
    soup = BeautifulSoup(dashi, 'lxml')
    response.close()
    return soup


def clean_html(url):
    req = Request(url)
    header_list = ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.78.2 (KHTML, like Gecko) Version/6.1.6 Safari/537.78.2', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31', 'Googlebot/2.1 (+http://www.google.com/bot.html)']
    req.add_header('User-agent', random.choice(header_list))

    try:
        response = urlopen(req)
    except URLError as e:
        if hasattr(e, 'reason'):
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
            print('URL:', url)
        elif hasattr(e, 'code'):
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
            print('URL:', url)
    else:
        # everything is fine
        soup = make_soup(response)
    return soup


def get_next_page_url(soup, base_url):
    next_page_link = soup.find('a', class_='next-results-link')
    if next_page_link is None:
        next_page_url = None
    else:
        next_page_url = urljoin(base_url, next_page_link.get('href'))
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
    h1_tag = soup.find('h1', id='article-title-1')
    title = str(h1_tag.contents[0:])
    # print(title)
    return title


def get_authors(soup):
    authors_list = []
    for author in soup.find_all('a', class_='name-search'):
        author = author.string
        authors_list.append(author)

    for collab in soup.find_all('span', class_='collab'):
        collab = collab.string
        authors_list.append(collab)
    # print(authors_list)
    return authors_list


def get_affiliation(soup):
    aff_list = []
    for aff in soup.find_all(id=re.compile('^aff-')):
        num = aff.get('id')[-1]
        address = aff.next_sibling.contents[-1].strip()
        aff_data = {'num': int(num), 'address': address}
        aff_list.append(json.dumps(aff_data))
    # pprint(aff_list)
    return aff_list


def get_received_date(soup):
    received = soup.find('li', class_='received')
    split_received = re.split(r'[,.\s]\s*', received.contents[1])
    month, date, year = split_received[:3]
    received_date = {'month': month,
                     'date': int(date),
                     'year': int(year)}
    # print(json.dumps(received_date))
    return received_date


def get_abstract(soup):
    abstract = soup.find('p', id='p-1')
    abstract = str(abstract.contents[0:])
    # print(abstract)
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
    # print(info)
    return info


def lessAuthors(s0, s1):
    # Normalize the text into a standard representaion
    # cf. NFD, NFKC, NFKD  
    t0 = unicodedata.normalize('NFC', s0)
    t1 = unicodedata.normalize('NFC', s1)

    # Leave the last word (author's family name),
    # then compare the words
    return t0.split()[-1].lower() < t1.split()[-1].lower()

def save_to_db(data, mongo_db, mongo_db_coll, **mongo_conn_kw):
    # Connects to the MongoDB server running on
    # localhost:27017 by default
    try:
        client = MongoClient(**mongo_conn_kw)
    except ConnectionFailure as e:
        sys.stderr.write("Could not connect to MongoDB: {0}".format(e))
        sys.exit(1)

    # Get a reference to a particular database
    db = client[mongo_db]

    # Reference a particular collection in the database
    coll = db[mongo_db_coll]

    # Perform a bulk insert and return the IDs
    return coll.insert(data)


def main():
    base_url = 'http://ptp.oxfordjournals.org/'
    # Oldest first
    # url = "http://ptp.oxfordjournals.org/search?submit=yes&pubdate_year=&volume=&firstpage=&doi=&author1=&author2=&title=&andorexacttitle=and&titleabstract=&andorexacttitleabs=and&fulltext=&andorexactfulltext=and&journalcode=ptp&fmonth=&fyear=&tmonth=&tyear=&flag=&format=standard&hits=125&sortspec=reverse-date&submit=yes&submit=Search"

    # Newest fist
    url = "http://ptp.oxfordjournals.org/search?submit=yes&pubdate_year=&volume=&firstpage=&doi=&author1=&author2=&title=&andorexacttitle=and&titleabstract=&andorexacttitleabs=and&fulltext=&andorexactfulltext=and&journalcode=ptp&fmonth=&fyear=&tmonth=&tyear=&flag=&format=standard&hits=125&sortspec=date&submit=yes&submit=Search"

    with fetch_url(url) as f:
        page = make_soup(f)

    pagenation_counter = 1
    continue_scraping = True

    while continue_scraping:
        next_page_link = get_next_page_url(page, base_url)
        if next_page_link is None:
            continue_scraping = False
        else:
            article_links = get_article_links(page, base_url)
            for link in article_links:
                article = clean_html(link)
                authors = get_authors(article)

                # Calculate whether author list is alphabetical order
                is_alphabetical = all(lessAuthors(a0, a1) for a0, a1
                                      in zip(authors[:-1], authors[1:]))

                if 'abstract' in link:
                    article_info = {
                        'title': get_title(article),
                        'authors': get_authors(article),
                        'order': isAO,
                        'affiliation': get_affiliation(article),
                        'date': get_received_date(article),
                        'abstract': get_abstract(article),
                        'info': get_other_info(article),
                        'url': link
                    }
                    # save_to_db(article_info, ptp, articles, onsh)
                else:
                    article_info = {
                        'title': get_title(article),
                        'authors': get_authors(article),
                        'order': isAO,
                        'affiliation': get_affiliation(article),
                        'date': get_received_date(article),
                        'abstract': "",
                        'info': get_other_info(article),
                        'url': link
                    }
                    # save_to_db(article_info, ptp, articles, onsh)
                time.sleep(10)
            page = next_page_link
            print('Dumped articles number:', pagenation_counter * 125)
            pagenation_counter += 1  # less than 127
            rndm = random.randint(10, 30)
            time.sleep(rndm)

if __name__ == '__main__':
    main()
