from typing import List
from datetime import datetime
from itertools import chain
import json
import time

import pytz
import requests

from constants import SPORTS_API_KEY
from main import session
from schema.schema import (
    League, 
    Team, 
    Fixture, 
    Player, 
    Transfer,
    Event,
    Statistic
)
from ptypes.responses import (
    PlayerResponse, 
    TransferResponse, 
    FixtureResponse, 
    EventResponse
)
from ptypes.player import PlayerStatistic


BASE_URL = "https://v3.football.api-sports.io"
TIME_ZONE = 'US/Eastern'

ALL_TEAM_IDS = set([int(team.id) for team in Team.query.all()])
ALL_PLAYERS = set([int(player.id) for player in Player.query.all()])
ALL_FIXTURES = set([int(fixture.id) for fixture in Fixture.query.all()])
FIXTURE_STATISTICS =  set([int(stat.fixture_id) for stat in Statistic.query.all()])


succeed_count = 0
events_count = 0


def get_data(endpoint, params={}):
    ''' get league data '''
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': SPORTS_API_KEY
    }
    response = requests.get(f"{BASE_URL}/{endpoint}", headers=headers, params=params)
    print(f"USED CACHE: {response.from_cache}")
    data = response.json()
    return data


def import_league(name, country):
    """ get leagues with a given name and country and add that league to the db session """
    params = {"name": name, "country": country}
    response: dict = get_data("leagues", params)['response'][0]['league']
    league = League(id=response.get("id"), name=response.get("name"), type=response.get("type"))
    session.add(league)
    return response.get("id")


def import_teams(league_id, season) -> List[Team]:
    """ get teams from a given league and season and add the teams to the db session """

    params = {"league": league_id, "season": season}
    response: list[dict] = get_data("teams", params)['response']
    teams = []
    
    for object in response:
        # print(object)
        team = Team(id=object['team'].get("id"), name=object['team'].get("name"))
        teams.append(team)
        ALL_TEAM_IDS.add(int(team.id))
        session.add(team)
    return teams


def import_fixtures(league_id, season):
    """ get fixtures from a given league and season and add them to db session """
    
    fixtures = get_data('fixtures', params={"league": league_id, "season": season})['response']
    fixture_objects = []
    for object in fixtures:
        object = FixtureResponse(**object)
        if int(object.fixture.id) not in ALL_FIXTURES:
            start_time = datetime.fromtimestamp(object.fixture.timestamp, pytz.timezone(TIME_ZONE))
            fixture = Fixture(id=object.fixture.id,
                              home_team_id=object.teams.home.id, 
                              away_team_id=object.teams.away.id, 
                              season=season, 
                              league_id=league_id,
                              start_time=start_time,
                              tz_info=TIME_ZONE,
                              home_goals=object.score.fulltime.home,
                              away_goals=object.score.fulltime.away)
            session.add(fixture)
            fixture_objects.append(fixture)
    return fixture_objects
    

error_count = 0
def get_all_fixture_statistics(fixtures: List[Fixture]):
    """ get statistics for all fixtures """
    global error_count
    
    num_success = 0
    for fixture in fixtures:
        # print(fixture.id)
        if fixture.id not in FIXTURE_STATISTICS:
            response = get_data("fixtures/players", {"fixture": fixture.id})
            
            
            for res in response['response']:
                
                team = PlayerStatistic.model_validate(res)
                for player in team.players:
                    try:
                        if int(player.player.id) not in ALL_PLAYERS:
                            # print(f"creating player {player.player.id} that does not exist")
                            names = player.player.name.split(" ", 1)
                            if len(names) < 2: names.append("")
                            p = Player(id=player.player.id, first_name=names[0], last_name=names[1])
                            ALL_PLAYERS.add(player.player.id)
                            session.add(p)
                        
                        # print(fixture.id)
                        statistic = Statistic(**player.model_dump(),
                                                team_id=team.team.id,
                                                player_id=player.player.id,
                                                fixture_id=fixture.id)
                        session.add(statistic)
                        
                    except Exception as error:
                        print(error)
                        error_count += 1
                        print(f"ERROR COUNT: {error_count}")
            
    

                

