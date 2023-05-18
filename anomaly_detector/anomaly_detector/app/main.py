from fastapi import FastAPI
from pydantic import BaseModel
from anomaly_detector.database.data_loader import DataLoader
import pika
from datetime import datetime
import time
import requests
import json
from anomaly_detector.model.inference import Inference

inference = Inference()


# Connection for rabbitmq. Binds the queue to the 'datagenerator' exchange. If an exception occurs the connection will restart. 
while True:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters("rmq", 5672))
        channel = connection.channel()

        queue = channel.queue_declare(queue="anomaly", durable=True)
        queue_name = queue.method.queue

        channel.queue_bind(
            exchange="datagenerator", queue=queue_name, routing_key="datagenerator.found"
        )
        # Callback to analyze received log. If an anomaly a call to the controller through post_anomaly is made. 
        def callback(ch, method, properties, body):
            analysedMessage = str(body)
            anomaly_score = inference(analysedMessage)
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
            #positive ack is sent
            channel.basic_ack(delivery_tag = method.delivery_tag)
        channel.basic_consume(queue=queue_name, on_message_callback=callback)

        channel.start_consuming()
    except pika.exceptions.ConnectionClosedByBroker:
        break
    except pika.exceptions.StreamLostError:
        time.sleep(0.5)
    