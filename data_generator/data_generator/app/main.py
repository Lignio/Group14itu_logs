import random
import pika
import json

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


connection = pika.BlockingConnection(pika.ConnectionParameters("rmq", 5672))
channel = connection.channel()

channel.exchange_declare(exchange="datagenerator", exchange_type="direct")

@app.get("/rabbitmqTest/")
def publish():
    logmessage = json.dumps(data_loader.get_log_message(random.choice(ids)).log_message)
    channel.basic_publish(
        exchange="datagenerator", routing_key="datagenerator.found", body=logmessage
    )
    return "success"

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
