import random
import pika
import json
import threading
import time

from datetime import datetime

from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

from data_generator.database.data_loader import DataLoader
from data_generator.database.datawriter import DataWriter
from data_generator.data.log_parser import LogParser
from data_generator.database.tables import Anomalies


app = FastAPI()
data_loader = DataLoader()
data_writer = DataWriter()
ids = data_loader.get_ids()
if len(ids) == 0:
    log_parser = LogParser()
    log_parser()
    ids = data_loader.get_ids()


class Anomaly(BaseModel):
    log_time: str
    log_message: str
    anomaly_score: float

#connecting to rabbitmqserver
connection = pika.BlockingConnection(pika.ConnectionParameters("rmq", 5672))
channel = connection.channel()

#declare exchange for sending messages to server
channel.exchange_declare(exchange="datagenerator", exchange_type="direct")

connection.close()


# Method for simulating getting constant steam of messages and inserting them into the queue
def simulateLogstream():
    print("time ", datetime.now().strftime("%H:%M:%S"))
    i = 0

    #connecting to rabbitmqserver
    connection = pika.BlockingConnection(pika.ConnectionParameters("rmq", 5672))
    channel = connection.channel()

    while i<5000:
        time.sleep(0.01)
        logmessage = json.dumps(data_loader.get_log_message(random.choice(ids)).log_message)
        channel.basic_publish(
             exchange="datagenerator", routing_key="datagenerator.found", body=logmessage
        )
        i+=1


@app.get("/rabbitmqTest/")
def publish():
    #connecting to rabbitmqserver
    connection = pika.BlockingConnection(pika.ConnectionParameters("rmq", 5672))
    channel = connection.channel()

    #sendeing a random log to anomaly detector to be analysed
    logmessage = json.dumps(data_loader.get_log_message(random.choice(ids)).log_message)
    channel.basic_publish(
        exchange="datagenerator", routing_key="datagenerator.found", body=logmessage
    )
    connection.close()
    return "success"

# Starts two threads, one simulates the log stream, the other simulates stream analysis
@app.get("/anomalies/start_stream")
def start_stream():
    t = threading.Thread(target=simulateLogstream)
    t.daemon = True
    t.start()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/logs/get_record")
def get_record():
    return data_loader.get_log_message(random.choice(ids)).log_message


# Function for getting the first 1000 logs in the database
@app.get("/logs/LogList/")
def get_logList():
    myResult = []
    for i in data_loader.get_all_records():
        if i.id < 1000:
            myResult.append((i.log_message, 0, False))
        else:
            break
    return myResult
