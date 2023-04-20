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

    def test_fp(self):
        with Session(self.engine) as session:
            statement = select(Anomalies).where(Anomalies.id == 1)
            result = session.exec(statement)
            anomaly = result.one()
            anomaly.false_positive = True
            session.add(anomaly)
            session.commit()
            session.refresh(anomaly)

    def write_test(self):
        data = Anomalies(
            id=100069,
            log_time="yee",
            log_message="Yeeeeeeee",
            anomaly_score=0.2,
            false_positive=True,
        )
        with Session(self.engine) as session:
            session.add(data)
            session.commit()
