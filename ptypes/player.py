from typing import List, Union, Optional
from datetime import date, datetime
from .responses import Team
from pydantic import (
    BaseModel, 
    Field, 
    conlist, 
    field_validator,
    model_serializer
)


class Games(BaseModel):
    minutes: Optional[int] = None
    # number: Optional[int] = None
    position: str
    rating: Optional[float] = None
    captain: bool = False
    substitute: bool


class Goals(BaseModel):
    goals_total: Optional[int] = Field(None, validation_alias='total')
    goals_conceded: Optional[int] = Field(None, validation_alias='conceded')
    assists: Optional[int] = None
    saves: Optional[int] = None


class Passes(BaseModel):
    total_passes: Optional[int] = Field(None, validation_alias='total')
    key_passes: Optional[int] = Field(None, validation_alias='key')
    passing_accuracy: Optional[str] = Field(None, validation_alias='accuracy')


class Tackles(BaseModel):
    tackles: Optional[int] =  Field(None, validation_alias='total')
    blocks: Optional[int] = None
    interceptions: Optional[int] = None


class Duels(BaseModel):
    total_duels: Optional[int] =  Field(None, validation_alias='total')
    duels_won: Optional[int] =  Field(None, validation_alias='won')


class Dribbles(BaseModel):
    dribble_attempts: Optional[int] =  Field(None, validation_alias='attempts')
    successful_dribbles: Optional[int] =  Field(None, validation_alias='success')


class Penalty(BaseModel):
    penalties_won: Optional[int] = Field(None, validation_alias='won')
    penalties_commited: Optional[int] = Field(None, validation_alias='committed')
    penalties_scored: Optional[int] = Field(None, validation_alias='scored')
    penalties_missed: Optional[int] = Field(None, validation_alias='missed')
    penalties_saved: Optional[int] = Field(None, validation_alias='saved')


class Fouls(BaseModel):
    fouls_drawn: Optional[int] = Field(None, validation_alias='drawn')
    fouls_committed: Optional[int] = Field(None, validation_alias='committed')


class Cards(BaseModel):
    yellow_cards: Optional[int] = Field(None, validation_alias='yellow')
    red_cards: Optional[int] = Field(None, validation_alias='red')


class Statistic(BaseModel):
    games: Games
    goals: Goals
    passes: Passes
    tackles: Tackles
    duels: Duels
    dribbles: Dribbles
    penalty: Penalty
    fouls: Fouls
    cards: Cards


class Player(BaseModel):
    id: int
    name: str
    photo: str


class PlayerParent(BaseModel):
    player: Player
    statistics: List[Statistic]

    @model_serializer
    def serialize(self):
        statistic = self.statistics[0]
        return {
            **statistic.games.model_dump(),
            **statistic.passes.model_dump(),
            **statistic.goals.model_dump(),
            **statistic.duels.model_dump(),
            **statistic.tackles.model_dump(),
            **statistic.dribbles.model_dump(),
            **statistic.fouls.model_dump(),
            **statistic.cards.model_dump(),
        }


class Players(BaseModel):
    player: PlayerParent
   


class PlayerStatisticTeam(Team):
    update: datetime


class PlayerStatistic(BaseModel):
    team: PlayerStatisticTeam
    players: List[PlayerParent]
