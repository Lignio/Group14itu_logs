from typing import Union
from fastapi import FastAPI
import requests
import json



#app = FastAPI()


def getAnomalyList(threshold : float = 0.02):
    myResult = []
    request = requests.get("http://localhost:8000/logs/LogList")
    dataList = request.json()
    for i in dataList:
         response = requests.get('http://localhost:8001/logs/getPredict/', params = {"log_message":i[0], "threshold":threshold} )
         answer = response.json()
         anomalyScore = answer["anomaly_score"]
         if anomalyScore > threshold:
            myResult.append((i[0], anomalyScore, True))
    print(myResult[0])

def testList():
    myL = requests.get("http://localhost:8000/logs/LogList")
    gooddata = myL.json()
    #test = gooddata[0].split(", ")
    print(type(gooddata[0]))
    #print(test[0])

def testGetHealth():
    val = requests.get('http://localhost:8000/health')
    print(val.text)

#testList()
getAnomalyList()
#testGetHealth()   

