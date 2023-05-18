from sqlalchemy.future.engine import Engine
from sqlmodel import Session, select

from controller.utils.sql_utils import get_database_engine
from controller.database.tables import Logs, Anomalies


class DataWriter:
    def __init__(self):
        self.engine: Engine = get_database_engine()

    def write_single_row_to_database(self, data):
        """Write a single row to database"""
        with Session(self.engine) as session:
            session.add(data)
            session.commit()

    def write_multiple_rows_to_database(self, data: list):
        """Write multiple rows of data to database"""
        with Session(self.engine) as session:
            for i in data:
                session.add(i)
            session.commit()

    def change_false_positive(self, data, falsePositive: bool):
        anomaly = data
        anomaly.false_positive = falsePositive
        with Session(self.engine) as session:
            session.add(anomaly)
            session.commit()

    def change_is_handled(self, data):
        anomaly = data
        anomaly.is_handled = True
        with Session(self.engine) as session:
            session.add(anomaly)
            session.commit()
