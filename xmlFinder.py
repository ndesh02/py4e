import urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as ET
import ssl
total=0
url = input('Enter url: ')

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

info = urllib.request.urlopen(url, context=ctx).read()

tr=ET.fromstring(info)

counts=tr.findall('comments/comment/count')
for c in counts:
    total=total+int(c.text)

print('total= ', total)
