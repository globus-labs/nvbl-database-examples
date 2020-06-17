# NVBTL Database Examples

This repository contains programs for using the REST API to access the nCoV Postgres database. 

![](https://github.com/globus-labs/nvbtl-database-examples/blob/master/nCoV.jpg)

## 1) REST API access to the nCoV database

The REST API, accessible at `https://covid-ws-01.alcf.anl.gov/rpc`, supports nine methods of the form `<from>2<to>`, where `<from>` is one of `[id, key, smiles]`, `<to>` is one of `[id, inchi, key, smiles]`, and `<from>`!=`<to>`, and:
* `id` is an identifier used in the nCoV database, which have the form XXX:ident, where XXX is the source name (as listed at https://2019-ncovgroup.github.io/data/) and ident is an identifier used by that source.
* `inchi` is an InChI
* `key` is an InChIKey
* `smiles` is a SMILES

You can use the REST API directly (e.g., via `curl`) or via the Python program `lookup.py`. 

### a) Accessing the nCoV database via `curl`

You first need to obtain a JWT token, e.g. as follows (you must have a USERID and PASSWORD):
```
curl --header "Content-Type: application/json"   --request POST   --data '{"email":"USERID", "pass":"PASSWORD"}' https://covid-ws-01.alcf.anl.gov/rpc/login --insecure
```
and store the token in a Bash shell variable:
```
TOKEN=<long-token-string>
```

Then, you can, for example ask what identifier(s) are record for the SMILES `'C'`:
```
curl https://covid-ws-01.alcf.anl.gov/rpc/smiles2id --request POST --data '{"input":"C"}' -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" --insecure
```
The response is a string containing a list of zero or more "output":<value> pairs: in this case, as there are five entries in the CoV database for the SMILES `C`, the following five identifiers:
```
 [{"output":"chm:CHEMBL17564"}, 
 {"output":"g13:1"}, 
 {"output":"mcu:MCULE-1431015236"}, 
 {"output":"pch:PC-281"}, 
 {"output":"qm9:1"}]
```


### b) Accessing the nCoV database via the `lookup.py` program

The program `lookup.py` allows access to the Postgres database tables via the Postgrest API. It is called as follows:
```
python lookup.py <from> <to> <from-entity>
```
where `<from>` and `<to>` are each one of `id`, `inchi`, `key`, or `smiles`, and `<from-entity>` is the string that is to be looked up. (Note that `<from>=inchi` is supported, with the ChemSpider API used to map from InChI to Key.) 
It writes to standard output a list of zero-or-more entities found in the CoV database. For example:
```
python lookup.py smiles id C
```
returns five identifiers, indicating that there are five entries in the CoV database for the SMILES `C`:
```
['chm:CHEMBL17564', 'g13:1', 'mcu:MCULE-1431015236', 'pch:PC-281', 'qm9:1']
```
Symmetrically, a call `python lookup.py id smiles pch:PC-281` returns one SMILES, `['C']`.

Before running the program, you need to create a JWT Token (which must be periodically renewed) and store it in your environment. As above, you generate the token as follows:

```
curl --header "Content-Type: application/json"   --request POST   --data '{"email":"USERID", "pass":"PASSWORD"}' https://covid-ws-01.alcf.anl.gov/rpc/login --insecure
```
You then store the token in your environment as follows:
```
export TOKEN=<long-token-string>
```

### c) The `test_lookup.sh` shell script

The shell script `test_lookup.sh` runs `lookup.py` for each non-identical combination of (id,inchi,key,smiles)x(id,inchi,key,smiles).

## 2) Direct access to the nCoV database

Authorized individuals with access to ALCF computers can access the nCoV database directly from Cooley login nodes (`cooley.alcf.anl.gov`) via 
```
psql -h covid-db-01.fst.alcf.anl.gov -U USERID -p 5432 -d emolecules
```

### Tables

The nCoV database contains the following tables.

* Four tables for navigating among the ~4.2B entries obtained from the 24 sources listed at https://2019-ncovgroup.github.io/data/, with `id` being a unique per-table number; `md5` = `md5(smiles)`; `smi` a SMILES string; `ide` an identifier, in the form `XXX:identifier` (`XXX` being a three-letter source label, as defined at the web site); `key` an InChIkey; and `inc` an InChI.
  * `m2s(id, md5, smi)`
  * `m2i(id, md5, ide)`
  * `m2k(id, md5, key)`
  * `k2n(id, key, inc)`

* 1 table that gives the number of occurrences for any SMILES with >1 occurence in the dataset:
  * `counts(md5, count)`
 
* 28 tables for mapping from (source, identifier) pairs to (file, line-number) pairs within the computed data to be found at https://2019-ncovgroup.github.io/data/ (with XXX being, again, a three-letter source label):
  * `XXX_fp_location(identifier, filename, line-number)`
  * `XXX_de_location(identifier, filename, line-number)`
  
  
## 3) Acknowlegdments

Thanks to Ben Lenard, Doug Waldron, and Skip Reddy for much help with the nCoV database.
