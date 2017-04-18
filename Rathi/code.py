import csv
from collections import defaultdict

with open("nodetable.csv","r") as csvfile:
	reader = csv.reader(csvfile)
	symp = []
	dise = []
	for row in reader:
		if row[2] == 'symptom':
			symp.append(row[1])
		if row[2] == 'disease':
			dise.append(row[1])

with open("dataset_clean1.csv","r") as csvfile, open("dataset1.csv","w") as csvfile2:
	reader = csv.reader(csvfile)
	writer = csv.writer(csvfile2)
	header = []
	for i in range(2+len(symp)):
		header.append(i)
	# header = list(len(symp)+2)
	# header.append("weight")
	# header.append("disease")
	writer.writerow(header)
	nsymp=len(symp)
	ndise=len(dise)
	inputl = [[0 for col in range(nsymp+2)] for row in range(ndise)]
	for dis in range(ndise):
		inputl[dis][nsymp+1]=dise[dis]
	for row in reader:
		if row[0] in dise:
			x = dise.index(row[0])
			y = symp.index(row[1])
			inputl[x][y]=1
			inputl[x][nsymp]=row[2]
	writer.writerows(inputl)
