#!/usr/bin/env python
import csv
import re
import sys

sys.path.insert(0,'./')
from bin.critical_concentrations_who import *

details={
    "antb":["INH","RIF","RFB","EMB","STR","ETA","CIP","CYS","CAP","KAN","OFX","PAS","PZA","AMI","MOXI","PRO","CLO","LEVO","CLAR","GATI","AMOXCLAV","LIN"],
    "abbrev_antb":{
        "INH":"ISONIAZID",
        "RIF":"RIFAMPICIN",
        "RFB":"RIFABUTIN",
        "EMB":"ETHAMBUTOL",
        "STR":"STREPTOMYCIN",
        "ETA":"ETHIONAMIDE",
        "CIP":"CIPROFLOXACIN",
        "CYS":"CYCLOSERINE",
        "CAP":"CAPREOMYCIN",
        "KAN":"KANAMYCIN",
        "OFX":"OFLOXACIN",
        "PAS":"PARA_AMINOSALICYLIC_ACID",
        "PZA":"PYRAZINAMIDE",
        "AMI":"AMIKACIN",
        "MOXI":"MOXIFLOXACIN",
        "PRO":"PROTHIONAMIDE",
        "CLO":"CLOFAZIMINE",
        "LEVO":"LEVOFLOXACIN",
        "CLAR":"CLARITHROMYCIN",
        "GATI":"GATIFLOXACIN",
        "AMOXCLAV":"AMOXICILLIN",
        "LIN":"LINEZOLID",
    },
    "fields":["xref", "antb", "mic_summary", "conc_units", "res_class", "method", "media", "tag"]
}

with open("resistance_data/summary_tables/farhat_lab_pools_cetr_tdr.mic","w") as outf:
    csv_data = csv.DictReader(open("resistance_data/sources/farhat_lab_pools_cetr_tdr/resistance_data_farhat_lab_pools_cetr_tdr.tsv","r"),delimiter="\t")
    outf.write("\t".join(details["fields"]) + "\n")
    for row in csv_data:
        for antb_abbrev in details["antb"]:
        #entry: "xref", "antb", "mic_summary", "conc_units", "tag"
            entry={}
            entry["method"]="NA"
            entry["media"]="NA"
            entry["xref"]=row["Id_rollingDB"]
            # I define the antibiotic
            entry["antb"]=details["abbrev_antb"][antb_abbrev]
            # I define the value of the MIC
            value_mic=row[antb_abbrev]
            if value_mic=="NA":
                continue
            ## some strains they are classified as "r" or "s"
            elif value_mic in ["r","s"]:
                entry["mic_summary"]="NA"
                entry["conc_units"]="NA"
                entry["res_class"]=value_mic.upper()
            else:
                entry["mic_summary"]=value_mic
                entry["conc_units"]="μg/ml"
                entry["res_class"]="NA"
            # I define the tag
            if(row["Source Lab"]=="MSLI"):
                tag="FARHAT_LAB:pools"
                if entry["antb"] in ["ISONIAZID","RIFAMPICIN","ETHAMBUTOL","STREPTOMYCIN","KANAMYCIN","CAPREOMYCIN","ETHIONAMIDE","CYCLOSERINE","PARA_AMINOSALICYLIC_ACID","AMIKACIN","LEVOFLOXACIN","OFLOXACIN","CIPROFLOXACIN"]:
                    entry["method"]="indirect proportion method"
                    entry["media"]="Middlebrook 7H10"
                elif entry["antb"]=="PYRAZINAMIDE":
                    entry["method"]="BACTEC MGIT"
            elif (row["Source Lab"]=="RIVM"):
                tag="FARHAT_LAB:pools"
                entry["method"]="BACTEC MGIT"
            # SES = Socios en Salud
            elif(row["Source Lab"]=="SES"):
                tag="FARHAT_LAB:cetr"
                if entry["antb"]=="PYRAZINAMIDE":
                    entry["method"]="BACTEC MGIT"
                else:
                    entry["media"]="Middlebrook 7H10"
            else:
                if entry["antb"] in ["ISONIAZID","RIFAMPICIN","ETHAMBUTOL","STREPTOMYCIN","PARA_AMINOSALICYLIC_ACID"]:
                    entry["media"]="Löwenstein-Jensen"
                elif entry["antb"] in ["OFLOXACIN","KANAMYCIN","CAPREOMYCIN"]:
                    entry["media"]="Middlebrook 7H11"
                entry["method"]="indirect proportion method"
                tag="FARHAT_LAB:tdr"
            entry["tag"]=tag
            outf.write("\t".join([entry["xref"], entry["antb"], entry["mic_summary"], 
entry["conc_units"], entry["res_class"], entry["method"], entry["media"], entry["tag"]]) + "\n")


# I load the critical concentrations data
thresholds=get_who_thresholds("who_critical_concentrations/critical_concentrations.csv")

# I define the media conversions
media_conv={"Middlebrook 7H10":"m7h10","Middlebrook 7H11":"m7h11","Löwenstein-Jensen":"lj"}
method_conv={"BACTEC MGIT":"mgit960"}

# Here I will store the list of the discarded entries
list_discarded=[]

#counters
count_all_entries=0
count_discarded=0

# regular expressions to interpret the MIC data
reasons_discarded={"no_media_method":0,"conc_tested_not_allows_decision":0,"new_regex_needed":0}
interm=re.compile("([0-9].*[0-9]*)-([0-9].*[0-9]*)")
great_eq_than=re.compile(">=([0-9]+.*[0-9]*)")
great_than=re.compile(">([0-9]+.*[0-9]*)")
less_than=re.compile("<=*([0-9]+.*[0-9]*)")
numb=re.compile("(^[0-9]$)")

