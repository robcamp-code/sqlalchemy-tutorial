from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import Relationship
from .base import Model
from .base import TimeStampedModel


class Fixture(TimeStampedModel):
    __tablename__ = "fixture"
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    home_team_id = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"), nullable=False, index=True)
    away_team_id = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"), nullable=False, index=True)
    home_goals = Column(Integer, nullable=True)
    away_goals = Column(Integer, nullable=True)
    season = Column(Integer, nullable=False)
    start_time = Column(Date, nullable=False)

    home_team = Relationship("Team", back_populates="fixture", passive_deletes=True)
    away_team = Relationship("Team", back_populates="fixture", passive_deletes=True)
    metadata = Relationship("Metadata", back_populates="fixture", passive_delete=True)


class Team(Model):
    __tablename__ = "team"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    home_team = Relationship("Fixture", back_populates="team")
    away_team = Relationship("Fixture", back_populates="team")

    players = Relationship("player")


class TeamPlayer(Model):
    __tablename__ = "team_player"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey("team", ondelete="CASCADE"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("player", ondelete="CASCADE"), nullable=False, index=True)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=True)

    
class Player(Model):
    __tablename__ = "player"
    id = Column(Integer, primary_key=True, autoincrement=True)

    teams = Relationship("Team", secondary="team_player", back_populates="player", passive_deletes=True)


class Metadata(Model):
    __tablename__ = "metadata"
    id = Column(Integer, primary_key=True, autoincrement=True)

