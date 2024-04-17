from typing import List, Union
from datetime import date, datetime
from pydantic import BaseModel, HttpUrl, Field, conlist


{
    "player": {
        "id": 276,
        "name": "Neymar",
        "firstname": "Neymar",
        "lastname": "da Silva Santos Júnior",
        "age": 28,
        "birth": {},
        "nationality": "Brazil",
        "height": "175 cm",
        "weight": "68 kg",
        "injured": False,
        "photo": "https://media.api-sports.io/football/players/276.png"
    },
    "statistics": []
}


class Player(BaseModel):
    id: int
    # name: str = ""
    first_name: str = Field(..., alias="firstname")
    last_name: str = Field(..., alias="firstname")
    age: Union[int, None] = None
    # birth: Any
    nationality: str


class Team(BaseModel):
    id: int
    name: str = ""
    logo: HttpUrl = ""


class Statistic(BaseModel):
    team: Team


class PlayerResponse(BaseModel):
    player: Player
    statistics: conlist(Statistic, min_length=1) # type: ignore


class TransferPlayer(BaseModel):
    id: int
    name: str


class TeamParent(BaseModel):
    """ Team as specified in Transfers api response """
    transfer_in: Team = Field(..., alias='in')
    transfer_out: Team = Field(..., alias='out')


class Transfer(BaseModel):
    date: date
    type: str # FREE, 250 K
    teams: TeamParent


class TransferResponse(BaseModel):
    """ Transfer Response """
    player: TransferPlayer
    update: datetime
    transfers: List[Transfer]

