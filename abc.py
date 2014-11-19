#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
# import html5lib
# import xml.etree
#import re
#import csv


def get_abst_links():
    url = "http://ptp.oxfordjournals.org/search?fulltext=&submit=yes&x=14&y=12"
    # url = "http://ptp.oxfordjournals.org/search?submit=yes&FIRSTINDEX=10"
    req = Request(url)
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
        html_doc = response.read()
        soup = BeautifulSoup(html_doc)
        respnse.close()
     
        base_url  = 'http://ptp.oxfordjournals.org/'
        abst_list = []
        for link in soup.find_all('a', rel = 'abstract'):
            # i dont know the necessality using of urljoin()
            abst_list.append(urljoin(base_url, link.get('href')))
            print(abst_list)
        

def authorsLess(a0, a1):
    return a0.split()[-1].lower() < a1.split()[-1].lower()

   
def main():
    authorsList = []
    for article in dom.findall('.//*[@class="results-cit cit"]'):
        elems = article.findall('.//*[@class="cit-auth cit-auth-type-author"]')
        # XXX: sanitize
        authors = [e.text for e in elems]
        authorsList.append(authors)

    for authors in authorsList:
        isABC = all(authorsLess(*a) for a in zip(authors[:-1], authors[1:]))
        print(isABC, len(authors), authors)

if __name__ == '__main__':
    main()

