#!/usr/bin/env python

import sys
sys.path.insert(0, "./")
import pandas as pd

# load the data frame
df = pd.read_csv("resistance_data/sources/zignol_LID_2018/zignol_resdata_combined.tab", sep = '\t')

#select only columns with Accession, Antibiotics, and geographic origin
df = df[['BioSample','Country', 'rif_pheno', 'inh',
       'ofx2_final', 'mfx2', 'lfx15', 'gfx2', 'kan', 'amk', 'cap',
       'pza']]

#rename the columns 
df.rename(columns={'BioSample':'Accession','Country':'country','rif_pheno':'RIFAMPICIN',
                  'inh':'ISONIAZID','ofx2_final':'OXIFLOXACIN','mfx2':'MOXIFLOXACIN',
                  'lfx15':'LEVOFLOXACIN','gfx2':'GATIFLOXACIN','kan':'KANAMYCIN',
                  'kan':'KANAMYCIN','amk':'AMIKACIN','cap':'CAPREOMYCIN','pza':'PYRAZINAMIDE'}, inplace = True)

#make a list of the columns with antibiotics
list_of_antibiotics = df.columns.tolist()[2:]

#remove the two countries where we have no resistance data for
df = df[~df['country'].str.contains("Ukraine")]
df = df[~df['country'].str.contains("Azerbaijan")]

#write it to a new *res file
with open("resistance_data/summary_tables/zignol_LID_2018.res", "w") as outf:
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
            outf.write("\t".join([row[0], antb, res_status, "ZIGNOL_2018"]) + "\n")
