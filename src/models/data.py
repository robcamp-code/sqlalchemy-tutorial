from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import Relationship
from .base import Model
from .base import TimeStampedModel

class Fixture(TimeStampedModel):
    __tablename__ = "fixture"
    id = Column(Integer, primary_key=True, autoincrement=True)
    home_goals = Column(Integer)
    away_goals = Column(Integer)
    season = Column(Integer, nullable=False)
    start_time = Column(Date, nullable=False)


    