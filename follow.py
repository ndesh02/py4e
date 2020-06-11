# To run this, download the BeautifulSoup zip file
# http://www.py4e.com/code3/bs4.zip
# and unzip it in the same directory as this file
import re
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl

count=None
position=None
lst=list()
lt=list()
name=None

count=input('Enter count: ')
count=int(count)
position=input('Enter position: ')
position=int(position)
# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = input('Enter - ')

for c in range(count):
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')
    p=0
    # Retrieve all of the anchor tags
    tags = soup('a')
    for tag in tags:
        p=p+1
        #up to the position chosen
        if p>position:
            break
        #change the url to the new one
        url=tag.get('href',None)
    print(url)
