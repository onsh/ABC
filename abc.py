#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import Request, urlopen
from urllib.error import URLError
import html5lib
# import xml.etree
#import re
#import csv

def authorsLess(a0, a1):
    return a0.split()[-1].lower() < a1.split()[-1].lower()


def main():
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


    data = response.read()

    dom = html5lib.parse(
        data,
        treebuilder = "etree",
        namespaceHTMLElements = False
    )

    # xml.etree.ElementTree.dump( dom )
    # print(dom)

    authorsList = []
    for article in dom.findall('.//*[@class="results-cit cit"]'):
        elems = article.findall('.//*[@class="cit-auth cit-auth-type-author"]')
        # XXX: sanitize
        authors = [e.text for e in elems]
        authorsList.append(authors)

    for authors in authorsList:
        isABC = all(authorsLess(*a) for a in zip(authors[:-1], authors[1:]))
        print(isABC, len(authors), authors)

main()
