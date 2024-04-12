from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.orm import Relationship
from .base import Model
from .base import TimeStampedModel


class Fixture(TimeStampedModel):
    __tablename__ = "fixture"
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    league_id = Column(Integer, ForeignKey("league.id", ondelete="CASCADE"), nullable=False, index=True)
    home_team_id = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"), nullable=False, index=True)
    away_team_id = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"), nullable=False, index=True)

    home_goals = Column(Integer, nullable=True)
    away_goals = Column(Integer, nullable=True)
    season = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    tz_info = Column(String, nullable=False)

    league = Relationship("League", 
                          back_populates="fixture", 
                          passive_deletes=True)
    home_team = Relationship("Team", 
                             passive_deletes=True,
                             foreign_keys=[home_team_id])
    away_team = Relationship("Team", 
                             passive_deletes=True,
                             foreign_keys=[away_team_id])
    
    # one-to-many collection with uselist = False forces it to be a one to one
    officiator = Relationship("Officiator", 
                             back_populates="fixture", 
                             passive_deletes=True,
                             uselist=False)


class Team(Model):
    __tablename__ = "team"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)


    players = Relationship("Player", secondary="team_player", back_populates="teams", passive_deletes=True)


class League(Model):
    __tablename__ = "league"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False, default=False)

    fixture = Relationship("Fixture", back_populates="league", passive_deletes=True)


class TeamPlayer(Model):
    __tablename__ = "team_player"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("player.id", ondelete="CASCADE"), nullable=False, index=True)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=True)

    Relationship()

    
class Player(Model):
    __tablename__ = "player"
    id = Column(Integer, primary_key=True, autoincrement=True)

    teams = Relationship("Team", secondary="team_player", back_populates="players", passive_deletes=True)


class Officiator(Model):
    __tablename__ = "officiator"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fixture_id = Column(Integer, ForeignKey("fixture.id"), unique=True, nullable=True)
    
    # many-to-one scalar unique constraint will enforce that it't trully a one-to-noe relationship
    fixture = Relationship("Fixture", back_populates="officiator")
