#!/usr/bin/env python

import sys
sys.path.insert(0, "./")
import pandas as pd
from metatools_ncbi import convert_to_biosample
from progress.bar import IncrementalBar

# load the data frame
df = pd.read_csv("resistance_data/sources/Dheda_Lancet_RM_2017/Dheda-2017_phenotype_data.csv")

#select only columns with Accession, Antibiotics, and geographic origin
df = df[['id', 'geographic_source', 'rifampicin',
       'isoniazid', 'ethambutol', 'pyrazinamide', 'streptomycin', 'amikacin',
       'kanamycin', 'capreomycin', 'ofloxacin', 'moxifloxacin', 'cycloserine',
       'ethionamide', 'para-aminosalicylic_acid', 'rifabutin', 'clofazimine',
       'linezolid', 'clarithromycin']]

#make all columns names upper string as in all other files in this repo
df.columns = map(str.upper, df.columns)


#rename columns where necessary
cols = df.columns.tolist()
cols[0] = 'Accession'
df.columns = cols

# I convert the run ids to biosamples
ids_to_convert = df['Accession'].tolist()
list_of_biosamples=convert_to_biosample.convert_to_biosample(ids_to_convert)
df['Accession']=list_of_biosamples

list_of_antibiotics = cols[2:]

#create the res file for this dataset 

with open("resistance_data/summary_tables/dheda_LID_2017.res", "w") as outf:
    for idx, row in df.iterrows(): 
        for antb in list_of_antibiotics:
            value = row[antb]
            res_status = ""
            if pd.isnull(value):
                continue
            elif value == 0:
                res_status = "S"
            elif value ==1:
                res_status = "R"
            outf.write("\t".join([row[0], antb, res_status, "DHEDA_Lancet_RM_2017"]) + "\n")