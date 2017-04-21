#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import csv

import json
import os,re
import numpy as np
import NaiveBayes
from flask import Flask
from flask import request
from flask import make_response
#import global variables
from globalData import *

from numpy import genfromtxt, savetxt
# Flask app should start in global layout
app = Flask(__name__)

#Global Variables
UserSymptomsData = dict()   #Stores user symptoms. Key: sessionId, Data: List of Symptoms
# SymptomList = []            #List of all symptoms



@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    print("Result: ")
    print(res)
    r = make_response(res)
    # r = make_response("Hello")
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    print("Processing Request: sessionId" + req.get("sessionId"))
    try:    
        if req.get("result").get("action") == "add_symptom":
            print("Action: add_symptom")
            symptoms = retrieveSymptom(req)
            symptoms = [symptom.lower() for symptom in symptoms]
            symptoms = list(set(symptoms))
            print("Symptoms detected" + " ".join(symptoms))
            print("Len of symptom: ", len(symptoms))
            if len(symptoms) == 0:
                print("No Symptom Found")
                outStr = "Couldn't Understand the symptom. Kindly rephrase ur query."
            else:
                print("Symptoms Found")
                addSymptomInList(req, symptoms)
                outStr =  "Apart from " + ", ".join(UserSymptomsData[req.get("sessionId")]) + " do you have any other symptom?"

        elif req.get("result").get("action") == "predict_disease":
            print("Action: predict_disease")
            outStr = predictDisease(req)
            outStr += "\n Do you also have any of these symptoms."
            sessionId = req.get("sessionId")
            relatedSymptoms = getRelatedSymptoms(UserSymptomsData[sessionId], 4)
            return makeWebhookResultForNextSymptom(outStr, relatedSymptoms)

        elif req.get("result").get("action") == "get_user_location":
            print("Action: get_user_location")
            outStr = "To know nearby hospitals, please provide your location by clicking below."
            return makeWebhookResultAskLocation(outStr)

        elif req.get("result").get("action") == "predict_hospital":
            latitude = req.get("result").get("contexts")[0].get("parameters").get("lat")
            longitude = req.get("result").get("contexts")[0].get("parameters").get("long")
            print(latitude, longitude)
            outStr = "To see nearby hospitals visit :\n" + "https://www.google.com/maps/search/hospitals/@" + str(latitude) + "," + str(longitude) + ",13z"

        elif req.get("result").get("action") == "flush_session":
            print("Good Bye message")
            sessionId = req.get("sessionId")                #String
            if sessionId in UserSymptomsData:
                print("session data deleted..")
                UserSymptomsData.pop(sessionId, None)
            outStr = "Goodbye. Happy to help :)"
        
        else:
            print("No action Detected")
            return {}
        
        res = makeWebhookResult(outStr)
        return res
    except:
        print("Error in Process Request. + ")
        return {}

def retrieveSymptom(req):
    ans = []
    print("Inside retrieveSymptom")
    try:
        sent = req.get("result").get("resolvedQuery").lower()
        for symptom in symp:
            if len(symptom.strip()) == 0:
                continue
            # delimiters = " ", "-"
            # regexPattern = '|'.join(map(re.escape, delimiters))
            # words = re.split(regexPattern, symptom)
            words = symptom.strip().lower().split(" ")
            check = True
            for word in words:
                if word not in sent:
                    check = False
                    break
            if check == True:
                if symptom not in ans:
                    ans.append(symptom)
                    print("Found symptom: '" + symptom + "' in sent" + sent)
        symptoms2 = req.get('result').get('parameters').get("Symptoms")
        for s in symptoms2:
            s= s.lower()
            if s not in ans:
                ans.append(s)
    except:
        print("Error:" )
    return ans

def addSymptomInList(req, symptoms):
    try:
        # symptoms = req.get("result").get("parameters").get("Symptoms")    #List of string
        sessionId = req.get("sessionId")                #String
        if sessionId in UserSymptomsData:
            for symptom in symptoms:
                if symptom not in UserSymptomsData[sessionId]:
                    UserSymptomsData[sessionId].append(symptom)
        else:
            UserSymptomsData[sessionId] = symptoms
        print("Added following symptom: in session " + str(sessionId) + " ".join(symptoms))
    except:
        print("Error in Process Request. + " )

