#!/usr/bin/env python

import pandas as pd
import sys
sys.path.insert(0, '.')
from bin import convert_to_biosample
from progress.bar import IncrementalBar
import re

with open("metadata/sources/cryptic_nejom_2018/spaghetti2.tsv","w") as outf:
    outf.write("BioSample\tcountry\tISONIAZID\tRIFAMPICIN\tETHAMBUTOL\tPYRAZINAMIDE\n")
    with open("metadata/sources/cryptic_nejom_2018/spaghetti.txt","r") as inp:
        # I get rid of the headers
        header=inp.readline()
        header2=inp.readline()
        for line in inp:
            data=re.split(' {2,}',line)
            print(data)
            # Should have the antibiotic resistance data (8 cols + the ID)
            if len(data) < 9:
                continue
            resistance_data=data[-8:-4]
            print(resistance_data)
            ncbi_id=data[-9]
            country=data[-11]
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
tab["OriginalIDs"]=biosamples
tab["BioSample"]=list_of_biosamples

tab.to_csv("resistance_data/sources/nejom_cryptic_2018/spaghetti3.tsv",sep="\t") 

list_of_antibiotics = tab.columns[2:6].tolist()
with open("resistance_data/summary_tables/nejom_cryptic_2018.res", "w") as outf:
    for idx, row in tab.iterrows(): 
        for antb in list_of_antibiotics:
            res_status = row[antb]
            if pd.isnull(res_status):
                continue
            else:
                outf.write("\t".join([row[0], antb.upper(), res_status, "NEJOM_CRYPTIC_2018"]) + "\n")


# UPDATE THE GEOGRAPHIC LOCATION DATA
# all the entries that have "Africa" as country map to South Africa
list_of_countries=tab["country"].tolist()
geo_d={'Birmingham':"UK", "Africa":"South Africa", "Mar;46(3):279-86":"Russia", "Italy_MGITstudy": "Italy", "South": "South Africa"}
correct_list_of_countries=[geo_d[i] if i in geo_d else i for i in list_of_countries] 
tab["country"]=correct_list_of_countries

# I rename the columns and I create an empty column for the isolation year
tab=tab.rename(columns={'country': 'isolation_country'})


