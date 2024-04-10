from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
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
    start_time = Column(Date, nullable=False)

    league = Relationship("League", back_populates="fixture", passive_deletes=True)
    home_team = Relationship("Team", back_populates="fixture", passive_deletes=True)
    away_team = Relationship("Team", back_populates="fixture", passive_deletes=True)
    game_info = Relationship("GameInfo", back_populates="fixture", passive_deletes=True)


class Team(Model):
    __tablename__ = "team"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    home_team = Relationship("Fixture", back_populates="team")
    away_team = Relationship("Fixture", back_populates="team")

    players = Relationship("player")


class League(Model):
    __tablename__ = "league"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    is_cup = Column(Boolean, nullable=False, default=False)

    fixture = Relationship("Fixture", back_populates="league", passive_deletes=True)


class TeamPlayer(Model):
    __tablename__ = "team_player"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("player.id", ondelete="CASCADE"), nullable=False, index=True)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=True)

    
class Player(Model):
    __tablename__ = "player"
    id = Column(Integer, primary_key=True, autoincrement=True)

    teams = Relationship("Team", secondary="team_player", back_populates="player", passive_deletes=True)


class GameInfo(Model):
    __tablename__ = "game_info"
    id = Column(Integer, primary_key=True, autoincrement=True)

