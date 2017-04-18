import csv
from collections import defaultdict
from sklearn.ensemble import RandomForestClassifier
from numpy import genfromtxt, savetxt
import numpy as np

with open("nodetable.csv","r") as csvfile:
    reader = csv.reader(csvfile)
    symp = []
    dise = []
    for row in reader:
        if row[2] == 'symptom':
            symp.append(row[1])
        if row[2] == 'disease':
            dise.append(row[1])

def predictDisease(symptoms):
    #create the training & test sets, skipping the header row with [1:]
    dataset = genfromtxt(open('dataset1.csv','r'), delimiter=',', dtype='f8')[1:]   
    target = [x[407] for x in dataset]
    train = [x[0:405] for x in dataset]

    #print target[:5]
    #print train[:5]
    # test = genfromtxt(open('test.csv','r'), delimiter=',', dtype='f8')[1:]
    
    #create and train the random forest
    #multi-core CPUs can use: rf = RandomForestClassifier(n_estimators=100, n_jobs=2)
    rf = RandomForestClassifier(n_estimators=1000)
    rf.fit(train, target)


    nsymp = len(symp)            
    check = [0 for col in range(nsymp)]
    for i in range(len(train[0])):
        if(train[0][i] == 1):
            check[i] = 1

    #symptoms = ['fever','snuffle','throat sore','malaise' ]

    #for i in symptoms:
    #    check[symp.index(i)] = 1
    #for i in range(3):
    #    check[i] = 1
    savetxt('submission2.csv', rf.predict_proba([check]), delimiter=',', fmt='%f')
    #print rf.predict_proba([check]),type(rf.predict_proba([check]))
    #a = rf.predict_proba([]
    a = np.argsort(rf.predict_proba([check])[0])
    print a
    print dise[a[len(a)-1]]
    print np.sort(rf.predict_proba([check]))
    #print 
    #print r
    
    # savetxt('submission2.csv', rf.predict_proba(test), delimiter=',', fmt='%f')

predictDisease(['fever','snuffle','throat sore','malaise' ])