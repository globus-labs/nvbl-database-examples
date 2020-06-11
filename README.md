# nvbtl-database-examples
nvbtl-database-examples

## Tables

The CoV database contains the following tables.

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
  

## Postgrest interface

