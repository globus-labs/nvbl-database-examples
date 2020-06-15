import requests
import urllib3
import hashlib
import os
import getpass

# PYTHON 3.7
# There is an issue with the SSL certs from the target server.
# Because of this verification of these certs needs to be turned off
# during requests. Turning this off generates a warning which the below
# line turns off
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

COVID_URL = 'https://covid-ws-01.alcf.anl.gov'


# ==================
# INTERNAL FUNCTIONS
# ==================

# Token is the string from get_token()
# table_name is the target of the get
# Params is a dict of get options.
#  ex: {"name":"Daniel", "id": 123456} -> ?name=Daniel&id=123456
def _get_json(token, table_name, params):
    url = COVID_URL + '/' + table_name
    # build auth header with token
    h = {'Authorization': 'Bearer ' + token}
    # Note that we are turning off SSL verification here.
    response = requests.get(url, headers=h, params=params, verify=False)
    # print(response.url)
    # Check the response code and handle it
    if response.status_code != 200:
        print("request faild: {0}".format(response.text))
    return response.json()


# Turn a given list or single object into a postgres REST query
# key is the name of the parameter
def _list_to_query(key, objs):
    if not isinstance(objs, list):
        return {key: 'eq.{0}'.format(objs)}
    else:
        query = 'in.('
        for o in objs:
            query += '{0},'.format(o)
        query += ')'
        return {key: query}


def _str_to_md5_hex(s):
    # converts a string into a md5 hex string
    return hashlib.md5(s.encode()).hexdigest()


# Given a set of strings turn them into a md5 lookup table
# md5 -> string
def _to_md5_table(strings):
    table = {}
    if not isinstance(strings, list):
        key = _str_to_md5_hex(strings)
        table[key] = strings
    else:
        for s in strings:
            key = _str_to_md5_hex(s)
            table[key] = s
    return table


# given the json results from dup_m2i and a dict with md5 values as the keys
# process results keyed by the values of md5_lookup
def _process_m2i_table_data(data, md5_lookup):
    json_r = {}
    for r in data:
        try:
            ids = json_r[md5_lookup[r['md5']]]
        except KeyError:
            param, val = r['ide'].split(':')
            json_r[md5_lookup[r['md5']]] = {param: val}
        else:
            param, val = r['ide'].split(':')
            ids[param] = val
    return json_r


def _process_m2s_table_data(data, md5_lookup, key):
    json_r = []
    for d in data:
        json_r.append({key: md5_lookup[d['md5']], 'smi': d['smi']})
    return json_r


def _process_m2k_table_data(data, md5_lookup, key):
    json_r = []
    for d in data:
        json_r.append({key: md5_lookup[d['md5']], 'key': d['key']})
    return json_r


# Given a list of data turn it into a lookup table of key -> val
def _to_lookup(data, key, val):
    lookup = {}
    for d in data:
        lookup[d[key]] = d[val]
    return lookup


# ==================
# EXTERNAL FUNCTIONS
# ==================
# email and password of user accessing endpoint
def get_token(email, password):
    login = COVID_URL + '/rpc/login'
    payload = {'email': email, 'pass': password}
    # Note that we are turning off SSL verification here.
    response = requests.post(login, data=payload, verify=False)
    # Check the response code and handle it
    if response.status_code != 200:
        print("request faild: {0}".format(response.text))
    # Get the json object then spit out the token
    return response.json()[0]['token']


# given a smi or set of smi strings get there keys
def smiles2key(token, smi):
    md5_smi = _to_md5_table(smi)
    params = _list_to_query('md5', [*md5_smi])
    results = _get_json(token, 'dup_m2k', params)
    # return list of smi -> key pairs
    return _process_m2k_table_data(results, md5_smi, 'smi')


def smiles2id(token, smi):
    md5_smi = _to_md5_table(smi)
    params = _list_to_query('md5', [*md5_smi])
    results = _get_json(token, 'dup_m2i', params)
    return _process_m2i_table_data(results, md5_smi)


def smiles2inchi(token, smi):
    keys = smiles2key(token, smi)
    keys_lookup = _to_lookup(keys, 'key', 'smi')
    params = _list_to_query('key', [*keys_lookup])
    results = _get_json(token, 'dup_k2n', params)
    # Post work
    json_r = []
    for r in results:
        json_r.append({'smi': keys_lookup[r['key']], 'inc': r['inc']})
    return json_r


def key2smiles(token, keys):
    params = _list_to_query('key', keys)
    md5_results = _get_json(token, 'dup_m2k', params)
    # Make lookup table
    md5_lookup = _to_lookup(md5_results, 'md5', 'key')
    params = _list_to_query('md5', [*md5_lookup])
    results = _get_json(token, 'dup_m2s', params)
    # POST
    return _process_m2s_table_data(results, md5_lookup, 'key')


def key2inchi(token, keys):
    params = _list_to_query('key', keys)
    results = _get_json(token, 'dup_k2n', params)
    return results


