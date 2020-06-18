# python lookup.py
#    $1: FROM : one of key, id, inchi, smiles
#    $2: TO   : one of key, id, inchi, smiles
#    $3: INPUT

import sys
import requests
import json
import ssl
import urllib
import os

if (len(sys.argv) != 4):
    print('Usage: lookup.py from to argument')
    exit(1)

ssl._create_default_https_context = ssl._create_unverified_context

#authstr = os.environ.get('TOKEN')
#if authstr==None:
#    print('You must do:(linux) setenv TOKEN=<java-web-token>')
#    print('            (mac) export TOKEN=<java-web-token>')
#    exit(1)

source = sys.argv[1]
dest   = sys.argv[2]
param  = sys.argv[3]

if source not in ['key', 'smiles', 'inchi', 'id']:
    print(f'first argument invalid: {source}')
    exit(1)

if dest not in ['key', 'smiles', 'inchi', 'id']:
    print(f'second argument invalid: {dest}')
    exit(1)

if source==dest:
    print('Source and destination cannot be equal')
    exit(1)
   
# If source is InChI, we use ChemSpider to convert to InChIKey
if source=='inchi':
    r = requests.get(f'http://www.chemspider.com/InChI.asmx/InChIToInChIKey?inchi={param}')
    t = r.text.split()[4]
    key = t.split('>')[1].split('<')[0]
    # If we are converting InChI to Key, we have it already
    if dest=='key':
         print("['%s']"%key)
         exit(1)
    source='key'
    param=key

urlstr=f'https://covid-ws-01.alcf.anl.gov/rpc/{source}2{dest}'
data = urllib.parse.urlencode({'input':param})
req = urllib.request.Request(urlstr, data.encode('ascii')) # {'Authorization': 'Bearer %s'%authstr})
try: response = urllib.request.urlopen(req).read()
except urllib.error.URLError as e:
    print(e.reason)
    exit(1)
results = json.loads(response.decode('ascii'))
outputs = [v for d in results for k,v in d.items()]
print(outputs)
