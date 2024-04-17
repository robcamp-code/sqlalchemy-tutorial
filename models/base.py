from datetime import datetime

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime
from main import session

Model = declarative_base()
Model.query = session.query_property()

class TimeStampedModel(Model):
    __abstract__ = True

    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, onupdate=datetime.now())
