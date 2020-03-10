#!/usr/bin/env python

import sys
sys.path.insert(0, "./")
import pandas as pd
from bin import convert_to_biosample
from progress.bar import IncrementalBar

# load the data frame
df = pd.read_csv("resistance_data/sources/hicks_nat_micro_2018/hicks_suppl_table_cut.tsv",sep="\t")


# I convert the run ids to biosamples
ids_to_convert = df['sra_accession'].tolist()
list_of_biosamples=convert_to_biosample.convert_to_biosample(ids_to_convert)
df['sra_accession']=list_of_biosamples

list_of_antibiotics = df.columns[3:].tolist()

with open("resistance_data/summary_tables/hicks_nat_micro_2018.res", "w") as outf:
    for idx, row in df.iterrows(): 
        for antb in list_of_antibiotics:
            res_status = row[antb]
            outf.write("\t".join([row[0], antb.upper(), res_status, "HICKS_NAT_MICRO_2018"]) + "\n")


