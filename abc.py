#!/use/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
from pprint import pprint

## first page
# http://ptp.oxfordjournals.org/search?submit=yes&pubdate_year=&volume=&firstpage=&doi=&author1=&author2=&title=&andorexacttitle=and&titleabstract=&andorexacttitleabs=and&fulltext=&andorexactfulltext=and&journalcode=ptp&fmonth=&fyear=&tmonth=&tyear=&flag=&format=standard&hits=125&sortspec=reverse-date&submit=yes&submit=Search

## second page
# http://ptp.oxfordjournals.org/search?tmonth=&pubdate_year=&submit=yes&submit=yes&submit=Search&andorexacttitle=and&format=standard&firstpage=&fmonth=&title=&tyear=&hits=125&titleabstract=&flag=&journalcode=ptp&volume=&sortspec=reverse-date&andorexacttitleabs=and&author2=&andorexactfulltext=and&author1=&fyear=&doi=&fulltext=&FIRSTINDEX=125

## third page
# http://ptp.oxfordjournals.org/search?tmonth=&pubdate_year=&submit=yes&submit=yes&submit=Search&andorexacttitle=and&format=standard&firstpage=&fmonth=&title=&tyear=&hits=125&flag=&titleabstract=&journalcode=ptp&volume=&sortspec=reverse-date&andorexacttitleabs=and&author2=&andorexactfulltext=and&author1=&fyear=&doi=&fulltext=&FIRSTINDEX=250

### quoted from "Getting Started with Beautiful Soup" ---------
# def get_isbn(url):
#     book_title_url = packtpub_url + url
#     page = urllib2.urlopen(book_title_url)
#     soup_bookpage = BeautifulSoup(page, "lxml")
#     page.close()
#     isbn_tag = soup_bookpage.find('b', text=re.comiple("ISBN :"))
#     return isbn_tag.next_sibling

# def get_bookdetails(url):
#     page = urllib2.urlopen(url)
#     soup_package = BeautifulSoup(page, "lxml")
#     page.close()
#     all_books_table = soup_package.find("table", class_="views-view-grid")
#     all_book_titles = all_books_table.find("div", class_="views-field-title")
#     isbn_list = []
#     for book_title in all_book_titles:
#         book_title_span = book_title.span
#         print("Title Name:"+book_title_span.a.string)
#         print("Url:"+book_title_span.a.get('href'))
#         price = book_title.find_next("div", class_="views-field-sell-price")
#         print("PacktPub Price:"+price.span.string)
#         isbn_list.apend(get_isbn(book_title_span.a.get('href')))
#     return isbn_list
###-------------------------------------------------------------

# test function for my local development
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
        soup = BeautifulSoup(page)
        return soup
        
def get_next_page_url(soup, base_url):
    next_page_link = soup.find("a", class_="next-results-link")
    if next_page_link is None :
        next_page_url = None
    else:
        next_page_url = base_url + next_page_link.get("href")
    return next_page_url

#def get_article_list(soup, base_url):


def get_article_links(soup, base_url):
    article_list = []
    for link in soup.find_all('a', rel='abstract'):
        # i dont know the necessality using of urljoin()
        article_list.append(urljoin(base_url, link.get("href")))
    return article_list

def get_article_details(soup):
    # title
    title = soup.title.string
    # authors
    authorsList = []
    for author in soup.find_all("a", class_="name-search"):
        authorsList.append(author.string)
    # publication date ['September', '29,', '2012.']
    for x in soup.find_all("li", class_="received"):
        pub_date = x.text.split()
        pub_date = pub_date.pop(0)
    # abstract
    abstract = soup.find_all("p", id="p-1")[0].text
    p = re.compile('\n\s*')
    abstract = p.sub(' ', abstract)
    # article info ['128', '(6):', '1001-1060.', '10.1143/PTP.128.1061']
    # info = {'vol':"slug-vol", 'issue':"slug-issue", 'pages':"slug-pages", 'doi':"slug-doi"}
    # info_keys = ['vol', 'issue', 'pages', 'doi']
    # info_values = ["slug-vol", "slug-issue", "slug-pages", "slug-doi"]
    # for k, v in zip(info_keys, info_values):
    #     v_part = soup.find_all("span", class_=v)[0].text
    #     info.append(k, v_part.strip())
    

def authorsLess(a0, a1):
    return a0.split()[-1].lower() < a1.split()[-1].lower()

   
def main():
    base_url  = 'http://ptp.oxfordjournals.org/'
    url = "http://ptp.oxfordjournals.org/search?submit=yes&pubdate_year=&volume=&firstpage=&doi=&author1=&author2=&title=&andorexacttitle=and&titleabstract=&andorexacttitleabs=and&fulltext=&andorexactfulltext=and&journalcode=ptp&fmonth=&fyear=&tmonth=&tyear=&flag=&format=standard&hits=125&sortspec=reverse-date&submit=yes&submit=Search"
    # url = "http://ptp.oxfordjournals.org/search?fulltext=&submit=yes&x=14&y=12"
    # url = "http://ptp.oxfordjournals.org/search?submit=yes&FIRSTINDEX=10"

    soup = read_html('sample.html')
    # soup = clean_html(url)
    print('Next page >>> ', get_next_page_url(soup, base_url))
    article_links = get_article_links(soup, base_url)
    print('# of article links:', len(article_links))
    pprint(article_links)

    # If there is an abstract-link in an article,
    # if  in  :
    #     get_article_links(soup, base_url) <-- have to be changed to proper function
    #     
    # else:
    #     extract rough info of an article
    

    # authorsList = []
    # for article in dom.findall('.//*[@class="results-cit cit"]'):
    #     elems = article.findall('.//*[@class="cit-auth cit-auth-type-author"]')
    #     # XXX: sanitize
    #     authors = [e.text for e in elems]
    #     authorsList.append(authors)

    # for authors in authorsList:
    #     isABC = all(authorsLess(*a) for a in zip(authors[:-1], authors[1:]))
    #     print(isABC, len(authors), authors)

if __name__ == '__main__':
    main()

