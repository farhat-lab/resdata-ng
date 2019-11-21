#!/usr/bin/env python

import csv
import collections as coll

def get_who_thresholds(csv_crit_conc_who):
    who_thresholds=coll.defaultdict(lambda: coll.defaultdict(float))
    with open(csv_crit_conc_who,"r") as inp:
        header=inp.readline()
        fields=header.rstrip("\n").split("\t")
        reader = csv.reader(inp,delimiter="\t")
        for entry in reader:
            for x in range(1,len(fields)):
                try:
                    who_thresholds[entry[0]][fields[x]]=float(entry[x])
                except:
                    who_thresholds[entry[0]][fields[x]]=float('nan')
    return(who_thresholds)


#I provide the concentration to test and the dictionary of the data 
def is_who_compliant(antb,media,conc,dict_data_who):
    decision=False
    try:
        if float(dict_data_who[antb][media]) == float(conc):
            decision=True
    except:
        decision=False
    return(decision)


# Example
#is_who_compliant("CAPREOMYCIN","m7h11","5",who_thresholds)