with open("resistance_data/summary_tables/farhat_lab_pools_cetr_tdr.res","w") as outf:
    mic_data = csv.DictReader(open("resistance_data/summary_tables/farhat_lab_pools_cetr_tdr.mic","r"),delimiter="\t")
    for row in mic_data:
        count_all_entries+=1
        if row["res_class"] in ["R","S"]:
            outf.write("{}\t{}\t{}\t{}\n".format(row["xref"],row["antb"],row["res_class"],row["tag"]))
        else:
            res_interm=re.findall(interm,row["mic_summary"])
            res_great_eq_than=re.findall(great_eq_than,row["mic_summary"])
            res_great_than=re.findall(great_than,row["mic_summary"])
            res_less_than=re.findall(less_than,row["mic_summary"])
            res_numb=re.findall(numb,row["mic_summary"])
            if res_interm:

                inf_lim=float((res_interm[0][0]))
                sup_lim=float((res_interm[0][1]))
                if row["media"] in media_conv:
                    medium=media_conv[row["media"]]
                elif row["method"] in method_conv:
                    medium=method_conv[row["method"]]
                else:
                    count_discarded+=1
                    list_discarded.append(row)
                    reasons_discarded["no_media_method"]+=1
                    continue
                who_threshold=thresholds[row["antb"]][medium]
                if inf_lim >= who_threshold:
                    outf.write("{}\t{}\t{}\t{}\n".format(row["xref"],row["antb"],"R",row["tag"]))
                elif sup_lim <= who_threshold:
                    outf.write("{}\t{}\t{}\t{}\n".format(row["xref"],row["antb"],"S",row["tag"]))
                else:
                    count_discarded+=1
                    list_discarded.append(row)
                    reasons_discarded["conc_tested_not_allows_decision"]+=1
                    #print(row)
            elif res_great_eq_than:

                lim=float((res_great_eq_than[0]))
                if row["media"] in media_conv:
                    medium=media_conv[row["media"]]
                elif row["method"] in method_conv:
                    medium=method_conv[row["method"]]
                else:
                    count_discarded+=1
                    list_discarded.append(row)
                    reasons_discarded["no_media_method"]+=1
                    continue
                who_threshold=thresholds[row["antb"]][medium]
                if lim > who_threshold:
                    outf.write("{}\t{}\t{}\t{}\n".format(row["xref"],row["antb"],"R",row["tag"]))
                else:
                    count_discarded+=1
                    list_discarded.append(row)
                    reasons_discarded["conc_tested_not_allows_decision"]+=1
                    #print(row)
            elif res_great_than:

                lim=float((res_great_than[0]))
                if row["media"] in media_conv:
                    medium=media_conv[row["media"]]
                elif row["method"] in method_conv:
                    medium=method_conv[row["method"]]
                else:
                    count_discarded+=1
                    list_discarded.append(row)
                    reasons_discarded["no_media_method"]+=1
                    continue
                who_threshold=thresholds[row["antb"]][medium]
                if lim >= who_threshold:
                    outf.write("{}\t{}\t{}\t{}\n".format(row["xref"],row["antb"],"R",row["tag"]))
                else:
                    count_discarded+=1
                    list_discarded.append(row)
                    reasons_discarded["conc_tested_not_allows_decision"]+=1
                    #print(row)
            elif res_less_than:

                lim=float((res_less_than[0]))
                if row["media"] in media_conv:
                    medium=media_conv[row["media"]]
                elif row["method"] in method_conv:
                    medium=method_conv[row["method"]]
                else:
                    count_discarded+=1
                    list_discarded.append(row)
                    reasons_discarded["no_media_method"]+=1
                    continue
                who_threshold=thresholds[row["antb"]][medium]
                if lim <= who_threshold:
                    outf.write("{}\t{}\t{}\t{}\n".format(row["xref"],row["antb"],"S",row["tag"]))
                else:
                    count_discarded+=1
                    list_discarded.append(row)
                    reasons_discarded["conc_tested_not_allows_decision"]+=1
                    #print(row)
            elif res_numb:

                lim=float((res_numb[0]))
                if row["media"] in media_conv:
                    medium=media_conv[row["media"]]
                elif row["method"] in method_conv:
                    medium=method_conv[row["method"]]
                else:
                    count_discarded+=1
                    list_discarded.append(row)
                    reasons_discarded["no_media_method"]+=1
                    continue
                who_threshold=thresholds[row["antb"]][medium]
                if lim > who_threshold:
                    outf.write("{}\t{}\t{}\t{}\n".format(row["xref"],row["antb"],"R",row["tag"]))
                elif lim <= who_threshold:
                    outf.write("{}\t{}\t{}\t{}\n".format(row["xref"],row["antb"],"S",row["tag"]))
                else:
                    count_discarded+=1
                    list_discarded.append(row)
                    reasons_discarded["conc_tested_not_allows_decision"]+=1
                    #print(row)
            else:
                reasons_discarded["new_regex_needed"]+=1
                list_discarded.append(row)
                print("unknown regex: {} // {} {} {} {}".format(row["mic_summary"],row["xref"],row["antb"],row["res_class"],row["tag"]))
print("[INFO] Total number of entries: {}".format(count_all_entries))
print("[INFO] {} entries were discarded ({:.1f}%)".format(count_discarded,count_discarded/count_all_entries*100))
for reason in reasons_discarded:
    print("* {}: {}".format(reason,reasons_discarded[reason]))

