from typing import Union
from fastapi import FastAPI
import requests
import json
import threading
import queue

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

# Queue with our log messages
logQueue = queue.Queue(1000)

# Method for simlating getting constant steam of mesagges and inserting them into the queue
def simulateLogsteam():
    while True:
        # Missing load balancing when queue is full
        myLogmessage = requests.get("http://localhost:8000/logs/get_record").json()
        logQueue.put(myLogmessage) # Put blocks/waits when the queue is full
    



# Method for analysing and handeling log messages in the queue.
def simulateStreamAnalysis():
    while True:
        while logQueue.not_empty:
            analysedMessage = requests.get('http://localhost:8001/logs/getPredict', params={"log_message":logQueue.get(),"threshold":0.02 })
            analysedMessage = analysedMessage.json()
            if analysedMessage["anomaly_score"] > 0.02:
                # Replace print with insertion into database
                print(analysedMessage["log_message"])



t = threading.Thread(target=simulateLogsteam)
t.daemon = True
t.start()
t2 = threading.Thread(target=simulateStreamAnalysis)
t2.daemon = True
t2.start()