def key2id(token, keys):
    params = _list_to_query('key', keys)
    md5_results = _get_json(token, 'dup_m2k', params)
    # Make lookup table
    md5_lookup = _to_lookup(md5_results, 'md5', 'key')
    params = _list_to_query('md5', [*md5_lookup])
    results = _get_json(token, 'dup_m2i', params)
    return _process_m2i_table_data(results, md5_lookup)


def id2smiles(token, ids):
    param = _list_to_query('ide', ids)
    results = _get_json(token, 'dup_m2i', param)
    md5_lookup = _to_lookup(results, 'md5', 'ide')
    param = _list_to_query('md5', [*md5_lookup])
    results = _get_json(token, 'dup_m2s', param)
    # POST
    return _process_m2s_table_data(results, md5_lookup, 'ide')


def id2key(token, ids):
    param = _list_to_query('ide', ids)
    results = _get_json(token, 'dup_m2i', param)
    md5_lookup = _to_lookup(results, 'md5', 'ide')
    param = _list_to_query('md5', [*md5_lookup])
    results = _get_json(token, 'dup_m2k', param)
    return _process_m2k_table_data(results, md5_lookup, 'ide')


def id2inchi(token, ids):
    key_results = id2key(token, ids)
    key_lookup = _to_lookup(key_results, 'key', 'ide')
    param = _list_to_query('key', [*key_lookup])
    results = _get_json(token, 'dup_k2n', param)
    # Post work
    json_r = []
    for r in results:
        json_r.append({'ide': key_lookup[r['key']], 'inc': r['inc']})
    return json_r


def inchi2id(token, inc):
    param = _list_to_query('inc', inc)
    results = _get_json(token, 'dup_k2n', param)
    key_lookup = _to_lookup(results, 'key', 'inc')
    results = key2id(token, [*key_lookup])
    json_r = {}
    for r in results.keys():
        json_r[key_lookup[r]] = results[r]
    return json_r


def inchi2smiles(token, inc):
    param = _list_to_query('inc', inc)
    results = _get_json(token, 'dup_k2n', param)
    key_lookup = _to_lookup(results, 'key', 'inc')
    results = key2smiles(token, [*key_lookup])
    json_r = []
    for r in results:
        json_r.append({'inc': key_lookup[r['key']], 'smi': r['smi']})
    return json_r


def inchi2key(token, inc):
    param = _list_to_query('inc', inc)
    results = _get_json(token, 'dup_k2n', param)
    return results


if __name__ == '__main__':
    email = os.getenv('COVID_DB_EMAIL') or input('Please input your email > ')
    password = os.getenv('COVID_DB_PASSWORD') or getpass.getpass()
    token = get_token(email, password)
    # S -> Key
    print(smiles2key(token, 'C'))
    print(smiles2key(token, ['C', 'CCCCCC']))
    # S -> id
    print(smiles2id(token, 'C'))
    print(smiles2id(token, ['C', 'CCCCCC']))
    # S -> inchi
    print(smiles2inchi(token, 'C'))
    print(smiles2inchi(token, ['C', 'CCCCCC']))
    # Key -> smi
    print(key2smiles(token, 'VNWKTOKETHGBQD-UHFFFAOYSA-N'))
    print(key2smiles(token, ['VNWKTOKETHGBQD-UHFFFAOYSA-N', 'VLKZOEOYAKHREP-UHFFFAOYSA-N']))
    # Key -> INC
    print(key2inchi(token, 'VNWKTOKETHGBQD-UHFFFAOYSA-N'))
    print(key2inchi(token, ['VNWKTOKETHGBQD-UHFFFAOYSA-N', 'VLKZOEOYAKHREP-UHFFFAOYSA-N']))
    # Key -> Ids
    print(key2id(token, 'VNWKTOKETHGBQD-UHFFFAOYSA-N'))
    print(key2id(token, ['VNWKTOKETHGBQD-UHFFFAOYSA-N', 'VLKZOEOYAKHREP-UHFFFAOYSA-N']))
    # id -> smi
    print(id2smiles(token, 'qm9:1'))
    print(id2smiles(token, ['qm9:1', 'qm9:543']))
    # id -> key
    print(id2key(token, 'qm9:1'))
    print(id2key(token, ['qm9:1', 'qm9:543']))
    # id -> inc
    print(id2inchi(token, 'qm9:1'))
    print(id2inchi(token, ['qm9:1', 'qm9:543']))
    # inc -> id
    print(inchi2id(token, 'InChI=1S/CH4/h1H4'))
    print(inchi2id(token, ['InChI=1S/CH4/h1H4', 'InChI=1S/C6H14/c1-3-5-6-4-2/h3-6H2,1-2H3']))
    # inc -> smi
    print(inchi2smiles(token, 'InChI=1S/CH4/h1H4'))
    print(inchi2smiles(token, ['InChI=1S/CH4/h1H4', 'InChI=1S/C6H14/c1-3-5-6-4-2/h3-6H2,1-2H3']))
    # inc -> key
    print(inchi2key(token, 'InChI=1S/CH4/h1H4'))
    print(inchi2key(token, ['InChI=1S/CH4/h1H4', 'InChI=1S/C6H14/c1-3-5-6-4-2/h3-6H2,1-2H3']))
