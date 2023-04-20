from sqlalchemy import func
from sqlmodel import Session, select

from controller.database.tables import Logs, Anomalies
from controller.utils.sql_utils import get_database_engine

class DataLoader():
    def __init__(self):
        self.engine = get_database_engine()
    
    def get_all_records(self):
        with Session(self.engine) as session:
            statement = select(Logs)
            result = session.exec(statement).all()
            return result
        
    def get_count(self):
        with Session(self.engine) as session:
            statement = select(func.count(Logs.id))
            result = session.exec(statement).one()
            return result
        
    def get_ids(self):
        with Session(self.engine) as session:
            statement = select(Logs.id)
            result = session.exec(statement).all()
            return result
        
    def get_log_message(self, log_id: int):
        with Session(self.engine) as session:
            statement = select(Logs).where(Logs.id == log_id)
            result = session.exec(statement).one()
            return result

    def get_all_anomalies(self):
        with Session(self.engine) as session:
            statement = select(Anomalies)
            result = session.exec(statement).all()
            return result
        
    def get_anomaly_count(self):
        with Session(self.engine) as session:
            statement = select(func.count(Anomalies.id))
            result = session.exec(statement).one()
            return result
        
    def get_anomaly_ids(self):
        with Session(self.engine) as session:
            statement = select(Anomalies.id)
            result = session.exec(statement).all()
            return result 

    def get_anomaly_log_message(self, log_id: int):
        with Session(self.engine) as session:
            statement = select(Anomalies).where(Anomalies.id == log_id)
            result = session.exec(statement).one()
            return result

    def get_anomaly_score(self, log_id:int):
        with Session(self.engine) as session:
            statement = select(Anomalies.anomaly_score).where(Anomalies.id == log_id)
            result = session.exec(statement).one()   
            return result 
        
    def get_all_false_positives(self):
        with Session(self.engine) as session:
            statement = select(Anomalies).where(Anomalies.false_positive == True)
            result = session.exec(statement).all()
            return result
        
    def get_all_false_positives_messages(self):
        with Session(self.engine) as session:
            statement = select(Anomalies.log_message).where(Anomalies.false_positive == True)
            result = session.exec(statement).all()
            return result
           
    def get_count_false_positives(self):
        with Session(self.engine) as session:
            statement = select(func.count(Anomalies.id)).where(Anomalies.false_positive == True)
            result = session.exec(statement).all()
            return result        