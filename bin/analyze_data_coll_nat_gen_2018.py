#!/usr/bin/env python

import pandas as pd
from bin import convert_to_biosample
from progress.bar import IncrementalBar

# load the data frame
df = pd.read_csv("resistance_data/sources/coll_nat_gen_2018/coll_suppl_material.tsv",sep="\t")

# I standardize the names of the antibiotics
cols = df.columns.tolist()
## I just ned to standardise the pas
cols[11] = "PARA_AMINOSALISYLIC_ACID"
df.columns = cols

# I convert the run ids to biosamples
ids_to_convert = df['Accession'].tolist()
list_of_biosamples=convert_to_biosample.convert_to_biosample(ids_to_convert)
df['Accession']=list_of_biosamples

list_of_antibiotics = cols[1:]

with open("resistance_data/summary_tables/coll_nat_gen_2018.res", "w") as outf:
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
            outf.write("\t".join([row[0], antb, res_status, "COLL_NAT_GEN_2018"]) + "\n")


