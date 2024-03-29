
import re
import requests
from progress.bar import IncrementalBar

#test=["SRS2774703","PRJNA413593","SRR6397334"]

def get_ncbi_id_type(my_id: str):
	#bioproject
	re_bp=re.compile("^PRJ")
	if(re_bp.match(my_id)):
		return "bioproject"
	#biosample
	re_bs=re.compile("^SAM")
	if(re_bs.match(my_id)):
		return "biosample"
	#run
	re_r=re.compile("^ERR")
	re_r2=re.compile("^SRR")
	re_r3=re.compile("^SRS")
	if(re_r.match(my_id) or re_r.match(my_id)):
		return "sra"
	return "unknown"

def parse_response(ncbi_id, response) -> str:
	biosample=""
	biosamples_found=[]
	lines=response.split("\n")
	header=lines.pop(0)
	idx_biosample=header.split(",").index("BioSample")
	for line in lines:
		if line == "":
			continue
		biosamples_found.append(line.split(",")[idx_biosample])
	n_biosamples_found=len(set(biosamples_found))
	if n_biosamples_found == 1 :
		biosample=set(biosamples_found).pop()
	return(biosample)

def convert_to_biosample(list_ncbi_ids: list) -> list:
	ncbi_ids_with_issues=[]
	with IncrementalBar("Converting...".format(value), max=len(list_ncbi_ids), suffix='%(percent).1f%%') as bar:
		list_of_biosamples=[]
		for ncbi_id in list_ncbi_ids:
			if ncbi_id == "":
				list_of_biosamples.append("")
			else:
				db=get_ncbi_id_type(ncbi_id)
				if db == "biosample":
					list_of_biosamples.append(ncbi_id)
				else:
					request = "http://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?save=efetch&db={}&rettype=runinfo&term={}".format(db, ncbi_id)
					response = requests.get(url=request,stream=True,timeout=60)
					response.encoding = 'utf-8'
					try:
						biosample=parse_response(ncbi_id, response.text)
					except:
						biosample=""
						ncbi_ids_with_issues.append(ncbi_id)
					list_of_biosamples.append(biosample)
			bar.next()
		print("* I found {} issues in converting the IDs you provided".format(len(ncbi_ids_with_issues)))
		if len(ncbi_ids_with_issues)!=0:
			print("* Here are the problematic IDs:")
			print(",".join(ncbi_ids_with_issues))
		return(list_of_biosamples)

def convert_to_biosample_simplified(list_ncbi_ids: list) -> list:
	ncbi_ids_with_issues=[]
	list_of_biosamples=[]
	counter=0
	for ncbi_id in list_ncbi_ids:
		counter = counter + 1
		print("* analysing {} ({} of {})".format(ncbi_id, counter, len(list_ncbi_ids)))
		if ncbi_id == "":
			list_of_biosamples.append("")
		else:
			db=get_ncbi_id_type(ncbi_id)
			if db == "biosample":
				list_of_biosamples.append(ncbi_id)
			else:
				request = "http://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?save=efetch&db={}&rettype=runinfo&term={}".format(db, ncbi_id)
				response = requests.get(url=request,stream=True,timeout=60)
				response.encoding = 'utf-8'
				try:
					biosample=parse_response(ncbi_id, response.text)
				except:
					biosample=""
					ncbi_ids_with_issues.append(ncbi_id)
				list_of_biosamples.append(biosample)
	print("* I found {} issues in converting the IDs you provided".format(len(ncbi_ids_with_issues)))
	if len(ncbi_ids_with_issues)!=0:
		print("* Here are the problematic IDs:")
		print(",".join(ncbi_ids_with_issues))
	return(list_of_biosamples)


def write_tsv(list_ncbi_ids, list_of_biosamples, file_out):
	with open(file_out,"w") as outf:
		for i, ncbi_id in enumerate(list_ncbi_ids):
			outf.write("{}\t{}\n".format(ncbi_id,list_of_biosamples[i]))

