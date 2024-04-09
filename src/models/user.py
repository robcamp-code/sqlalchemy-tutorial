from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import Relationship
from .base import Model
from .base import TimeStampedModel

class Fixture(TimeStampedModel):
    __tablename__ = "fixture"
    home_goals = Integer()
    away_goals = Integer()
    season = Integer(nullable=False)
    start_time = Date(nullable=False)


    