
import urllib2
import base64
import xml.etree.ElementTree as ET
import nltk
from collections import Counter

bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27jaguar%27&$top=10&$format=Atom'
#Provide your account key here
accountKey = 'xQsuyV9c3sG/oW9e5FTBmfm/YrTq6uXXmtNV+k5Mmxs'
atom_prefix = '{http://www.w3.org/2005/Atom}'
microsoft_prefix = '{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}'
inner_prefix = '{http://schemas.microsoft.com/ado/2007/08/dataservices}'

accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
headers = {'Authorization': 'Basic ' + accountKeyEnc}
req = urllib2.Request(bingUrl, headers = headers)
response = urllib2.urlopen(req)
content = response.read()
#content contains the xml/json response from Bing.

root = ET.fromstring(content)  

query = root[0].text
url = root[5].attrib['href']
total_results = 0
num_relevant = 0.0

print "Parameters:"
print "Client Key: " + accountKey
print "Query: Jaguar"
print "Precision: .9"
print "URL: " + bingUrl
print "Total Results: 10"
print "Bing Search Results:"
print "========================"

for node in root.findall(atom_prefix+'entry'):
    total_results+=1
    print "Result " + str(total_results)
    print "["
    entry_node = node.find(atom_prefix+'content').find(microsoft_prefix+'properties')
    URL = entry_node.find(inner_prefix+'Url').text
    print " URL: " + URL
    print " Title: " + entry_node.find(inner_prefix+'Title').text
    print " Summary: " + entry_node.find(inner_prefix+'Description').text
    print "]\n"

    tokens = []
    req = urllib2.Request(URL, headers = headers)
    response = urllib2.urlopen(req)
    content = response.read()
    raw = nltk.clean_html(content)
    tokens = map(lambda x:x.lower(), nltk.word_tokenize(raw))
    

    counts = Counter(tokens)

    print counts

    relevancy = raw_input("Relevant (Y/N)?")
    if relevancy.lower() == "y":
        num_relevant+=1

print "Precision: " + str(num_relevant/total_results)

if num_relevant == 0:
    print "Program Terminating. No relevant results found in top 10."
if total_results != 10:
    print "Program Terminating. Less than 10 results returned by Bing."

