from sqlmodel import Session, delete
from sqlmodel import create_engine
from pydantic import BaseSettings

from controller.utils.utility import get_env_variables
from controller.database.tables import Logs
from controller.database.tables import Anomalies

class Settings(BaseSettings):
    anomaly_detector: str
    data_generator: str

settings = Settings()

def get_database_connection_string():
    env = get_env_variables()
    hostname = env["DATABASE_HOST"]
    port = env["DATABASE_PORT"]
    database = env["DATABASE_NAME"]
    username = env["DATABASE_USERNAME"]
    password = env["DATABASE_PASSWORD"]

    connection_string = (
        f"postgresql+psycopg2://{username}:{password}@{hostname}:{port}/{database}"
    )
    return connection_string


def get_database_engine():
    connection_string = get_database_connection_string()
    engine = create_engine(connection_string)
    return engine


#def get_anomaly_detector():
 #   env = get_env_variables()
  #  anomaly_detector = env["ANOMALY_DETECTOR"]
   # return anomaly_detector


def empty_database_tables():
    engine = get_database_engine()
    with Session(engine) as session:
        delete_table = delete(Logs)
        delete_anomalies = delete(Anomalies)
        session.exec(delete_table)
        session.exec(delete_anomalies)
        session.commit()
