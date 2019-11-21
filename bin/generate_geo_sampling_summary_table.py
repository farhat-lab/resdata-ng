#!/usr/bin/env python

import glob

# dictionary containing all the data
l={}

# I fill the dictionary with the data
files_to_parse=glob.glob("metadata/sources/*/*.geo_sampling")
for f in files_to_parse:
    print("- analyzing {}".format(f))
    with open(f,"r") as inp:
        header=inp.readline()
        for line in inp:
            entry=line.rstrip("\n").split("\t")
            biosample=entry[0]
            country=entry[1]
            year=entry[2]
            tag=entry[3]
            if biosample in l:
                if country:
                    l[biosample]["isolation_country"][country]=1
                if year:
                    l[biosample]["collection_year"][year]=1
                l[biosample]["tag"][tag]=1
            else:
                l[biosample]={}
                l[biosample]["isolation_country"]={}
                l[biosample]["collection_year"]={}
                l[biosample]["tag"]={}
                if country:
                    l[biosample]["isolation_country"][country]=1
                if year:
                    l[biosample]["collection_year"][year]=1
                l[biosample]["tag"][tag]=1

# I manage the collisions and write down the final tables
counter_ok=0
counter_collisions=0
# I will write the good data here
with open("./metadata/summary_tables/geo_sampling.txt","w") as outf1:
    outf1.write("BioSample\tisolation_country\tcollection_year\ttag\n")
    # I will write the data that need some review here
    with open("./metadata/summary_tables/geo_sampling_collisions.txt","w") as outf2:
        outf2.write("BioSample\tisolation_country\tcollection_year\n")
        for item in l:
            count_isolation_country=len(l[item]["isolation_country"])
            count_collection_year=len(l[item]["collection_year"])
            if count_isolation_country <= 1 and count_collection_year <= 1:
                outf1.write("{}\t{}\t{}\t{}\n".format(item, ",".join(l[item]["isolation_country"]), ",".join(l[item]["collection_year"]), ",".join(l[item]["tag"])))
                counter_ok=counter_ok+1
            else:
                print("{}:".format(item),l[item])
                outf2.write("{}\t{}\t{}\t{}\n".format(item, ",".join(l[item]["isolation_country"]), ",".join(l[item]["collection_year"]), ",".join(l[item]["tag"])))
                counter_collisions=counter_collisions+1

print("* Statistics")
print("  - No. of isolates analyzed: {}".format(str(counter_ok+counter_collisions)))
print("  - No. of isolates OK: {} ({:.1%})".format(str(counter_ok), (counter_ok/(counter_ok+counter_collisions))))
print("  - No. of collisions: {} ({:.1%})".format(str(counter_collisions), (counter_collisions/(counter_ok+counter_collisions))))
print("* check the file ./metadata/summary_tables/geo_sampling_collisions.txt to solve the collisions.")




