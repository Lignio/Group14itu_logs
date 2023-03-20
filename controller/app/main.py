from typing import Union
from fastapi import FastAPI
import requests
import json
import threading

app = FastAPI()


# Function that calls the data-generator api for a list of the first 1000 logs and then calls the anomaly-detector api
# to check which of those logs are a anomaly. It then returns a list of all anomalies and there anomaly-score.
@app.get("/getAnomalyList")
def getAnomalyList(threshold: float = 0.02):
    myResult = []
    # Retrives the list from the datagenerator
    request = requests.get("http://localhost:8000/logs/LogList")
    # Deserialize it from json
    dataList = request.json()
    for i in dataList:
        response = requests.get(
            "http://localhost:8001/logs/getPredict/",
            params={"log_message": i[0], "threshold": threshold},
        )
        answer = response.json()
        anomalyScore = answer["anomaly_score"]
        if anomalyScore > threshold:
            myResult.append((i[0], anomalyScore))
    return myResult


def simulateLogsteam():
    #Runs the method after amount of time, currently 0.08 second
    t = threading.Timer(0.08, simulateLogsteam)
    t.daemon = True
    t.start()
    myLogmessage = requests.get("http://localhost:8000/logs/get_record")
    analysedMessage = requests.get('http://localhost:8001/logs/getPredict', params={"log_message":myLogmessage,"threshold":0.02 })
    analysedMessage = analysedMessage.json()
    if analysedMessage["anomaly_score"] > 0.02:
        # Replace print with insertion into database
        print(analysedMessage["log_message"])

simulateLogsteam()


@app.get("/getNumOfThreads")
def getNumOfThreads():
    return threading.active_count()
