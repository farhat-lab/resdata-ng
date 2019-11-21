#!/usr/bin/env python

import pandas as pd
import sys
sys.path.insert(0, '.')
from bin import convert_to_biosample
from progress.bar import IncrementalBar
import re

with open("metadata/sources/cryptic_nejom_2018/spaghetti2.tsv","w") as outf:
    outf.write("BioSample\tcountry\tisoniazid\trifampicin\tethambutol\tpyrazinamide\n")
    with open("metadata/sources/cryptic_nejom_2018/spaghetti.tsv","r") as inp:
        # I get rid of the headers
        header=inp.readline()
        header2=inp.readline()
        for line in inp:
            data=re.split(' +',line)
            #print(data)
            # Should have the antibiotic resistance data (8 cols + the ID)
            if len(data) < 9:
                continue
            resistance_data=data[-9:-5]
            ncbi_id=data[-10]
            if re.match("^\(",data[-11]):
                country=data[-13]
            else:
                country=data[-12]
            outf.write("\t".join([ncbi_id,country, "\t".join(resistance_data)])+"\n")

tab=pd.read_csv("metadata/sources/cryptic_nejom_2018/spaghetti2.tsv",sep="\t")

#I filter out some problematic datasets. I will recover them later
## PRJNA413593: impossible to find the associations biosample -> isolate ID; for the other isolates: I can recover them
problematic_datasets=["PRJNA413593","PRJNA393378","PRJNA270697","SRP058221","SRS935924", "SRS935941", "SRS935943", "SRS935949","SRS935979","SRS935993"]
tab=tab[~tab.BioSample.isin(problematic_datasets)]

# I convert the biosamples when possible
biosamples=tab["BioSample"].tolist()
biosamples_clean=["" if str(x) == "nan" else x for x in biosamples]
list_of_biosamples=convert_to_biosample.convert_to_biosample(biosamples_clean)
tab["BioSample"]=list_of_biosamples

# geographic location data
# all the entries that have "Africa" as country map to South Africa
list_of_countries=tab["country"].tolist()
geo_d={'Birmingham':"UK", "Africa":"South Africa", "Mar;46(3):279-86":"Russia", "Italy_MGITstudy": "Italy", "South": "South Africa"}
correct_list_of_countries=[geo_d[i] if i in geo_d else i for i in list_of_countries] 
tab["country"]=correct_list_of_countries

# I rename the columns and I create an empty column for the isolation year
tab_md_uniq=tab_md_uniq.rename(columns={'country': 'isolation_country'})

tab.to_csv("")

