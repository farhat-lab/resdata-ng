# A database of AMR data

It is very important for a lab that works on AMR to have a tool that allows to download the resistance data and process them consistently.

## Requirements

- reproducible pipeline. Should be tested by someone else.
- should be easy to update the database and there should be version control in place.
- I need a informative and sleek architecture of files
  - /who_critical_concentrations/ -- tables with the critical concentrations
  - /metadata/ -- _sources_ and _summary_tables_ 
  - /resistance_data/ 
  - /bin/
  
  
## Todo

- ~~script / functionality to convert a list of IDs to biosamples~~
- convert the ReseqTB data to the Patric format
- clean the Patric data
- somebody should test this pipeline
- ~~patric in the biosample section has entries that are not biosamples (e.g. SRS)~~  





- download the data
- extract geo metadata + sampling time
- res file
- mic file
- hqres?

## Summary data sources / analyzed data

| Source | downloaded data | geo/sampling data | resistance data |
| ---- | :-----------: | :----------: | :--: |
| NCBI | ✔ | ✔ | ? |
| Patric| ✔ | ✔ |      |
| ReSeqTB | ✔ | - |      |
| cryptic_nejom_2018 |               |              |      |

last update: 2019-11-19 -- Luca Freschi



- update db of geo + sampling time
- mic.summary
- mic.summary.res
- res.summary

## Data sources

### NCBI (geographic location, sampling)

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

### Patric (resistance data, geographic location, sampling)

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

I convert the reseqTB data to the PATRIC format

### Cryptic_nejom_2018 (geographic location, sampling, resistance data)

This is the original paper ("Prediction of Susceptibility to First-Line Tuberculosis Drugs by DNA Sequencing", N Engl J Med 2018;  379:1403-1415, doi:  10.1056/NEJMoa1800474). In the supplementary material there is a table with geographic location data and resistance data.




## Guidelines on how to add new data
- the raw data should be on: `./resistance_data/sources/<new_source>`
- understand the fields that are available and convert them to the patric scheme
- check inconsistencies in the names of the antibiotics, the media, the 
- for each source there should be:
  - a .res file: `<biosample> <antibiotic> <R|S>`
  - a .mic file: `<biosample> <antibiotic> <mic_result>`
  - a .hqres file (we know the media and the conc. of antibiotic tested and it fits the WHO critical conc.): `<biosample> <antibiotic> <media> <conc_tested> <R|S>`
- Then summary tables can be generated pooling together the results of multiple/all studies:
    - .mic.summary: summary table with all mic data
    - .mic.summary.res: converts the mic data into a binary phenotype (`S|R`)  
    - .res.summary: summary table with the binary phenotype data (`S|R`)
    - a summary table with the geographic location data (both NCBI and papers)

