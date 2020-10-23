#!/usr/bin/env python3

import re
import pandas as pd
from bin import convert_to_biosample

#I load the CSV
my_data = pd.read_csv("resistance_data/sources/phelan_sci_rep_2019/Phil_WGS_database_180_DRS_2_isolates.csv")

my_data["tag"]=["phelan_sci_rep_2019"]*my_data.shape[0]

#.geo_sampling file should be like this:
#BioSample       isolation_country       collection_year tag
#SAMN08708150    Ukraine         zignol_LID_2018

# converting the biosamples
biosamples = my_data["ENA_run_accession"].tolist()
rlist = ["^ERR", "^SRR", "^SRS"]
list_of_biosamples = [convert_to_biosample.convert_to_biosample_simplified([x])[0] if re.search(rlist[0],x) or re.search(rlist[1],x) or re.search(rlist[2],x) else "" for x in biosamples]

my_data["BioSample"]=list_of_biosamples
my_data["isolation_country"]=my_data["country"]
my_data["collection_year"]=[""]*my_data.shape[0]

try:
    os.makedirs("metadata/sources/phelan_sci_rep_2019")
except:
    print("metadata/sources/phelan_sci_rep_2019/ has been created")
pass

my_data.to_csv("metadata/sources/phelan_sci_rep_2019/phelan_sci_rep_2019.geo_sampling",sep="\t", columns=['BioSample','isolation_country','collection_year','tag'], index=False)

# NOw I FOCUS ON THE RESISTANCE DATA
with open("resistance_data/summary_tables/phelan_sci_rep_2019.res","w") as outf:
    for k, row in my_data.iterrows():
        for antb in ['amikacin', 'capreomycin', 'ethambutol', 'isoniazid', 'kanamycin', 'levofloxacin', 'rifampicin', 'streptomycin']:
            current_biosample=row["BioSample"]
            numeric_res_status=row[antb]
            if numeric_res_status==0:
                outf.write("{}\t{}\tS\tPHELAN_SCI_REP_2019\n".format(current_biosample, antb.upper()))
            if numeric_res_status==1:
                outf.write("{}\t{}\tR\tPHELAN_SCI_REP_2019\n".format(current_biosample, antb.upper()))


