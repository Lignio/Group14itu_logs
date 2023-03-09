## Requirments
Docker and docker-compose: https://docs.docker.com/engine/install/ubuntu/

## Description
This repository contains three components.

### A postgres database
The database is used as a backend for storing log messages for the data generator
### A data generator REST service
The REST services provides log messages upon make a regquest. 
### A REST endpoint for the anomaly detection model
The REST endpoint for anomaly detection takes a log message as input and predicts if the message is an anomaly. Optinally a threshold for anomalies can be provided.
## Running the code
From the root of the project (same folder as the readme), run 
```bash
docker-compose -f docker/docker-compose.yaml up   
```
Alternatively you can use the make command
```bash
make compose_up
```
Building the images can take a few minutes.
### Acessing the data generator
By default the data generator listen on localhost:8000 <br>
Swagger ui is provided on localhost:8000/docs

### Acessing the anomaly detection service
The anomaly detection rest services listens on localhost:8001 <br>
Swagger ui is provided on localhost:8001/docs


### Running the controller api
The controller api is run by calling python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
from the termial within the controller folder.The api only currently has one method - which returns a list of anomalies amongs the first 1000 logs in the database. The api listens on localhost:8002 and swapper ui is provided on localhost:8002/docs