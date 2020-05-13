# Resdata-NG

This is the Farhat lab repository for MTB antibiotic resistance data and isolate metadata. To access the version 1 of the database, please click [here](https://github.com/farhat-lab/resdata).

## Design

### The directory tree



This repository is organized in folders:

- `bin/` 
  
  - All scripts used to analyze/filter/clean the data are available in the `bin/` folder and **must** be under version control.
- `metadata/sources/`
  
  - This directory contains all the raw data from the different studies that provide information on the metadata of MTB isolates. For instance the the metadata on MTB isolates downloaded from the NCBI are stored inside `metadata/sources/ncbi/`. The raw data of each study **must** be under version control.
- `metadata/summary_tables/`
  
  - Two files must be present: `geo_sampling_collisions.txt`  `geo_sampling.txt`. The file `geo_sampling.txt` stores the metadata for the isolates where there is no disagreement between different data sources. The file `geo_sampling_collisions.txt` allows to quickly detect the cases in which different data sources disagree. Both files are generated by the script `bin/generate_geo_sampling_summary_table.py`.
- `resistance_data/sources/`
  
  - This directory contains all the raw data from the different studies that provide information on the resistance data of MTB isolates. For instance the the metadata on MTB isolates downloaded from PATRIC (a public database of ) are stored inside `metadata/sources/ncbi/`. The raw data of each study **must** be under version control.
- `resistance_data/summary_tables/`
  
  - Three files must be present: `mic.summary`, which is a summary table of all the MIC data;  `mic.res`, where the MIC data are converted to binary phenotypes (`S|R`) and `resistance_summary.txt`: summary table with the binary phenotype data (`S|R`). Both files are generated by the script `bin/generate_amr_summary_table.py`.
  

### File formats for the intermediate files

Intermediate files are necessary to have a standard format so that all data can be merged and we can check for collisions (cases in which two or more data sources do not agree about a datum). Here are the current formats for the intermediate files:

- `.geo_sampling`  

```
BioSample  isolation_country  collection_year  tag
```

- `.res`

```
BioSample  antibiotic  [S|R]  tag
```

- `.mic`

```
BioSample  antibiotic  media  concentration_tested  [S|R]  tag
```

**NOTE:** all these files are `.tsv` (tab separated values) files.

### How to add new data to the database

- Download the raw data on: `./resistance_data/sources/<source_name>`
  - right away make a commit for the new data
  - add the new data source to the list of current data sources on this file
- Depending if the data source provides metadata or resistance data:
  - metadata: add a script (should be placed inside the directory `bin/`) to generate a `.geo_sampling` file (see above for the details about the format) inside the `./resistance_data/sources/<source_name>` directory.
  - resistance data: add a script (should be placed inside the directory `bin/`) to generate a `.res`, a `.mic`  files (see above for the details about the format)
- Write a new section of the documentation (see examples below)
-  run the scripts that generate the final tables for the metadata and resistance data:

```
./bin/generate_geo_sampling_summary_table.py
./bin/generate_amr_summary_table.py
```
- commit the new versions of the summary tables and add a tag to let people know which version of the db they are using.
  - rules for the version numbering: `2.x.y`
    - `x` = a new source (or more than one!) was added and we got new information about some isolates
    - `y` = solved collisions or corrected some bugs
    - we will start with version `2.0.0` in order to do not generate confusion with the repository resdata.



## Current data sources (Summary)

| Source | downloaded data | geo/sampling data | resistance data |
| ---- | :-----------: | :----------: | :--: |
| NCBI | ● | ● |        -        |
| Patric| ● | ● | ● |
| ReSeqTB | ● | - | partial |
| cryptic_nejom_2018 |        ●        |      pending      |     partial     |
| coll_nat_gen_2018 | ● | pending | ● |
| hicks_nat_micro_2018 | ● | pending | ● |
| wollenberg_j_clin_microb_2017 | ● | pending | ● |
| farhat_lab_pools_cetr_tdr | ● | ● | ● |
| dheda_LRM_2017 | ● | pending | ● |
| zignol_LID_2018 | ● | pending | ● |

last update: 2020-05-13 -- Matthias Groeschel

## Current data sources

### NCBI (metadata)

#### Software requirements
To perform this analysis the following python packages are required:  `python-dateutils, country_converter, pandas`

#### Getting and analyzing the metadata

We use the python package metatools_ncbi to download all the metadata associated to MTB strains available on NCBI. "txid1773" is the NCBI taxonomic id for _Mycobacterium tuberculosis_ (MTB). 

```
mkdir -p metadata/sources/ncbi/
metatools_download biosamples -t txid1773 metadata/sources/ncbi/
```

Then we run a python script to parse the metadata and get the geo/sampling metadata:

```
./bin/analyze_data_ncbi.py > metadata/sources/ncbi/log_ncbi.txt 2>&1
```

### Coll Nat Gen 2018 (resistance data)

We are referring to this [paper](https://www.nature.com/articles/s41588-017-0029-0). I just have to run a script:

```
python3 ./bin/analyze_data_coll_nat_gen_2018.py
```

### Hicks Nat Micro 2018 (resistance data)

We are referring to this [paper](https://www.nature.com/articles/s41564-018-0218-3). I just have to run a script:

```
python3 ./bin/analyze_data_hicks_nat_micro_2018.py
```

### Dheda Lancet RM 2017 (resistance Data)

We are reffering to this [paper](https://www.ncbi.nlm.nih.gov/pubmed/28109869). I just have to run a script:

```
python3 ./bin/analyze_data_dheda_2017.py
```

### Zignol Lancet ID 2018 (resistance data, metadata)

We are reffering to this [paper](https://www.ncbi.nlm.nih.gov/pubmed/29574065/?utm_source=gquery&utm_medium=referral&utm_campaign=CitationSensor). I just have to run a script:

```
python3 ./bin/analyze_zignol_LID_2018.py
```

### Patric (resistance data, metadata)

#### Software requirements

- Download the Patric CLI (Command Line Interface) in order to download the Patric data (tested on Ubuntu). **Note: you need to have root access to install the CLI. So I do not think you can install it on a cluster.**

  - Download  the CLI of Patric from this location: https://github.com/PATRIC3/PATRIC-distribution/releases/download/1.026/patric-cli-1.026-1.fc29.x86_64.rpm
  - Install alien and convert the rpm package to deb. Then install the deb package:

  ```
  sudo apt install alien
  sudo alien patric-cli-1.026-1.fc29.x86_64.rpm
  sudo dpkg -i patric-cli_1.026-2_amd64.deb
  ```

  - The PATRIC CLI seems to require additional packages. You can install them with:

```
sudo apt install libjson-xs-perl libgetopt-long-descriptive-perl
```
#### Analyzing the data
You can download the raw data with the following script:
```
python3 ./bin/get_amr_data_patric.py
```
Then you can get the output files (.geo, .res, .mic ) with:
```
python3 ./bin/analyze_data_patric.py
```

### ReseqTB (resistance data)

Create the directory to store the data:

```
mkdir -p resistance_data/sources/reseqtb
```

Log-in on the ReseqTB web site and click on "data access" > "data export and analysis" > "CSV export files" to download the latest version of the database. Save the .zip on resistance_data/sources/reseqtb. Then unzip it:

```
cd resistance_data/sources/reseqtb 
unzip fullExportDb-1254-External-CSV.zip
```

The data are available on "resistance_data/sources/reseqtb/msf.csv". 

Here is the command to parse the data:

```
python3 ./analyze_data_reseqtb.py
```



### Cryptic_nejom_2018 (metadata, resistance data)

This is the original paper:

- Prediction of Susceptibility to First-Line Tuberculosis Drugs by DNA Sequencing, N Engl J Med 2018;  379:1403-1415, doi:  10.1056/NEJMoa1800474). 

In the supplementary material there is a table with geographic location data and resistance data. Here is the procedure to analyze the data:

1. We convert the `PDF` to text. Then we filter out some unwanted rows (those that do not contain any information or that have information on species other than _M. tuberculosis_):

```
cd metadata/sources/cryptic_nejom_2018/
pdftotext -layout -f 10 -l 95 nejmoa1800474_appendix.pdf prova.txt
cat prova.txt|grep -v "^ "|grep -v "^$" | grep -v "orygis" | grep -v "bovis" | grep -v "caprae" |grep -v "microti"|grep -v "BCG" > spaghetti.txt
```

2. now we can parse the `.txt` file:

```
python3 ./bin/analyze_data_nejom_cryptic_2018.py
```



### Wollenberg J Clin Microbiol 2017

"Wollenberg, K. R. et al. Whole-Genome Sequencing of _Mycobacterium tuberculosis_ Provides Insight into the Evolution and Genetic Composition of Drug-Resistant Tuberculosis in Belarus. J. Clin. Microbiol. 55, 457–469 (2017)". The supplementary material contains a table with binary resistance data linked to isolate names, and another suppl. table with isolate names linked to NCBI accessions. The source table in `resistance_data/sources/` was hand-curated from these two suppl. tables. 

```
python3 ./bin/analyze_data_wollenberg_j_clin_microb_2017.py
```



### Farhat lab (pools, cetr, tdr)

- The resistance and `.geo_sampling` data were extracted using the following script:

```
./bin/analyze_data_farhat_lab_pools_cetr_tdr.py 
[INFO] Total number of entries: 16288
[INFO] 2338 entries were discarded (14.4%)
* no_media_method: 130
* conc_tested_not_allows_decision: 2208
* new_regex_needed: 0
[INFO] writing down the .geo_sampling data
```



### Already curated isolates without source data  

ongoing



## Collisions
At the moment there are 875 collisions listed on: `./resistance_data/summary_tables/collisions_summary.txt`

### Examples

There are inconsistencies between `RESEQTB` and `NEJOM_CRYPTIC_2018` (< 200 / estimated):

```
cat ./resistance_data/summary_tables/*.res |tr "\t" " "|grep  "SAMEA1015939 ETHAMBUTOL"
SAMEA1015939 ETHAMBUTOL S NEJOM_CRYPTIC_2018
SAMEA1015939 ETHAMBUTOL S PATRIC
SAMEA1015939 ETHAMBUTOL S PATRIC
SAMEA1015939 ETHAMBUTOL R RESEQTB
```

Analysis: 

```
IS-1017 / ETHAMBUTOL / R / ERR067767. Correponds to BioSample: SAMEA1015939; SRA: ERS050970. Includes ERR067767.
```

There are also inconsistencies between the same study:

```
cat ./resistance_data/summary_tables/*.res |tr "\t" " "|grep  "SAMEA3558109 RIFAMPICIN"
SAMEA3558109 RIFAMPICIN S COLL_NAT_GEN_2018
SAMEA3558109 RIFAMPICIN R COLL_NAT_GEN_2018
```

## Changelog

- version 2.0.0
  - summary tables for the metadata (geographic location, collection year). Sources: NCBI and PATRIC. 

