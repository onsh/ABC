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


def make_soup(response):
    dashi = response.read()
    soup = BeautifulSoup(dashi, 'lxml')
    response.close()
    return soup


def clean_html(url):
    req = Request(url)
    header_list = ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.78.2 (KHTML, like Gecko) Version/6.1.6 Safari/537.78.2', 'Mozilla/5.0 (X11; Linux i686) AppleWebK\
it/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31', 'Googlebot/2.1 (+http://www.google.com/bot.html)']
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
        return response


def get_next_page_url(soup, base_url):
    next_page_link = soup.find('a', class_='next-results-link')
    if next_page_link is None:
        next_page_url = None
    else:
        next_page_url = urljoin(base_url, next_page_link.get('href'))
    return next_page_url


def get_section(soup):
    section = soup.find('span', class_='cit-first-element cit-section')
    return section.string


def get_authors(soup):
    authors_list = []
    for author in soup.find_all('span', class_='cit-auth cit-auth-type-auth'):
        author = author.string
        authors_list.append(author)
    return authors_list


def get_title(soup):
    title = soup.find('span', class_='cit-title')
    return title.string


def get_other_info(soup):
    ''' Get other article info of an article '''
    year = soup.find('span', class_='cit-print-date').contents[1]
    info = {'year' : year.strip()}
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

    # Newest fist
    url = "http://ptp.oxfordjournals.org/search?submit=yes&pubdate_year=&volume=&firstpage=&doi=&author1=&author2=&title=&andorexacttitle=and&titleabstract=&andorexacttitleabs=and&\
fulltext=&andorexactfulltext=and&journalcode=ptp&fmonth=&fyear=&tmonth=&tyear=&flag=&format=standard&hits=125&sortspec=date&submit=yes&submit=Search"

    with clean_html(url) as f:
        page = make_soup(f)

        pagenation_counter = 1
        continue_scraping = True

        while continue_scraping:
            print('start')
            next_page_link = get_next_page_url(page, base_url)
            if next_page_link is None:
                continue_scraping = False

            else:
                print(next_page_link)
                for list in page.find_all('li', class_='results-cit cit'):
                    authors = get_authors(list)

                    # Calculate whether author list is alphabetical order
                    is_alphabetical = all(lessAuthors(a0, a1) for a0, a1
                                          in zip(authors[:-1], authors[1:]))

                    article_info = {
                        'section' : get_section(list),
                        'authors' : authors,
                        'order' : is_alphabetical,
                        'title' : get_title(list),
                        'info' : get_other_info(list)
                    }
                    print(article_info)

                # save_to_db(article_info, 'ptp', 'articles')

                page = next_page_link
                print(page)
                print('Dumped articles number:', pagenation_counter * 125)
                pagenation_counter += 1  # less than 127
                rndm = random.randint(10, 15)
                time.sleep(rndm)

if __name__ == '__main__':
    main()


