import csv



with open("nodetable.csv","r") as csvfile:
    reader = csv.reader(csvfile)
    symp = []
    dise = []
    for row in reader:
        if row[2] == 'symptom':
            symp.append(row[1])
        if row[2] == 'disease':
            dise.append(row[1])


# with open("allsymptoms.txt", 'wb') as f3:
# 	for symptom in data:
# 		symptom = symptom.strip()
# 		f3.write(symptom + "\n")



with open("symptomsEntity.txt", 'wb') as f2:
	for symptom in symp:
		symptom = symptom.strip()
		f2.write('"' + symptom + '"' + ',' + '"' + symptom + '"' + "\n")