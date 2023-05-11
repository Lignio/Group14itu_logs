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


# class representing an anomaly.


class Anomaly(BaseModel):
    log_time: str
    log_message: str
    anomaly_score: float


# test class for putting false positives into the db. only for testing purpose
class false_positive_anomaly(BaseModel):
    log_time: str
    log_message: str
    anomaly_score: float
    false_positive: bool


# Class for caching the flagged value
class Flag:
    isFlagged = False


anomalyFlag = Flag()

# Queue with our log messages
logQueue = queue.Queue(1000)


# Method for simulating getting constant steam of mesagges and inserting them into the queue
def simulateLogstream():
    while True:
        # Missing load balancing when queue is full
        myLogmessage = requests.get(get_record).json()
        logQueue.put(myLogmessage)  # Put blocks/waits when the queue is full


# Method for analysing and handling log messages in the queue.
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
                # Flag anomaly for front-end use
                anomalyFlag.isFlagged = True
                new_post = Anomalies(**anomaly.dict())
                data_writer.write_single_row_to_database(new_post)


@app.get("/check_flag")
def checkFlag():
    flag = anomalyFlag.isFlagged
    anomalyFlag.isFlagged = False
    return flag


@app.get("/get_anomaly_list")
def get_anomaly_list():
    return data_loader.get_all_anomalies()


# Endpoint for getting a log from the datagenerator, and inserting into the db if it is an anomaly
@app.post("/post_anomaly", response_model=Anomaly)
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
        is_positive = compare_false_positive(
            anomaly.log_message
        )  # checks if anomoly is false positive
        if is_positive == True:
            return anomaly
        # anomaly = Anomaly(log_time=analysedMessage["log_time"], log_message=analysedMessage["log_message"], anomaly_score=analysedMessage["anomaly_score"])
        new_post = Anomalies(**anomaly.dict())
        data_writer.write_single_row_to_database(new_post)
    return anomaly


# Finds anomaly with id uId in db and updates it to match uFalse_Positive
@app.put("/Update_false_positive")
def update_false_postive(uId: int, uFalse_Positive: bool):
    anomaly = data_loader.get_Anomaly(uId)
    data_writer.change_false_positive(anomaly, uFalse_Positive)


# Starts two threads, one simulates the log stream, the other simulates stream analysis
@app.get("/start_stream")
def start_stream():
    t = threading.Thread(target=simulateLogstream)
    t.daemon = True
    t.start()
    t2 = threading.Thread(target=simulateStreamAnalysis)
    t2.daemon = True
    t2.start()


# method for checking if the anomaly is a false positive
# it only takes the log_message into the consideration at the moment.
def compare_false_positive(logmessage: str):
    result = data_loader.get_all_false_positives_messages()
    for x in result:
        if logmessage == x:
            return True
    return False
