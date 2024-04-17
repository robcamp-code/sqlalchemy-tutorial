from typing import List
from datetime import datetime
from itertools import chain
import json
import pytz


import requests
from types.responses import PlayerResponse
from constants import SPORTS_API_KEY
from main import session
from models.schema import League, Team, Fixture, Player


BASE_URL = "https://v3.football.api-sports.io"
TIME_ZONE = 'US/Eastern'


def get_data(endpoint, params={}):
    ''' get league data '''
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': SPORTS_API_KEY
    }
    response = requests.get(f"{BASE_URL}/{endpoint}", headers=headers, params=params)
    data = response.json()
    return data


def import_league(name, country):
    """ get leagues with a given name and country and add that league to the db session """

    params = {"name": name, "country": country}
    response: dict = get_data("leagues", params)['response'][0]['league']
    league = League(id=response.get("id"), name=response.get("name"), type=response.get("type"))
    session.add(league)
    return response.get("id")


def import_teams(league_id, season):
    """ get teams from a given league and season and add the teams to the db session """

    params = {"league": league_id, "season": season}
    response: list[dict] = get_data("teams", params)['response']
    
    for object in response:
        # print(object)
        team = Team(id=object['team'].get("id"), name=object['team'].get("name"))
        session.add(team)


def import_fixtures(league_id, season):
    """ get fixtures from a given league and season and add them to db session """
    
    fixtures = get_data('fixtures', params={"league": league_id, "season": season})['response']
    for object in fixtures:

        start_time = datetime.fromtimestamp(object['fixture']['timestamp'], pytz.timezone(TIME_ZONE))
        fixture = Fixture(home_team_id=object['teams']['home']['id'], 
                          away_team_id=object['teams']['away']['id'], 
                          season=season, 
                          league_id=league_id,
                          start_time=start_time,
                          tz_info=TIME_ZONE,
                          home_goals=object['score']['fulltime']['home'],
                          away_goals=object['score']['fulltime']['away'])
        session.add(fixture)


def create_players_from_file(path):
    """ create players from prefetched data of the 2022 season """
    
    with open(path, "r") as f:
        results = json.load(f)
    results = list(map(lambda x: PlayerResponse(**{key: x[key] for key in ["player", "statistics"]}), results))
    
    for result in results:
        player = Player(**result.player.model_dump())
        team = Team.query.filter(Team.id == result.statistics[0].team.id).first()
        if team:
            player.teams.append(team)
        else:
            print(f"Team not found for this player")
        session.add(player)

