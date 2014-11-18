from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


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

        html_doc = response.read()
        soup = BeautifulSoup(html_doc)
        # print(soup.prettify())

        # print(soup.title)
        # print(soup.title.string)
        # print()
        # print(soup.find_all('a'))

        root_url = 'http://ptp.oxfordjournals.org/'
        abst_list = []
        for link in soup.find_all('a', rel='abstract'):
            abst_list.append(urljoin(root_url, link.get('href')))
        print(abst_list)

if __name__ == '__main__':
    main()
            
