import csv
from collections import defaultdict
#import pandas as pd
#import seaborn as sns
#import matplotlib.pyplot as plt
#matplotlib inline
#from sklearn.naive_bayes import MultinomialNB
#from sklearn.cross_validation import train_test_split
import numpy as np
#from numpy import genfromtxt, savetxt
from globalData import *

# with open("nodetable.csv","r") as csvfile:
#     reader = csv.reader(csvfile)
#     symp = []
#     dise = []
#     for row in reader:
#         if row[2] == 'symptom':
#             symp.append(row[1])
#         if row[2] == 'disease':
#             dise.append(row[1])


#data = pd.read_csv('data_pivoted.csv')
#print data.shape
#data = data.fillna(0)
#data.head(5)
#print data.info()
#cols = data.columns.tolist()
#cols.remove('disease')
# dataset = genfromtxt(open('dataset1.csv','r'), delimiter=',', dtype='f8')[1:]   
# target = [int(x[407])-1 for x in dataset]
# train = [x[0:405] for x in dataset]
# x = train
# y = target
# #print x
# #print y
# #print dataset[0]

# #z = raw_input()

# #x = data[cols]
# #print type(x)
# #y = data.disease
# #x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)

# mnb_tot = MultinomialNB()
# mnb_tot = mnb_tot.fit(x, y)

# disease_pred = mnb_tot.predict(x)
# disease_pred_probab = mnb_tot.predict_proba(x)
# a = np.argsort(disease_pred_probab[0])
# #print a
# print dise[a[len(a)-1]]
# print disease_pred_probab[0]
# #print np.sort(disease_pred_probab[0])
# print dise[disease_pred[0]]



def predict_disease(symptoms):
    #print "dsf"
    print "Inside predict disease naivebayes file"
    nsymp = len(symp)
    check = [0 for col in range(nsymp)]
    #print symp
    for i in symptoms:
        check[symp.index(i)] = 1

    print "Classifier before"
    disease_pred_probab = mnb_classifier.predict_proba(check)[0]
    print "classified: disease: " , disease_pred_probab
    sorted_probabs_indexes = np.argsort(disease_pred_probab)
    disease_top_3 = []
    disease_top_3.append([dise[sorted_probabs_indexes[len(sorted_probabs_indexes)-1]],disease_pred_probab[sorted_probabs_indexes[len(sorted_probabs_indexes)-1]]])
    disease_top_3.append([dise[sorted_probabs_indexes[len(sorted_probabs_indexes)-2]],disease_pred_probab[sorted_probabs_indexes[len(sorted_probabs_indexes)-2]]])
    disease_top_3.append([dise[sorted_probabs_indexes[len(sorted_probabs_indexes)-3]],disease_pred_probab[sorted_probabs_indexes[len(sorted_probabs_indexes)-3]]])
    return disease_top_3











