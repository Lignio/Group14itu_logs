from typing import Union
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
import json
import threading
import queue

from datetime import datetime

from controller.database.data_loader import DataLoader
from controller.database.datawriter import DataWriter
from controller.database.tables import Anomalies
from controller.utils.sql_utils import settings


app = FastAPI()
data_loader = DataLoader()
data_writer = DataWriter()

anomaly_detector = settings.anomaly_detector
data_generator = settings.data_generator

get_prediction = f"{anomaly_detector}/logs/getPredict"
get_LogList = f"{data_generator}/logs/LogList"
get_record = f"{data_generator}/logs/get_record"

#class representing an anolamy.
class Anomaly(BaseModel):
    log_time: str
    log_message: str
    anomaly_score: float 
#test class for putting false positives into the db. only for testing purpose
class false_positive_anomoly(BaseModel):
    log_time: str
    log_message: str
    anomaly_score: float
    false_positive: bool

# Function that calls the data-generator api for a list of the first 1000 logs and then calls the anomaly-detector api
# to check which of those logs are a anomaly. It then returns a list of all anomalies and there anomaly-score.
@app.get("/getAnomalyList")
def getAnomalyList(threshold: float = 0.02):
    myResult = []
    # Retrives the list from the datagenerator
    request = requests.get(get_LogList)
    # Deserialize it from json
    dataList = request.json()
    for i in dataList:
        response = requests.get(
            get_prediction,
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
        myLogmessage = requests.get(get_record).json()
        logQueue.put(myLogmessage) # Put blocks/waits when the queue is full
    

#Method for analysing and handeling log messages in the queue.
def simulateStreamAnalysis():
    while True:
        while logQueue.not_empty:
            analysedMessage = requests.get(get_prediction, params={"log_message":logQueue.get(),"threshold":0.02 })
            analysedMessage = analysedMessage.json()
            if analysedMessage["anomaly_score"] > 0.02:
                #Replace print with insertion into database
                #print(analysedMessage["log_message"])
                return post_anomaly(analysedMessage["log_message"], analysedMessage["anomaly_score"]) #changed post_test_anomaly to post_anomaly - may cause problems
        return Anomaly(log_time="10", log_message=analysedMessage["log_message"], anomaly_score=analysedMessage["anomaly_score"])


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

#Endpoint for forcing a custom anomaly with false positive as true into the db - for testing purposes
@app.post("/anomalies/post_test_false_positive",response_model=false_positive_anomoly)
def post_test_false_positive(log_message:str, anomaly_score:float):

    dt = datetime.now()
    dts = dt.strftime('%d/%m/%Y')

    anomaly = false_positive_anomoly(log_time=dts,log_message=log_message, anomaly_score=anomaly_score, false_positive=True)
    is_positive = compare_false_positive(anomaly.log_message) #checks if anomoly is false positive
    if is_positive == True:
       return anomaly
    new_post = Anomalies(**anomaly.dict())
    data_writer.write_single_row_to_database(new_post)
    return anomaly

#Endpoint for getting a log from the datagenerator, and the inserting into the db if it is an anomaly
@app.post("/anomalies/post_anomaly",response_model=Anomaly)
def post_anomaly():
    myLogmessage = requests.get(get_record)
    analysedMessage = requests.get(get_prediction, params={"log_message":myLogmessage,"threshold":0.02 })
    analysedMessage = analysedMessage.json()

    dt = datetime.now()
    dts = dt.strftime('%d/%m/%Y')
    
    anomaly = Anomaly(log_time=dts, log_message=analysedMessage["log_message"], anomaly_score=analysedMessage["anomaly_score"])
    if analysedMessage["anomaly_score"] > 0.02:
        is_positive = compare_false_positive(analysedMessage.log_message) #checks if anomoly is false positive
        if is_positive == True:
           return anomaly
        #anomaly = Anomaly(log_time=analysedMessage["log_time"], log_message=analysedMessage["log_message"], anomaly_score=analysedMessage["anomaly_score"])

        new_post = Anomalies(**anomaly.dict())
        data_writer.write_single_row_to_database(new_post)
    return anomaly


#method for checking if the anomoly is a false positive
#it only takes the log_message into the consideration at the moment. 
def compare_false_positive(logmessage: str):
    result = data_loader.get_all_false_positives_messages()
    for x in result:
        if logmessage == x:
            return True
    return False

t = threading.Thread(target=simulateLogsteam)
t.daemon = True
t.start()
t2 = threading.Thread(target=simulateStreamAnalysis)
t2.daemon = True
t2.start()
