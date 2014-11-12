#!/usr/bin/env python3
# coding: utf-8

from urllib import request
from urllib import parse

def main():
    url1 = "http://ptp.oxfordjournals.org/search?submit=yes&pubdate_year=&volume=&firstpage=&doi=&author1=&author2=&title=&andorexacttitle=and&titleabstract=&andorexacttitleabs=and&fulltext=&andorexactfulltext=and&journalcode=ptp&fmonth=&fyear=&tmonth=&tyear=&flag=&format=standard&hits=125&sortspec=relevance&submit=yes&submit=Search"
    url2 = "http://ptp.oxfordjournals.org/search?tmonth=&pubdate_year=&submit=yes&submit=yes&submit=Search&andorexacttitle=and&format=standard&firstpage=&fmonth=&title=&tyear=&hits=125&titleabstract=&flag=&journalcode=ptp&volume=&sortspec=relevance&andorexacttitleabs=and&author2=&andorexactfulltext=and&author1=&fyear=&doi=&fulltext=&FIRSTINDEX=125"
    url3 = "http://ptp.oxfordjournals.org/search?tmonth=&pubdate_year=&submit=yes&submit=yes&submit=Search&andorexacttitle=and&format=standard&firstpage=&fmonth=&title=&tyear=&hits=125&flag=&titleabstract=&journalcode=ptp&volume=&sortspec=relevance&andorexacttitleabs=and&author2=&andorexactfulltext=and&author1=&fyear=&doi=&fulltext=&FIRSTINDEX=250"
    
    opener = request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    # with opener.open(url) as f:
    #     data = f.read(100).decode('utf-8')
    #     print(data)
    
    q1 = parse.urlsplit(url1)
    q2 = parse.urlsplit(url2) # url1とurl2はqueryが違う
    q3 = parse.urlsplit(url3) # url2とurl3はqueryの最後が違う &FIRSTINDEX=125 &FIRSTINDEX=250
   
    print(q1.query)
    print(q2.query)
    print(q3.query)
    

main()        

