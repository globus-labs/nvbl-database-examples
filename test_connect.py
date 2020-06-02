"""
This is a small script written by Ben L. to test connecting to the PostGREST API.
"""

import requests
import json
import urllib3
import os
import getpass

# PYTHON 3.7
# There is an issue with the SSL certs from the target server.
# Because of this verification of these certs needs to be turned off
# durning requests. Turning this off genereates a warning which the below
# line surpresses
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
COVID_URL = 'https://covid-ws-01.alcf.anl.gov'
# email and password of user accessing endpoint
def get_token(email, password):
        login = COVID_URL + '/rpc/login'
        payload = {'email': email, 'pass': password}
        # Note that we are turning off SSL verification here.
        response = requests.post(login, data=payload, verify=False, timeout=3)
        # Check the response code and handle it
        if response.status_code != 200:
                print("request faild: {0}".format(response.text))
        # Get the json object then spit out the token
        return response.json()[0]['token']


# Token is the string from get_token()
# table_name is the target of the get
# Params is a dict of get options.
#  ex: {"name":"Daniel", "id": 123456} -> ?name=Daniel&id=123456
def get_csv(token, table_name, params):
        url = COVID_URL + '/' + table_name
        # build auth header with token
        h = {'Authorization': 'Bearer ' + token}
        # Note that we are turning off SSL verification here.
        response = requests.get(url, headers=h, params=params, verify=False)
        # Check the response code and handle it
        if response.status_code != 200:
                print("request faild: {0}".format(response.text))
        return response.json()
if __name__=='__main__':
        email = os.getenv('COVID_DB_EMAIL', input('Please input your email > '))
        password = os.getenv('COVID_DB_PASS', getpass.getpass())
        token = get_token(email, password)
        print(get_csv(token, 'test', {'id': 'eq.BDB-1'}))
