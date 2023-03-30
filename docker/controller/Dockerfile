FROM python:3.10

ENV DATABASE_HOST db
ENV DATABASE_PORT 5432
ENV DATABASE_NAME postgres
ENV DATABASE_USERNAME postgres
ENV DATABASE_PASSWORD postgres

WORKDIR /app

COPY ./controller .

RUN pip install -e .
RUN pip install uvicorn

CMD ["uvicorn", "controller.app.main:app", "--host", "0.0.0.0", "--port", "8002"]