def predictDisease(req):
    print("In predict disease")
    sessionId = req.get("sessionId")                #String
    #return "Symptoms are " + (", ".join(UserSymptomsData[sessionId]))
    try:
        disease_predict = NaiveBayes.predict_disease(UserSymptomsData[sessionId])
    except:
        print("Error in predict disease")
    print ("Disease predicted is:" + disease_predict[0][0])
    reply = "The top 3 predicted diseases for you along with confidence:\n"
    reply = reply + "1 " + disease_predict[0][0] + " : " + "{:2.3f}".format(disease_predict[0][1]*100) + "%\n"
    reply = reply + "2 " + disease_predict[1][0] + " : " + "{:2.3f}".format(disease_predict[1][1]*100) + "%\n"
    reply = reply + "3 " + disease_predict[2][0] + " : " + "{:2.3f}".format(disease_predict[2][1]*100) + "%\n"
    return reply

def makeWebhookResult(outStr):
    print("Response:")
    print(outStr)

    return {
        "speech": outStr,
        "displayText": outStr,

        "data": {},
        # "contextOut": [],
        "source": "yourdoc"  
    }


def makeWebhookResultAskLocation(outStr):
    print("Response:")
    print(outStr)

    return {
        "speech": outStr,
        "displayText": outStr,
        "data": {"facebook": {
        "text":outStr,
         "quick_replies":[
        {
            "content_type":"location",
        }
        ]
        }

        },
        # "contextOut": [],
        "source": "yourdoc"  
    }
#Input: list of strings: each string is a symptom.
#Output: Most probable next symptom. 
def getRelatedSymptoms(symptoms, count):
    l = [symp.index(symptom) for symptom in symptoms]
    Scores = cooccurMat[l[0]]
    for i in range(1, len(symptoms)):
        Scores = Scores * cooccurMat[l[i]]
    for i in range(0, len(l)):
        Scores[l[i]] = 0
    sortedInd = np.argsort(Scores)
    n = len(Scores)
    sortedInd[n-1]
    return [symp[sortedInd[n-i]] for i in range(1,count+1)]

def makeWebhookResultForNextSymptom(outStr,symptomList):
    print("Response:")
    print(outStr)

    return {
        "speech": outStr,
        "displayText": outStr,
         "data": {"facebook": 
            {
                "text":outStr,
                "quick_replies":[
                {
                    "content_type":"text",
                    "title":symptomList[0],
                    "payload":"I have " + symptomList[0],
                    #"image_url":"http://petersfantastichats.com/img/red.png"
                },
                {
                    "content_type":"text",
                    "title":symptomList[1],
                    "payload":"I have " + symptomList[1],
                    #"image_url":"http://petersfantastichats.com/img/red.png"
                },
                {
                    "content_type":"text",
                    "title":symptomList[2],
                    "payload":"I have " +symptomList[2],
                    #"image_url":"http://petersfantastichats.com/img/red.png"
                },
                {
                    "content_type":"text",
                    "title":symptomList[3],
                    "payload":"I have " +symptomList[3],
                    #"image_url":"http://petersfantastichats.com/img/red.png"
                },
                ]
            }

        },
        # "contextOut": [],
        "source": "yourdoc"
        
    }

if __name__ == '__main__':
    dataset = genfromtxt(open('dataset1.csv','r'), delimiter=',', dtype='f8')[1:]   
    target = [int(x[407])-1 for x in dataset]
    train = [x[0:405] for x in dataset]
    mnb_classifier = mnb_classifier.fit(train,target)

    with open("nodetable.csv","r") as csvfile:
        reader = csv.reader(csvfile)
        #symp = []
        #dise = []
        for row in reader:
            if row[2] == 'symptom':
                symp.append(row[1])
            if row[2] == 'disease':
                dise.append(row[1])
    print("Loaded all symptoms, Length:", len(symp))
    print("Building Co-occurence Matrix")
    nsymp = len(symp)
    
    cooccurMat = np.zeros((nsymp, nsymp), dtype=np.int)
    for x in dataset:
        for i in range(0, 404):
            for j in range(i+1, 405):
                if int(x[i]) == 1 and int(x[j]) == 1:
                    # if i == 1 and j == 2:
                    #     print(dise[int(x[407])-1])
                    #     print(int(x[405]))
                    cooccurMat[i][j] += int(x[405])
                    cooccurMat[j][i] += int(x[405])
    symptoms_1stDis = [symp[i] for i in range(405) if int(dataset[0][i]) == 1]
    # print("1st disease symptoms: disease: ", dise[0], symptoms_1stDis)
    # print([symp[i] for i in range(10)])
    # print(cooccurMat[:10, :10])
    # print("Related syptom to first 5 syptom of 1st dis", getRelatedSymptoms(symptoms_1stDis[:5], 5))
    # print("cooccurMat for first symptom\n", cooccurMat[0])

    #with open("allsymptoms.txt", 'rb') as f:
    #SymptomList = f.read().split("\n")
    #disease_predict = NaiveBayes.predict_disease(['fever','snuffle','throat sore','malaise' ])
    #print(disease_predict)

    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
