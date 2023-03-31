from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json
import threading
import queue

from datetime import datetime

from controller.database.data_loader import DataLoader
from controller.database.datawriter import DataWriter
from controller.database.tables import Anomalies


app = FastAPI()
data_loader = DataLoader()
data_writer = DataWriter()


class Anomaly(BaseModel):
    log_time: str
    log_message: str
    anomaly_score: float 

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
    



#Method for analysing and handeling log messages in the queue.
def simulateStreamAnalysis():
    while True:
        while logQueue.not_empty:
            analysedMessage = requests.get('http://localhost:8001/logs/getPredict', params={"log_message":logQueue.get(),"threshold":0.02 })
            analysedMessage = analysedMessage.json()
            if analysedMessage["anomaly_score"] > 0.02:
                #Replace print with insertion into database
                print(analysedMessage["log_message"])
        return Anomaly(log_time="10", log_message=analysedMessage["log_message"], anomaly_score=analysedMessage["anomaly_score"])



#Function to post an anomaly into db, by getting anomaly from stream and sending the parameters to data_generator, which handles the final insertion into Anomaly db table
#Jakob : this function is now outdated - the real endpoint that handles insertion into db is "/anomalies/post_anomaly"
#Jakob : I kept this endpoint in case it is used by other
@app.post("/postAnomaly_outdated")
def postAnomaly():
    while True:
        while logQueue.not_empty:
            myLogmessage = requests.get("http://localhost:8000/logs/get_record")
            analysedMessage = requests.get('http://localhost:8001/logs/getPredict', params={"log_message":myLogmessage,"threshold":0.02 })
            analysedMessage = analysedMessage.json()
            if analysedMessage["anomaly_score"] > 0.02:
              # Replace print with insertion into database
                #requests.post('http://localhost:8000/anomalies/post_anomaly', params={"log_message":analysedMessage["log_message"], "anomaly_score":analysedMessage["anomaly_score"] })
                print(analysedMessage["log_message"])
            return Anomaly(log_time="10", log_message=analysedMessage["log_message"], anomaly_score=analysedMessage["anomaly_score"])



#----------------------------------------------------------------------------------------------
@app.get("/anomalies/get_anomaly_list")
def get_anomaly_list():

    return data_loader.get_all_anomalies()


#Endpoint for forcing a custom anomaly into the db - for testing purposes
#Note: this does not account for the anomaly threshold - this is purely for inserting ANYTHING into the database for testing
@app.post("/anomalies/post_test_anomaly",response_model=Anomaly)
def post_test_anomaly(log_message:str, anomaly_score:float):

    dt = datetime.now()
    dts = dt.strftime('%d/%m/%Y')

    anomaly = Anomaly(log_time=dts,log_message=log_message, anomaly_score=anomaly_score)
    new_post = Anomalies(**anomaly.dict())
    data_writer.write_single_row_to_database(new_post)
    return anomaly

#Endpoint for getting a log from the datagenerator, and the inserting into the db if it is an anomaly
@app.post("/anomalies/post_anomaly",response_model=Anomaly)
def post_anomaly():
    myLogmessage = requests.get("http://data_generator:8000/logs/get_record")
    analysedMessage = requests.get('http://anomaly_detector:8001/logs/getPredict', params={"log_message":myLogmessage,"threshold":0.02 })
    analysedMessage = analysedMessage.json()

    dt = datetime.now()
    dts = dt.strftime('%d/%m/%Y')
    

    anomaly = Anomaly(log_time=dts, log_message=analysedMessage["log_message"], anomaly_score=analysedMessage["anomaly_score"])
    if analysedMessage["anomaly_score"] > 0.02:
        #anomaly = Anomaly(log_time=analysedMessage["log_time"], log_message=analysedMessage["log_message"], anomaly_score=analysedMessage["anomaly_score"])
        new_post = Anomalies(**anomaly.dict())
        data_writer.write_single_row_to_database(new_post)
    return anomaly





#t = threading.Thread(target=simulateLogsteam)
#t.daemon = True
#t.start()
#t2 = threading.Thread(target=simulateStreamAnalysis)
#t2.daemon = True
#t2.start()
