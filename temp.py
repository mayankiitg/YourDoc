

f = open("symptoms.txt", 'rb')
data = f.read()

data = data.split(",")

with open("allsymptoms.txt", 'wb') as f3:
	for symptom in data:
		symptom = symptom.strip()
		f3.write(symptom + "\n")

with open("symptomsEntity.txt", 'wb') as f2:
	for symptom in data:
		symptom = symptom.strip()
		f2.write('"' + symptom + '"' + ',' + '"' + symptom + '"' + "\n")