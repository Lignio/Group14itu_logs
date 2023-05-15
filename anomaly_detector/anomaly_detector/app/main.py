from fastapi import FastAPI
from pydantic import BaseModel
from anomaly_detector.database.data_loader import DataLoader
import pika
from datetime import datetime
import time
import requests
import json
from anomaly_detector.model.inference import Inference
from loguru import logger

app = FastAPI()
inference = Inference()


# Connection for rabbitmq. Binds the queue to the 'datagenerator' exchange.
counter = 0

# class representing an anomaly.
class Anomaly(BaseModel):
    log_time: str
    log_message: str
    anomaly_score: float


class Prediction(BaseModel):
    log_message: str
    anomaly_score: float
    is_anomaly: bool


def predict(log_message: str, threshold: float = 0.02):
    anomaly_score = inference(log_message)
    is_anomaly = False
    if anomaly_score > threshold:
        is_anomaly = True
    return Prediction(
        log_message=log_message, anomaly_score=anomaly_score, is_anomaly=is_anomaly
    )


@app.get("/health")
def health():
    return {"status": "ok"}


# Same method as above, but used for testing purposes, since post-methods have access issues when called locally
@app.get("/logs/getPredict/", response_model=Prediction)
def getPredict(log_message: str, threshold: float = 0.02):
    anomaly_score = inference(log_message)
    is_anomaly = False
    if anomaly_score > threshold:
        is_anomaly = True
    return Prediction(
        log_message=log_message, anomaly_score=anomaly_score, is_anomaly=is_anomaly
    )
while True:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters("rmq", 5672))
        channel = connection.channel()

        queue = channel.queue_declare(queue="anomaly", durable=True)
        queue_name = queue.method.queue

        channel.queue_bind(
            exchange="datagenerator", queue=queue_name, routing_key="datagenerator.found"
        )
        # Callback to analyze received anomaly. The body consists of code from post_anomaly.
        def callback(ch, method, properties, body):
            global counter
            counter = counter+1
            logger.debug(counter)
            analysedMessage = str(body)
            anomaly_score = inference(analysedMessage)
            print(counter)
            if anomaly_score > 0.02:
                dt = datetime.now()
                dts = dt.strftime("%d/%m/%Y")


                requests.post(
                    "http://controller:8002/anomalies/post_anomaly",
                    params={
                        "log_message": analysedMessage,
                        "log_time": dts,
                        "anomaly_score": anomaly_score,
                    },
                )
            channel.basic_ack(delivery_tag = method.delivery_tag)
        channel.basic_consume(queue=queue_name, on_message_callback=callback)

        channel.start_consuming()
    except pika.exceptions.ConnectionClosedByBroker:
        break
    except pika.exceptions.StreamLostError:
        time.sleep(0.5)
    