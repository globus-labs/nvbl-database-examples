# nvbtl-database-examples

This repository contains programs for using the REST API to access the Postgres database. 

## Using the REST API to access the Postgres database

The program `lookup.py` allows access to the Postgres database tables via the Postgrest API. It is called as follows:
```
python lookup.py <from> <to> <from-entity>
```
where `<from>` and `<to>` are each one of `id`, `inchi`, `key`, or `smiles`, and `<from-entity>` is the from string that is to be looked up. It writes to standard output a list of zero-or-more entities found in the CoV database. For example:
```
python lookup.py smiles id C
```
returns four identifiers, indicating that there are four entries in the CoV database for the SMILES `C`:
```
['chm:CHEMBL17564', 'g13:1', 'mcu:MCULE-1431015236', 'pch:PC-281', 'qm9:1']
```

Before running the program, you need to create a JWT Token (which must be periodically renewed) and stored it in your environment. To do this, you must have a USERID and PASSWORD:

```
curl --header "Content-Type: application/json"   --request POST   --data '{"email":"USERID", "pass":"PASSWORD"}' https://covid-ws-01.alcf.anl.gov/rpc/login --insecure
```
This returns a token, and you can then go:
```
setenv TOKEN=<long-token-string>
```

The shell script `test_all.sh` runs a simple example of each combination of (id,inchi,key,smiles)x(id,inchi,key,smiles).

## Tables

The CoV database contains the following tables. These are not directly accessible via the REST API, but we provide information on them here for people who have direct access to the CoV database.

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
