#!/use/bin/env python3

from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from pprint import pprint
import lxml
import time
import random
import unicodedata

# try / exception
# def get_next_page_url(soup, base_url):
#     next_page_link = soup.find('a', class_='next-results-link')
#     if next_page_link is None:
#         next_page_url = None
#     else:
#         next_page_url = urljoin(base_url, next_page_link.get('href'))
#     return next_page_url

def request(url):
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


def get_section(one_page):
    # Section type, i.e. Article, Letter, etc 
    section        = one_page.find('span', class_='cit-first-element cit-section')
    section_type   = section.contents[0]  # 'Articles'    
    # section_type = section.get_text()  # 'Articles: '
    return section_type


def get_authors(one_page):
    # Authors
    # TODO: if len(authors_list) > 1
    authors_list = []
    for li in one_page.find_all('span', class_='cit-auth cit-auth-type-author'):
        authors_list.append(li.string)
    return authors_list


def get_title(one_page):
    # Title
    title_obj = one_page.find('span', class_='cit-title')
    title     = title_obj.get_text()


def get_year(one_page):
    # Year
    year   = one_page.find('span', class_='cit-print-date').contents[1]  # 2016
    # year = one_page.find('span', class_='cit-print-date').get_text()  # (2016)


def get_doi(one_page):
    #DOI
    doi   = one_page.find('span', class_='cit-doi').get_text()
    # doi = one_page.find('span', class_='cit-doi').contents[1]


def lessAuthors(s0, s1):
    # Normalize the text into a standard representaion
    # cf. NFD, NFKC, NFKD
    t0 = unicodedata.normalize('NFC', s0)
    t1 = unicodedata.normalize('NFC', s1)

    # Leave the last word (author's family name),
    # then compare the words
    return t0.split()[-1].lower() < t1.split()[-1].lower()


def main():
    # Total : 15783 articles, 15783 / 125 = 126.264
    page = [i * 125 for i in range(1, 127)] 
    continue_scraping  = True


    const_url = 'http://ptp.oxfordjournals.org/search?submit=yes&pubdate_year=&volume=&firstpage=&doi=&author1=&author2=&title=&andorexacttitle=and&titleabstract=&andorexacttitleabs=and&fulltext=&andorexactfulltext=and&journalcode=ptp&fmonth=&fyear=&tmonth=&tyear=&flag=&format=standard&hits=125&sortspec=date&submit=yes&submit=Search'

    http://ptp.oxfordjournals.org/search?tmonth=&pubdate_year=&submit=yes&submit=yes&submit=Search&andorexacttitle=and&format=standard&firstpage=&fmonth=&title=&tyear=&hits=125&titleabstract=&flag=&journalcode=ptp&volume=&sortspec=date&andorexacttitleabs=and&author2=&andorexactfulltext=and&author1=&fyear=&doi=&fulltext=&FIRSTINDEX=125

    http://ptp.oxfordjournals.org/search?tmonth=&pubdate_year=&submit=yes&submit=yes&submit=Search&andorexacttitle=and&format=standard&firstpage=&fmonth=&title=&tyear=&hits=125&flag=&titleabstract=&journalcode=ptp&volume=&sortspec=date&andorexacttitleabs=and&author2=&andorexactfulltext=and&author1=&fyear=&doi=&fulltext=&FIRSTINDEX=250
    
    for num in page:
        # To get absolute URL
        url = const_url + str(num)
        raw_data = request(url)
        soup = BeautifulSoup(raw_data, 'lxml')
        
        pagenation_counter = 1

        # with open(url, 'r') as f:
        #     soup = BeautifulSoup(f, 'lxml')
        
        for one_page in soup.find_all('li', class_ = 'results-cit cit'):
            # # For debugging
            # print(one_page.prettify())
            # print('----------------------------------------')
            
            authors = get_authors(one_page)
            # Calculate whether author list is alphabetical order
            is_alphabetical = all(lessAuthors(a0, a1) for a0, a1
                              in zip(authors_list[:-1], authors_list[1:]))
            
            article_info = {
                'section' : get_section(one_page),
                'auhtors' : authors,
                'order' : is_alphabetical,
                'title' : get_title(one_page),
                'year' : get_year(one_page),
                'doi' : get_doi(onepage)
            }
                    
            # pprint(article_info)
            # print('----------------------------------------')
            one_page_info = []
            one_page_info.append(article_info)
            
        with open('page' + str(pagenation_counter) + '.json', 'wb') as data_file:
                data_file.write(one_page_info)

        print('Dumped articles number:', page)
        # soup = next_page_link
        # print(soup)
        # pagenation_counter += 1  # less than 127
        # print('page :', pagenation_counter - 1)
        
        # for interval
        rndm = random.randint(10, 20)
        time.sleep(rndm)

if __name__ == '__main__':
    main()

