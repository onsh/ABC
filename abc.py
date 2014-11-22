#!/use/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
#import re

## first page
# http://ptp.oxfordjournals.org/search?submit=yes&pubdate_year=&volume=&firstpage=&doi=&author1=&author2=&title=&andorexacttitle=and&titleabstract=&andorexacttitleabs=and&fulltext=&andorexactfulltext=and&journalcode=ptp&fmonth=&fyear=&tmonth=&tyear=&flag=&format=standard&hits=125&sortspec=reverse-date&submit=yes&submit=Search

## second page
# http://ptp.oxfordjournals.org/search?tmonth=&pubdate_year=&submit=yes&submit=yes&submit=Search&andorexacttitle=and&format=standard&firstpage=&fmonth=&title=&tyear=&hits=125&titleabstract=&flag=&journalcode=ptp&volume=&sortspec=reverse-date&andorexacttitleabs=and&author2=&andorexactfulltext=and&author1=&fyear=&doi=&fulltext=&FIRSTINDEX=125

## third page
# http://ptp.oxfordjournals.org/search?tmonth=&pubdate_year=&submit=yes&submit=yes&submit=Search&andorexacttitle=and&format=standard&firstpage=&fmonth=&title=&tyear=&hits=125&flag=&titleabstract=&journalcode=ptp&volume=&sortspec=reverse-date&andorexacttitleabs=and&author2=&andorexactfulltext=and&author1=&fyear=&doi=&fulltext=&FIRSTINDEX=250

def get_next_page_url(url):
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
        page = response.read()
        soup = BeautifulSoup(page)
        respnse.close()
        next_page_li = soup_package.find("li", class_="pager-next last")
        if next_page_li is None :
            next_page_url = None
        else:
            next_page_url base_url + next_page_li.a.get('href')
            
        return next_page_url

# quoted from "Getting Started with Beautiful Soup"
def get_bookdetails(url):
    page = urllib2.urlopen(url)
    soup_package = BeautifulSoup(page, "lxml")
    page.close()
    all_books_table = soup_package.find("table", class_="views-view-grid")
    all_book_titles = all_books_table.find("div", class_="views-field-title")
    isbn_list = []
    for book_title in all_book_titles:
        book_title_span = book_title.span
        print("Title Name:"+book_title_span.a.string)
        print("Url:"+book_title_span.a.get('href'))
        price = book_title.find_next("div", class_="views-field-sell-price")
        print("PacktPub Price:"+price.span.string)
        isbn_list.apend(get_isbn(book_title_span.a.get('href')))
    return isbn_list


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

