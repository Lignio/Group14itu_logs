## Requirments
Docker and docker-compose: https://docs.docker.com/engine/install/ubuntu/

## Description
This repository provides a service for log message filtration, and handling of found anomalies.
It can receive a stream of log messages (currently internally simulated), predict which are anomalies and show the user in the frontend where they can handle it.
A more through explaination of the product can be found in the Technical_Overview.pdf in this folder.
This repository consists of seven components.

### A postgres database
The database is used as a backend for storing anomalies found and information about them.

### A data generator REST service
The REST services provide log messages upon make a request. Used to simulate log messages.

### A REST endpoint for the anomaly detection model
The REST endpoint for anomaly detection takes a log message as input and predicts if the message is an anomaly.

### A REST endpoint for the Controller
The Controller acts as a mediator, making communication between other parts of the program with combined API calls.

### A Rabbitmq message broker
Rabbitmq is a message broker service that enables the program to have multiple anomaly detectors and ensures there is no loss of data incase of a crash. It is a distibuted queue, that holds onto the messages on a seperate server and delivers them to the anomaly detector.

### Authentication container
A seperate container for authentication is used to handle authentication and user management for the app. The container runs on the 'Keycloak' image.

### A Frontend
A website where one can see one's anomalies and handle them.

For a more detailed description, see "link here"

## Running the code
From the docker folder, run
`docker compose build`

To build the images. This can take a few minutes.
Now you can run
`docker compose up`

Alternatively

From the root of the project (same folder as the readme), run
```bash
docker-compose -f docker/docker-compose.yaml up
```
Alternatively, you can use the make command
```bash
make compose_up
```
Building the images can take a few minutes.

### Accessing the database
The database listens on port 5432

### Accessing the data generator
By default, the data generator listen on localhost:8000 <br>
Swagger ui is provided on localhost:8000/docs

### Accessing the anomaly detection service
The anomaly detection rest services listens on localhost:8001 <br>
Swagger ui is provided on localhost:8001/docs

### Accessing the controller api
The controller listens on localhost:8002 <br>
Swagger ui is provided on localhost:8002/docs

### Accessing the keycloak admin console
The admin console for keycloak is accesible from your browser. Once the authentication container is running, navigate to 'localhost:8080/admin' (or whichever port docker says it runs on). From here, log in with your admin credentials, initially set to: Username: admin password: admin (these credentials can and should be changed in the docker compose file, where the keycloak container is started). From here, the admin can create users, clients, roles, etc.  * Important: * In order for the login of the application to function, a client must be created with the name 'dashclient'.  The keycloak handler file needs a client name to access the users and their login info, which is initially set to be 'dashclient'.

### Accessing the Rabbitmq admin mangemnt
Go to localhost:15672
Login: guest/guest

### Accessing the Frontend
The Frontend is a website that can be accessed on localhost:8050

### Known bugs and issues
- Currently the dropdown for severity on the Anomalies page does not display properly on firefox.
- When using Firefox, marking/unmarking anomalies as false positives does not cause a visual change on the page like it should before either reloading, selecting different filters or marking/unmarking another anomaly.

