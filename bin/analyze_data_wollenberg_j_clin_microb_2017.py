#!/usr/bin/env python

import pandas as pd
from progress.bar import IncrementalBar

# load the data frame
df = pd.read_csv("resistance_data/sources/wollenberg_j_clin_microb_2017/wollenberg_2017_curated_phenotypes.tsv",sep="\t")

# I standardize the names of the antibiotics
cols = df.columns.tolist()
cols[2:] = ["ETHAMBUTOL","ISONIAZID","RIFAMPICIN","RIFABUTIN","PYRAZINAMIDE",
"AMIKACIN","KANAMYCIN","CAPREOMYCIN","CYCLOSERINE","ETHIONAMIDE","OFLOXACIN",
"PARA_AMINOSALICYLIC_ACID","STREPTOMYCIN"]
df.columns = cols

# No need to convert the biosamples

list_of_antibiotics = cols[2:]

with open("resistance_data/summary_tables/wollenberg_j_clin_microb_2017.res", "w") as outf:
    for idx, row in df.iterrows(): 
        for antb in list_of_antibiotics:
            res_status = row[antb]
            if pd.isnull(res_status):
                continue
            else:
                outf.write("\t".join([row[0], antb, res_status, "WOLLENBERG_J_CLIN_MICROB_2017"]) + "\n")


