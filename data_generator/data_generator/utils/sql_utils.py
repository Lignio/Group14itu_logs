from sqlmodel import Session, delete
from sqlmodel import create_engine

from data_generator.utils.utility import get_env_variables
from data_generator.database.tables import Logs
from data_generator.database.tables import Anomalies


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


def empty_database_tables():
    engine = get_database_engine()
    with Session(engine) as session:
        delete_table = delete(Logs)
        delete_anomalies = delete(Anomalies)
        session.exec(delete_table)
        session.exec(delete_anomalies)
        session.commit()
