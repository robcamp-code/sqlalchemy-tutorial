from typing import List, Union, Optional
from datetime import date, datetime
from pydantic import (
    BaseModel, 
    Field, 
    conlist, 
    field_validator
)


class Periods(BaseModel):
    first: Optional[int]
    second: Optional[int]


class Venue(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    city: Optional[str] = None


class Status(BaseModel):
    long: str
    short: str
    elapsed: int


class Fixture(BaseModel):
    id: int
    referee: Optional[str]
    timezone: str
    date: str
    timestamp: int
    periods: Periods
    venue: Optional[Venue] = None
    status: Status


class League(BaseModel):
    id: int
    name: str
    country: str
    logo: str
    flag: str
    season: int
    round: str


class Team(BaseModel):
    id: int
    name: str = ""
    logo: str = ""


class TeamDetail(Team):
    winner: bool


class FixtureTeams(BaseModel):
    home: TeamDetail
    away: TeamDetail


class FixtureResponseTeams(BaseModel):
    home: Team
    away: Team


class Goals(BaseModel):
    home: int
    away: int


class ScoreDetail(BaseModel):
    home: Optional[int]
    away: Optional[int]


class Score(BaseModel):
    halftime: ScoreDetail
    fulltime: ScoreDetail
    extratime: ScoreDetail
    penalty: ScoreDetail


class FixtureResponse(BaseModel):
    fixture: Fixture
    league: League
    teams: FixtureResponseTeams
    goals: Goals
    score: Score


class Player(BaseModel):
    id: int
    # name: str = ""
    first_name: str = Field(..., alias="firstname")
    last_name: str = Field(..., alias="firstname")
    age: Union[int, None] = None
    # birth: Any
    nationality: str


class Statistic(BaseModel):
    team: Team


class PlayerResponse(BaseModel):
    player: Player
    statistics: conlist(Statistic, min_length=1) # type: ignore


class TransferPlayer(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class TeamParent(BaseModel):
    """ Team as specified in Transfers api response """
    transfer_in: Team = Field(..., alias='in')
    transfer_out: Team = Field(..., alias='out')


class Transfer(BaseModel):
    """ Transfer Model """
    date: Union[date, None]
    type: Union[str, None] # FREE, 250 K
    teams: TeamParent

    @field_validator('date', mode='before')
    def date_not_correct_format(cls, v: str):
        try:
            return datetime.strptime(v, '%d-%m-%Y').date()
        except:
            return None


class TransferResponse(BaseModel):
    """ Transfer Response """
    player: TransferPlayer
    update: datetime
    transfers: List[Transfer]


class Time(BaseModel):
    elapsed: int
    extra: Optional[int]  # assuming the type should be int when not null


class EventResponse(BaseModel):
    time: Time
    team: Team
    player: TransferPlayer
    assist: TransferPlayer
    type: str
    detail: str
    comments: Optional[str]