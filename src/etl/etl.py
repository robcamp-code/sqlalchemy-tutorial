from datetime import datetime
import pytz

import requests
from src.constants import SPORTS_API_KEY
from src.main import session
from src.models.schema import League, Team, Fixture


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
    params = {"name": name, "country": country}
    response: dict = get_data("leagues", params)['response'][0]['league']
    league = League(id=response.get("id"), name=response.get("name"), type=response.get("type"))
    session.add(league)
    return response.get("id")


def import_teams(league_id, season):
    params = {"league": league_id, "season": season}
    response: list[dict] = get_data("teams", params)['response']
    
    for object in response:
        print(object)
        team = Team(id=object['team'].get("id"), name=object['team'].get("name"))
        session.add(team)


def import_fixtures(league_id, season):
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


        
    
