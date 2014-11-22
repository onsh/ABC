from urllib.request import urlopen
import re
from bs4 import BeautifulSoup

packtpub_url = "HTTP://www.packtpub.com/"

def get_bookurls(url):
    page = urlopen(url)
    soup_packtpage = BeautifulSoup(page, "lxml")
    page.close()
    next_page_li = soup_package.find("li", class_="pager-next last")
    if next_page_li is None :
        next_page_url = None
    else:
        next_page_url base_url + next_page_li.a.get('href')
        
    return next_page_url

start_url = "www.packtpub.com/books"
continue_scrapping = True
books_url = [start_url]
while continue_scrapping:
    next_page_url = get_bookurls(start_url)
    if next_page_url is None:
        continue_scrapping = False
    else:
        books_url.append(next_page_url)
    start_url = next_page_url

def get_bookdetails(url):
    page = urlopen(url)
    soup_package = BeautifulSoup(page, "lxml")
    page.close()
    all_books_table = soup_package.find("table", class_="views-view-grid")
    all_book_titles = all_books_table.find_all("div", class_="views-field-title")
    isbn_list = []
    for book_title in all_book_titles:
        book_title_span = book_title.span
        print("Title Name:"+book_title_span.a.string)
        print("Url:"+book_title_span.a.get('href'))
        price = book_title.find_next("div", class_="views-field-sell-price")
        print("PacktPub Price:"+price.span.string)
        isbn_list.apend(get_isbn(book_title_span.a.get('href')))
    return isbn_list

def get_isbn(url):
    book_title_url = packtpub_url + url
    page = urlopen(book_title_url)
    soup_bookpage = BeautifulSoup(page, "lxml")
    page.close()
    isbn_tag = soup_bookpage.find('b', text=re.compile("ISBN :"))
    return isbn_tag.next_sibling

isbns = []
for bookurl in books_url:
    isbns += get_bookdetails(bookurl)

print(isbns)


if __name__ == '__main__':
    main()    
