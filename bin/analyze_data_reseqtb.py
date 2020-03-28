import pandas as pd
import sys
sys.path.insert(0, '.')
from bin import convert_to_biosample
from progress.bar import IncrementalBar
import re

tab=pd.read_csv("resistance_data/sources/reseqtb/msf.csv")
# we want the DST data
tab=tab.loc[tab["MSTESTCD"]=="DST"]
# filtering out the borderline cases
tab=tab[tab.MSORRES.isin(["R","S"])]

# converting the biosamples
biosamples = tab["MSREFID"].tolist()
rlist = ["^ERR", "^SRR", "^SRS"]
list_of_biosamples = [convert_to_biosample.convert_to_biosample_simplified([x])[0] if re.search(rlist[0],x) or re.search(rlist[1],x) or re.search(rlist[2],x) else "" for x in biosamples]

tab["BioSample"]=list_of_biosamples
tab.to_csv("resistance_data/sources/reseqtb/intermediate_out_file.csv",sep="\t") 

# I select the ones that are OK
tab=pd.read_csv("resistance_data/sources/reseqtb/intermediate_out_file.csv",sep="\t")

tab=tab[tab.BioSample.notnull()]
# I correct the mistakes in the antibiotic names
tab["MSDRUG"]=tab["MSDRUG"].replace("PARA-AMINOSALICYLIC ACID","PARA_AMINOSALICYLIC_ACID")
tab["MSDRUG"]=tab["MSDRUG"].replace("AMOXICILLIN/CLAVULANATE","AMOXICILLIN")

with open("resistance_data/summary_tables/reseqtb.res", "w") as outf:
    for idx, row in tab.iterrows():
        antb=row['MSDRUG']
        res_status = row['MSORRES']
        if pd.isnull(res_status):
            continue
        else:
            outf.write("\t".join([row["BioSample"], antb, res_status, "RESEQTB"]) + "\n")



