# NVBL Database Examples

This repository contains programs for using the REST API to access the nCoV Postgres database. 

![](https://github.com/globus-labs/nvbl-database-examples/blob/master/nCoV.jpg)

## 1) REST API access to the nCoV database

The REST API, accessible at `https://covid-ws-01.alcf.anl.gov/rpc`, supports nine methods of the form `<from>2<to>`, where `<from>` is one of `[id, key, smiles]`, `<to>` is one of `[id, inchi, key, smiles]`, and `<from>`!=`<to>`, and:
* `id` is an identifier used in the nCoV database, which have the form XXX:ident, where XXX is the source name (as listed at https://2019-ncovgroup.github.io/data/) and ident is an identifier used by that source.
* `inchi` is an InChI
* `key` is an InChIKey
* `smiles` is a SMILES

You can use theREST API client, the REST API directly (e.g., via `curl`) or via the Python script `lookup.py`. 
### a) Accessing the nCoV database via the client
Install the NVBL Client by calling `pip install -e .` from within this repository.

Example Usage:
```python
from nvbl_client import NVBLClient

cl = NVBLClient()
res = cl.search_all('smiles', 'CCC(COC(=O)C(NP(=O)(Oc1ccccc1)OCC1OC(C(C1O)O)(C#N)c1ccc2n1ncnc2N)C)CC')
res
```

Return Value:
```json
{
	"key": ["RWWYLEGWBNMMLJ-UHFFFAOYSA-N"],
	"inchi": ["InChI=1S/C27H35N6O8P/c1-4-18(5-2)13-38-26(36)17(3)32-42(37,41-19-9-7-6-8-10-19)39-14-21-23(34)24(35)27(15-28,40-21)22-12-11-20-25(29)30-16-31-33(20)22/h6-12,16-18,21,23-24,34-35H,4-5,13-14H2,1-3H3,(H,32,37)(H2,29,30,31)"],
	"id": ["lit:LIT-1",
		"lit:LIT-110",
		"lit:LIT-476",
		"lit:LIT-503",
		"lit:LIT-558",
		"lit:LIT-578",
		"lit:LIT-607",
		"lit:LIT-689",
		"lit:LIT-715",
		"lit:LIT-94",
		"pch:PC-46676083"
	]
}
  ```

### b) Accessing the nCoV database via `curl`

To ask what identifier(s) are record for the SMILES `'C'`:
```
curl https://covid-ws-01.alcf.anl.gov/rpc/smiles2id --request POST --data '{"input":"C"}' -H "Content-Type: application/json"
```
The response is a string containing a list of zero or more "output":<value> pairs: in this case, as there are five entries in the CoV database for the SMILES `C`, the following five identifiers:
```
 [{"output":"chm:CHEMBL17564"}, 
 {"output":"g13:1"}, 
 {"output":"mcu:MCULE-1431015236"}, 
 {"output":"pch:PC-281"}, 
 {"output":"qm9:1"}]
```

### c) Accessing the nCoV database via the `lookup.py` program

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

### d) The `test_lookup.sh` shell script

The shell script `test_lookup.sh` runs `lookup.py` for each non-identical combination of (id,inchi,key,smiles)x(id,inchi,key,smiles).

## 2) Direct access to the nCoV database

Authorized individuals with access to ALCF computers can access the nCoV database directly from Cooley login nodes (`cooley.alcf.anl.gov`) via 
```
psql -h covid-db-01.fst.alcf.anl.gov -U USERID -p 5432 -d emolecules
```

### Tables

The nCoV database contains the following tables, with a * by a field meaning that it is indexed.

* Four tables for navigating among the ~4.2B entries obtained from the 24 sources listed at https://2019-ncovgroup.github.io/data/, with `id` being a unique per-table number; `md5` = `md5(smiles)` (i.e., the MD5 hash of the SMILES string); `smi` a canonicalized SMILES string; `ide` an identifier, in the form `XXX:identifier` (`XXX` being a three-letter source label, as defined at the web site); `key` an InChIkey; and `inc` an InChI.
  * `m2s(id, md5, smi)`
  * `m2i(id, md5, ide)`
  * `m2k(id, md5, key)`
  * `k2n(id, key, inc)`

* 1 table that gives the number of occurrences for any SMILES with >1 occurence in the dataset:
  * `counts(md5*, count*)`
 
* 46 tables for mapping from (source, identifier) pairs to (file, line-number) pairs within the computed data to be found at https://2019-ncovgroup.github.io/data/ (with XXX being, again, a three-letter source label):
  * `XXX_fp_location(identifier, filename, line-number)`
  * `XXX_de_location(identifier, filename, line-number)`
  
Note that the `m2i`, `m2s`, etc., tables includes various duplicates. For example:
 
```
select count(distinct id), count(distinct md5), count(distinct ide) from m2i;
4207033824 | 3865672599 | 4206933842
```
That is, the 4.2B entries in `m2i` correspond to only 3.9B unique SMILES; this is because some SMILES map to >1 identifier, as detailed in the `counts` table. Furthermore, there are 4207033824-4206933842=99982 fewer identifiers than entries; this is because a few identifiers map to >1 SMILES (the reason seems to be isomers). 

We also find that the number of unique InChiKeys is 27,438,472 less than the number of SMILES:
```
select count(distinct id), count(distinct md5), count(distinct key) from m2k;
4207033824 | 3865672599 | 3838234127
```
This is because we do not have an InChI for every SMILES.


## 3) Some Code Examples

### Example: Find Ids in a file `NCATS_Spike_ACE2_inhibition.tsv` downloaded from NCATS, for which the 21st Column is a SMILES

1) Extract SMILESs from NCAT input file

```
        awk -F "\t" '{print $21}' NCATS_Spike_ACE2_inhibition.tsv > ~/data/ncat_smiles.smi
```

2) Canonicalize, with a version of `canonicalize.py` that does NOT remove duplicates (as we want to have one output for each row in input CSV file)

```
        python canonicalize.py -f ~/data/ncat_smiles.smi -o ~/data/Output
```

3) Lookup

```
        python lookup_all.py smiles id file Output/can_smiles-0.smi > ~/data/ncat_smiles_locations.tsv
```

4) Append new columns to `NCATS_Spike_ACE2_inhibition.csv` as two extra columns.
  
  
## 4) Acknowlegdments

Thanks to Ben Lenard, Doug Waldron, and Skip Reddy for much help with the nCoV database.
