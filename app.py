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
            print("Symptoms detected" + " ".join(symptoms))
            if len(symptoms) == 0:
                print("No Symptom Found")
                outStr = "Couldn't Understand the symptom. Kindly rephrase ur query."
            else:
                print("Symptoms Found")
                addSymptomInList(req, symptoms)
                outStr = "Do You have any other symptom" + " ".join(UserSymptomsData[req.get("sessionId")]) + " id: " + req.get("sessionId")

        elif req.get("result").get("action") == "predict_disease":
            print("Action: predict_disease")
            outStr = predictDisease(req)

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
            # delimiters = " ", "-"
            # regexPattern = '|'.join(map(re.escape, delimiters))
            # words = re.split(regexPattern, symptom)
            words = symptom.split(" ")
            check = True
            for word in words:
                if word not in sent:
                    check = False
                    break
            if check == True:
                ans.append(symptom)
    except:
        print("Error:" )
    return ans

def addSymptomInList(req, symptoms):
    try:
        # symptoms = req.get("result").get("parameters").get("Symptoms")    #List of string
        sessionId = req.get("sessionId")                #String
        if sessionId in UserSymptomsData:
            UserSymptomsData[sessionId] += symptoms
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
    reply = "The top 3 predicted diseases for you along with probab:\n"
    reply = reply + "disease: " + disease_predict[0][0] + " with probab: " + str(disease_predict[0][1]) + "\n"
    reply = reply + "disease: " + disease_predict[1][0] + " with probab: " + str(disease_predict[1][1]) + "\n"
    reply = reply + "disease: " + disease_predict[2][0] + " with probab: " + str(disease_predict[2][1]) + "\n"
    return reply

def makeWebhookResult(outStr):
    print("Response:")
    print(outStr)

    return {
        "speech": outStr,
        "displayText": outStr,
        # "data": "data",
        # "contextOut": [],
        "source": "yourdoc"
        
    }

def makeWebhookResultForNextSymptom(outStr,symptomList):
    print("Response:")
    print(outStr)

    return {
        "speech": outStr,
        "displayText": outStr,
         "data": {"facebook": 
            {
                "text":"Pick a color:",
                "quick_replies":[
                {
                    "content_type":"text",
                    "title":symptomList[0],
                    "payload":symptomList[0],
                    #"image_url":"http://petersfantastichats.com/img/red.png"
                },
                {
                    "content_type":"text",
                    "title":symptomList[1],
                    "payload":symptomList[1],
                    #"image_url":"http://petersfantastichats.com/img/red.png"
                },
                {
                    "content_type":"text",
                    "title":symptomList[2],
                    "payload":symptomList[2],
                    #"image_url":"http://petersfantastichats.com/img/red.png"
                },
                {
                    "content_type":"text",
                    "title":symptomList[3],
                    "payload":symptomList[3],
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
    port = int(os.getenv('PORT', 5000))


    print("Starting app on port %d" % port)
    with open("nodetable.csv","r") as csvfile:
        reader = csv.reader(csvfile)
        #symp = []
        #dise = []
        for row in reader:
            if row[2] == 'symptom':
                symp.append(row[1])
            if row[2] == 'disease':
                dise.append(row[1])

    #with open("allsymptoms.txt", 'rb') as f:
    #SymptomList = f.read().split("\n")
    print("Loaded all symptoms, Length: %d", len(symp))
    #disease_predict = NaiveBayes.predict_disease(['fever','snuffle','throat sore','malaise' ])
    #print(disease_predict)
    app.run(debug=False, port=port, host='0.0.0.0')


