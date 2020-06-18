import sqlite3
import urllib.error
import ssl
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4 import BeautifulSoup

#Comment all this code to understand each little part

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

#Make a file
conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()

#Creates the sqlite database
cur.execute('''CREATE TABLE IF NOT EXISTS Pages
    (id INTEGER PRIMARY KEY, url TEXT UNIQUE, html TEXT,
     error INTEGER, old_rank REAL, new_rank REAL)''')

#Many to many table
cur.execute('''CREATE TABLE IF NOT EXISTS Links
    (from_id INTEGER, to_id INTEGER)''')

#in case i have more than one web
cur.execute('''CREATE TABLE IF NOT EXISTS Webs (url TEXT UNIQUE)''')

# Check to see if we are already in progress...
#Randomly pick a record in the databse where this is true
cur.execute('SELECT id,url FROM Pages WHERE html is NULL and error is NULL ORDER BY RANDOM() LIMIT 1')
#Fetch a row
row = cur.fetchone()
if row is not None:
    print("Restarting existing crawl.  Remove spider.sqlite to start a fresh crawl.")
else :
    #Ask for a new web
    starturl = input('Enter web url or enter: ')
    #Insert the url we start with
    if ( len(starturl) < 1 ) : starturl = 'http://www.dr-chuck.com/'
    if ( starturl.endswith('/') ) : starturl = starturl[:-1]
    web = starturl
    if ( starturl.endswith('.htm') or starturl.endswith('.html') ) :
        pos = starturl.rfind('/')
        web = starturl[:pos]
    #If they entered a url
    if ( len(web) > 1 ) :
        cur.execute('INSERT OR IGNORE INTO Webs (url) VALUES ( ? )', ( web, ) )
        cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES ( ?, NULL, 1.0 )', ( starturl, ) )
        conn.commit()

# Get the current webs
#Only does links to the site you tell it to
cur.execute('''SELECT url FROM Webs''')
webs = list()
#Makes list of all the websites
for row in cur:
    webs.append(str(row[0]))

print(webs)

many = 0
#Loop
while True:
    #Ask for how many pages
    if ( many < 1 ) :
        sval = input('How many pages:')
        if ( len(sval) < 1 ) : break
        many = int(sval)
    many = many - 1

    #Get the from id from the page we're linking from
    cur.execute('SELECT id,url FROM Pages WHERE html is NULL and error is NULL ORDER BY RANDOM() LIMIT 1')
    try:
        row = cur.fetchone()
        # print row
        fromid = row[0]
        url = row[1]
    except:
        print('No unretrieved HTML pages found')
        many = 0
        break

    print(fromid, url, end=' ')

    # If we are retrieving this page, there should be no links from it
    cur.execute('DELETE from Links WHERE from_id=?', (fromid, ) )
    try:
        #Grab the url
        document = urlopen(url, context=ctx)

        html = document.read()
        #Html error code - 200 is good
        if document.getcode() != 200 :
            print("Error on page: ",document.getcode())
            #So we don't retrieve it ever again
            cur.execute('UPDATE Pages SET error=? WHERE url=?', (document.getcode(), url) )

        #Check to see if the content type is text html
        if 'text/html' != document.info().get_content_type() :
            print("Ignore non text/html page")
            #Wipe out if not what we want
            cur.execute('DELETE FROM Pages WHERE url=?', ( url, ) )
            conn.commit()
            continue

        #How many characters we got
        print('('+str(len(html))+')', end=' ')
        #Parse it
        soup = BeautifulSoup(html, "html.parser")

    #If i hit control z
    except KeyboardInterrupt:
        print('')
        print('Program interrupted by user...')
        break

    #Something else blew up
    except:
        print("Unable to retrieve or parse page")
        cur.execute('UPDATE Pages SET error=-1 WHERE url=?', (url, ) )
        conn.commit()
        continue

    #Sets the page rank in as 1 and insert it into the table
    cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES ( ?, NULL, 1.0 )', ( url, ) )
    #Doubly making sure it's there
    cur.execute('UPDATE Pages SET html=? WHERE url=?', (memoryview(html), url ) )
    conn.commit()

    # Retrieve all of the anchor tags
    tags = soup('a')
    count = 0
    for tag in tags:
        #Pull out the href tag
        href = tag.get('href', None)
        if ( href is None ) : continue
        # Resolve relative references like href="/contact"
        up = urlparse(href)
        #Get the scheme
        if ( len(up.scheme) < 1 ) :
            href = urljoin(url, href)
            #Check to see if anchor
        ipos = href.find('#')
        #Throw everything past anchor away
        if ( ipos > 1 ) : href = href[:ipos]
        #Throw away everything we don't like and cleaning it up
        if ( href.endswith('.png') or href.endswith('.jpg') or href.endswith('.gif') ) : continue
        if ( href.endswith('/') ) : href = href[:-1]
        # print href
        if ( len(href) < 1 ) : continue

		# Check if the URL is in any of the webs
        #Webs are urls we're willing to stay with (on our site)
        found = False
        for web in webs:
            if ( href.startswith(web) ) :
                found = True
                break
        if not found : continue
        #Ready to put this into Pages and giving it no html
        cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES ( ?, NULL, 1.0 )', ( href, ) )
        count = count + 1
        conn.commit()

        #Wanna get the id by getting the one already there or just created
        cur.execute('SELECT id FROM Pages WHERE url=? LIMIT 1', ( href, ))
        try:
            row = cur.fetchone()
            toid = row[0]
        except:
            print('Could not retrieve id')
            continue
        # print fromid, toid
        #Put link in
        cur.execute('INSERT OR IGNORE INTO Links (from_id, to_id) VALUES ( ?, ? )', ( fromid, toid ) )


    print(count)

cur.close()
