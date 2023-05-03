FROM python:3.10

ENV DATABASE_HOST db
ENV DATABASE_PORT 5432
ENV DATABASE_NAME postgres
ENV DATABASE_USERNAME postgres
ENV DATABASE_PASSWORD postgres
ENV ANOMALY_DETECTOR http://anomaly_detector:8001
ENV DATA_GENERATOR http://data_generator:8000

WORKDIR /app

COPY ./controller .

RUN pip install -e .
RUN pip install uvicorn
RUN pip install pika
RUN pip install logging

CMD ["uvicorn", "controller.app.main:app", "--host", "0.0.0.0", "--port", "8002"]
