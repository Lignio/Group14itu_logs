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
from controller.utils.sql_utils import settings


app = FastAPI()
data_loader = DataLoader()
data_writer = DataWriter()

anomaly_detector = settings.anomaly_detector
data_generator = settings.data_generator

get_prediction = f"{anomaly_detector}/logs/getPredict"
get_LogList = f"{data_generator}/logs/LogList"
get_record = f"{data_generator}/logs/get_record"


class Anomaly(BaseModel):
    log_time: str
    log_message: str
    anomaly_score: float


class FalsePositive(BaseModel):
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
def simulateLogstream():
    while True:
        # Missing load balancing when queue is full
        myLogmessage = requests.get(get_record).json()
        logQueue.put(myLogmessage)  # Put blocks/waits when the queue is full


# Method for analysing and handeling log messages in the queue.
def simulateStreamAnalysis():
    while True:
        while logQueue.not_empty:
            analysedMessage = requests.get(
                get_prediction,
                params={"log_message": logQueue.get(), "threshold": 0.02},
            )
            analysedMessage = analysedMessage.json()

            dt = datetime.now()
            dts = dt.strftime("%d/%m/%Y")

            anomaly = Anomaly(
                log_time=dts,
                log_message=analysedMessage["log_message"],
                anomaly_score=analysedMessage["anomaly_score"],
            )

            if analysedMessage["anomaly_score"] > 0.02:
                # Replace print with insertion into database
                # print(analysedMessage["log_message"])
                new_post = Anomalies(**anomaly.dict())
                data_writer.write_single_row_to_database(new_post)


# Gets all anomalies
@app.get("/anomalies/get_anomaly_list")
def get_anomaly_list():
    return data_loader.get_all_anomalies()


# Endpoint for getting a log from the datagenerator, and the inserting into the db if it is an anomaly
@app.post("/anomalies/post_anomaly", response_model=Anomaly)
def post_anomaly():
    myLogmessage = requests.get(get_record)
    analysedMessage = requests.get(
        get_prediction, params={"log_message": myLogmessage, "threshold": 0.02}
    )
    analysedMessage = analysedMessage.json()

    dt = datetime.now()
    dts = dt.strftime("%d/%m/%Y")

    anomaly = Anomaly(
        log_time=dts,
        log_message=analysedMessage["log_message"],
        anomaly_score=analysedMessage["anomaly_score"],
    )
    if analysedMessage["anomaly_score"] > 0.02:
        anomaly = Anomaly(
            log_time=analysedMessage["log_time"],
            log_message=analysedMessage["log_message"],
            anomaly_score=analysedMessage["anomaly_score"],
        )
        new_post = Anomalies(**anomaly.dict())
        data_writer.write_single_row_to_database(new_post)
    return anomaly


@app.put("/anomalies/Update_false_positive")
def update_false_postive(uId: int, uFalse_Positive: bool):
    anomaly = data_loader.get_Anomaly(uId)
    data_writer.change_false_positive(anomaly, uFalse_Positive)


# Starts two threads, one simulation the log stream, the other simulating stream analysis
@app.get("/anomalies/start_stream")
def start_stream():
    t = threading.Thread(target=simulateLogstream)
    t.daemon = True
    t.start()
    t2 = threading.Thread(target=simulateStreamAnalysis)
    t2.daemon = True
    t2.start()
