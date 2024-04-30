from typing import List
import logging

from sqlalchemy.orm import aliased
from sqlalchemy import or_, and_, desc, asc

from schema.schema import Team, Player, Fixture

# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.NOTSET)

home_team = aliased(Team)
away_team = aliased(Team)


def get_fixtures():
    """ GET FIXTURES """
    fixture: Fixture = Fixture.query.first()
    print(f"LEAGUE: {fixture.league.name}")
    print(f"KICKOFF @ {fixture.start_time} {fixture.tz_info}")
    print(f"SCORE: {fixture.home_team.name}: {fixture.home_goals} {fixture.away_team.name}: {fixture.away_goals}")


def get_games(team_name: str, limit: int = 20) -> List[Fixture]:
    """ get all games in a season for team with name [team_name] """
    games: List[Fixture] = Fixture.query \
    .join(home_team, Fixture.home_team) \
    .join(away_team, Fixture.away_team) \
    .filter(or_(home_team.name == team_name, away_team.name == team_name)) \
    .order_by(desc(Fixture.start_time)) \
    .limit(limit)
    
    return games


def get_historical_matchups(team_names: List[str]) -> List[Fixture]:
    matchups: List[Fixture] = Fixture.query \
    .join(home_team, Fixture.home_team) \
    .join(away_team, Fixture.away_team) \
    .filter(and_(home_team.name.in_(team_names), 
                 away_team.name.in_(team_names)))
    return matchups
    
    
def print_fixtures(fixtures: List[Fixture]) -> None:
    for fixture in fixtures:
        print(f"LEAGUE: {fixture.league.name}")
        print(f"HOME: {fixture.home_team.id} {fixture.home_team.name} {fixture.home_goals} AWAY: {fixture.away_team.name} {fixture.away_goals}")
        print(f"KICKOFF @ {fixture.start_time} {fixture.tz_info}")

    # for game in man_u_games:
    #     print(f"HOME: {game.home_team.name} {game.home_goals} AWAY: {game.away_team.name} {game.away_goals}")


def print_players(players: List[Player]) -> None:
    for player in players[:10]:
        print(f"NAME: {player.first_name} {player.last_name}\nAGE: {player.age}\nNATIONALITY: {player.nationality}")
        if len(player.teams[0]) > 0:
            players.teams[0].name


def get_players() -> List[Player]:

    players = Player.query.all()
    return players


if __name__ == "__main__":
    man_u_brighton = get_historical_matchups(["Manchester United", "Brighton"])
    man_u_games = get_games("Manchester United")
    print_fixtures(man_u_games)
    # players = get_players()
    # print_players(players)

