#!/usr/bin/env python

import sys
import glob
import json
import dateutil.parser as dateparser
import country_converter as coco
import pandas as pd
import re

# I initialize the country converter
cconverter = coco.CountryConverter()

#dictionary to store the metadata I need
d={}

print("* parsing the data")
# I parse all the json files and I get the metadata I need: BioSample, isolation_country, collection_year
## the isolation_country and collection_year are going to be messy
list_json_files=glob.glob("./metadata/sources/ncbi/*.json")
counter=0
total=len(list_json_files)

for f in list_json_files:
    counter=counter+1
    print("-- analyzing {} ({}/{})".format(f, str(counter), str(total)))
    # I load the json file
    with open(f, "r") as json_file:
        data = json.load(json_file)
        if data["biosample"]:
            biosample=data["accession"]
            try:
                geo_loc=data["geographic_location"]
            except:
                geo_loc=""
                pass
            try:
                coll_date=data["collection_date"]
            except:
                coll_date=""
                pass
            d[biosample]={}
            d[biosample]["collection_date"]=coll_date
            d[biosample]["geographic_location"]=geo_loc

# I try to make the isolateion_country and collection_year right
list_biosamples=[]
list_countries=[]
list_dates=[]
for entry in d:
    list_biosamples.append(entry)
    list_countries.append(d[entry]["geographic_location"])
    list_dates.append(d[entry]["collection_date"])

print("* converting countries")
# I cut the entries that are like this "USA: Boston"
#print(set(list_countries))
list_countries_cut=[re.sub("\:.+","",i) if type(i)==str else "" for i in list_countries]
list_countries_converted=cconverter.convert(names = list_countries_cut, to = 'name_short')
# I delete "not found, missing from the country names"
list_countries_converted_clean=["" if i in ["not found"] else i for i in list_countries_converted]

print("* converting dates")
list_dates_parsed=[]
for current_date in list_dates:
    try:
        current_year=dateparser.parse(current_date).year
    except:
        print("-- Problems parsing \"{}\". Skipping this!".format(current_date)) 
        current_year=""
    list_dates_parsed.append(current_year)


# I write down the final file with the processed data
print("* writing down the final data")
df = pd.DataFrame(list(zip(list_biosamples, list_countries_converted_clean, list_dates_parsed)), 
               columns =['BioSample', 'isolation_country',"collection_year"]) 
# I append a column with the tag
df["tag"]=["ncbi"]*df.shape[0]


df.to_csv("./metadata/sources/ncbi/ncbi.geo_sampling", index=False, sep="\t")