def create_players_from_file(path):
    """ create players from prefetched data of the 2022 season """
    
    with open(path, "r") as f:
        results = json.load(f)
    # TODO: cleanup
    results = list(map(lambda x: PlayerResponse(**{key: x[key] for key in ["player", "statistics"]}), results))
    
    for result in results:
        if int(result.player.id) not in ALL_PLAYERS:
            player = Player(**result.player.model_dump())
            team = Team.query.filter(Team.id == result.statistics[0].team.id).first()
            if team:
                player.current_team_id = team.id
            else:
                print(f"Team not found for this player")
            ALL_PLAYERS.add(int(player.id))
            session.add(player)


def import_events(fixtures: List[Fixture]):
    """ import events """
    global events_count
    for fixture in fixtures:
        try:
            
            events = get_data("fixtures/events", {"fixture": fixture.id})['response']
            for event in events:
                event = EventResponse(**event)
                
                # TODO: Make custom serializer
                if event.assist.id: # event assist could be none
                    if event.assist.id not in ALL_PLAYERS:
                        name = event.assist.name.split(" ", 1)
                        if len(name) < 2: name.append("")
                        p = Player(id=event.assist.id, first_name=name[0], last_name=name[1])
                        ALL_PLAYERS.add(int(p.id))
                        session.add(p)
                
                if event.player.id not in ALL_PLAYERS:
                    name = event.player.name.split(" ", 1)
                    if len(name) < 2: name.append("")
                    p = Player(id=event.player.id, first_name=name[0], last_name=name[1])
                    ALL_PLAYERS.add(int(p.id))
                    session.add(p)
                
                e = Event(assist_id=event.assist.id,
                          player_id=event.player.id,
                          team_id=event.team.id,
                          type=event.type,
                          detail=event.detail,
                          comments=event.comments,
                          time=event.time.elapsed)
                session.add(e)
                events_count += 1
        except Exception as error:
            print(error)

    print(f"Added {events_count} events to session")


def create_transfers(teams: List[Team]):
    global succeed_count
    for team in teams:
        transfers = get_data("transfers", {"team": team.id})['response']
        
        for transfer in transfers:
            try:
                transfer = TransferResponse(**transfer)
                
                if int(transfer.player.id) not in ALL_PLAYERS:
                    name = transfer.player.name.split(" ", 1)
                    p = Player(id=transfer.player.id, first_name=name[0], last_name=name[1])
                    ALL_PLAYERS.add(int(p.id))
                    session.add(p)
                
                for transfer_object in transfer.transfers:
                    if transfer_object.teams.transfer_in.id not in ALL_TEAM_IDS:
                        print(f"NEW IN TEAM WITH ID: {transfer_object.teams.transfer_in.id}")
                        new_team = Team(**transfer_object.teams.transfer_in.model_dump())
                        ALL_TEAM_IDS.add(int(new_team.id))
                        session.add(new_team)
                    
                    if transfer_object.teams.transfer_out.id not in ALL_TEAM_IDS:
                        print(f"NEW OUT TEAM WITH ID: {transfer_object.teams.transfer_out.id}")
                        new_team = Team(**transfer_object.teams.transfer_out.model_dump())
                        ALL_TEAM_IDS.add(int(new_team.id))
                        session.add(new_team)
                    
                    t = Transfer(player_id=transfer.player.id, 
                                in_team_id=transfer_object.teams.transfer_in.id,
                                out_team_id=transfer_object.teams.transfer_out.id,
                                date=transfer_object.date)
                    succeed_count += 1
                    session.add(t)
            
            except Exception as error:
                pass
                # print(error)
                # print(transfer["transfers"])
        print(f"Successfully added {succeed_count} transfer objects to session")
