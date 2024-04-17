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

    # one to many -> a team has many transfers
    transfers_in = Relationship("transfer",
                                back_populates="transfer_in",
                                passive_deletes=True)
    transfers_out = Relationship("transfer",
                                 back_populates="transfers_out",
                                 passive_deletes=True)


class League(Model):
    __tablename__ = "league"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False, default=False)

    fixture = Relationship("Fixture", back_populates="league", passive_deletes=True)


class Transfer(Model):
    __tablename__ = "transfer"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    in_team_id = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"), nullable=False, index=True)
    out_team_id = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("player.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)

    transfer_in = Relationship("Team", 
                             passive_deletes=True,
                             foreign_keys=[in_team_id])
    transfer_out = Relationship("Team", 
                             passive_deletes=True,
                             foreign_keys=[out_team_id])
    
    player = Relationship("Player",
                          passive_deletes=True)


    
class Player(Model):
    __tablename__ = "player"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    current_team_id = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"), nullable = True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    nationality = Column(String, nullable=True)
    position = Column(String, nullable=True)
    
    transfers = Relationship("transfer", back_populates="player", passive_deletes=True)


class Officiator(Model):
    __tablename__ = "officiator"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fixture_id = Column(Integer, ForeignKey("fixture.id"), unique=True, nullable=True)
    
    # many-to-one scalar unique constraint will enforce that it't trully a one-to-noe relationship
    fixture = Relationship("Fixture", back_populates="officiator")
