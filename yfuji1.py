#!/usr/bin/python

import re
import sys
import pprint
import urllib
import urllib.request
import urllib.parse
import html5lib


def lessAuthors( a0, a1 ):
    return a0.split()[-1].lower() < a1.split()[-1].lower()

def main():
    """
	url = "http://ptp.oxfordjournals.org/search?submit=yes"
	with urllib.request.urlopen( url ) as f:
        data = f.read()
	"""
    data = open( "src.html", encoding = "utf-8" ).read()

	dom = html5lib.parse( data,	treebuilder = "etree", namespaceHTMLElements = False )

	authorsList = []
	for article in dom.findall( './/*[@class="results-cit cit"]' ):
		elems = article.findall(
            './/*[@class="cit-auth cit-auth-type-author"]'
		)
		# XXX: sanitize
		authors = [ e.text for e in elems ]
		authorsList.append( authors )

	for authors in authorsList:
		isAO = all(
			lessAuthors( a0, a1 )
			for a0, a1 in zip( authors[:-1], authors[1:] )
		)
		print( isAO, len( authors ), authors )

main()
