#!/usr/bin/env python

import pandas as pd
import sys
import math
sys.path.insert(0, '.')
from bin import convert_to_biosample
from progress.bar import IncrementalBar
import country_converter as coco

patric_tsv="resistance_data/sources/patric/amr_data_20190912124554.tsv"
patric_metadata="metadata/sources/patric/patric_ids_geo_isoltime_data.tsv"

print("* loading data")
tab=pd.read_csv(patric_tsv, sep="\t")
# if the file does not have a biosample column I create it
if "genome.biosample_accession" not in tab.columns:
    # I load the file with the metadata
    tab_md=pd.read_csv(patric_metadata, sep="\t")
    # create a dictionary: patric ID -> biosample
    d_conv=dict(zip(tab_md["genome.genome_id"],tab_md["genome.biosample_accession"])) 
    # I create the genome.biosample_accession column in the main data frame
    biosamples=[]
    for entry in tab["genome.genome_id"]:
        if entry in d_conv:
            biosamples.append(d_conv[entry])
        else:
            biosamples.append("")
    # I remove all nan
    biosamples_clean=["" if str(x) == "nan" else x for x in biosamples]
    # I check that the biosamples are real biosamples
    list_of_biosamples=convert_to_biosample.convert_to_biosample(biosamples_clean)
    tab["genome.biosample_accession"]=list_of_biosamples
# I add the "patric" tag to the table
tab["tag"]=["patric"]*tab.shape[0]
# I just want the entries that have a biosample
tab=tab.loc[tab["genome.biosample_accession"] != ""]
# I just want the lab results
tab=tab.loc[tab["genome_drug.evidence"] == "Laboratory Method"]
# I correct the mistakes in the antibiotic names
tab["genome_drug.antibiotic"]=tab["genome_drug.antibiotic"].replace("para-aminosalicylic acid","para_aminosalicylic_acid")
tab["genome_drug.antibiotic"]=tab["genome_drug.antibiotic"].replace("rifampin","rifampicin")
# I correct the phenotypes
tab["genome_drug.resistant_phenotype"]=tab["genome_drug.resistant_phenotype"].replace("Susceptible","S")
tab["genome_drug.resistant_phenotype"]=tab["genome_drug.resistant_phenotype"].replace("Resistant","R")
# columns for the res file must be upper case
tab["genome.biosample_accession"] = tab["genome.biosample_accession"].str.upper() 
tab["genome_drug.antibiotic"] = tab["genome_drug.antibiotic"].str.upper() 
tab["genome_drug.resistant_phenotype"] = tab["genome_drug.resistant_phenotype"].str.upper() 
tab["tag"] = tab["tag"].str.upper() 

print("* writing down output files")
# I select the isolates that have phenotypes and I create a .res file
tab_res=tab[tab["genome_drug.resistant_phenotype"].isin(["S","R"])] 
tab_res.to_csv("resistance_data/summary_tables/patric.res",columns=["genome.biosample_accession","genome_drug.antibiotic","genome_drug.resistant_phenotype","tag"],sep="\t", header=False, index=False)

# I create a mic file
tab_mic_data=tab[tab["genome_drug.laboratory_typing_method"]=="MIC"]
tab_mic_data_valid=tab_mic_data[tab_mic_data['genome_drug.measurement'].notnull()]
tab_mic_data_valid.to_csv("resistance_data/summary_tables/patric.mic",columns=["genome.biosample_accession","genome_drug.antibiotic","genome_drug.measurement","genome_drug.measurement_unit","tag"],sep="\t", header=False, index=False)

#% I create a hq file (NOT IMPLEMENTED YET)

# I create a summary file for the grographic location data and the year of sampling
## I reload the file with the metadata
tab_md=pd.read_csv(patric_metadata, sep="\t")
biosamples=tab_md["genome.biosample_accession"].tolist()
biosamples_clean=["" if str(x) == "nan" else x for x in biosamples]
list_of_biosamples=convert_to_biosample.convert_to_biosample(biosamples_clean)
tab_md["genome.biosample_accession"]=list_of_biosamples
## I make sure that each row has a biosample accession
tab_md=tab_md.loc[tab_md["genome.biosample_accession"] != ""]
# I get the list of unique biosamples
#l=tab_md["genome.biosample_accession"].tolist()

# I select only the entries that are not duplicated
#% I could do something for the entries that are duplicated (right now they are just dropped, but a part of them they are fine -- J. Gardy)
tab_md_uniq=tab_md.drop_duplicates(subset ="genome.biosample_accession", keep = False) 
tab_md_uniq=tab_md_uniq.rename(columns={'genome.biosample_accession': 'BioSample', 'genome.isolation_country': 'isolation_country', 'genome.collection_year': 'collection_year'})

# I standardize the names of the countries
## I initialize the country converter
cconverter = coco.CountryConverter()
## Let's go
list_countries_to_parse=tab_md_uniq['isolation_country'].tolist()
list_countries_converted=cconverter.convert(names = list_countries_to_parse, to = 'name_short')
# I delete "not found, missing from the country names"
list_countries_converted_clean=["" if i in ["not found"] else i for i in list_countries_converted]
tab_md_uniq['isolation_country']=list_countries_converted_clean

# Let's convert also the dates (pandas considers the years as floats)
tab_md_uniq['collection_year']=tab_md_uniq['collection_year'].tolist()
tab_md_uniq['collection_year']=[str(int(i)) if i==i else i for i in tab_md_uniq['collection_year'].tolist()] 

# I append a column with the tag
tab_md_uniq["tag"]=["patric"]*tab_md_uniq.shape[0]


tab_md_uniq.to_csv("metadata/sources/patric/patric.geo_sampling",columns=["BioSample","isolation_country","collection_year","tag"], index=False, sep="\t")
