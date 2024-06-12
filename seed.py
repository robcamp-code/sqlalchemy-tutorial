from requests_cache import install_cache
from etl.etl import (
    import_league, 
    import_teams, 
    import_players,
    create_players_from_file, 
    create_transfers, 
    import_events, 
    import_fixtures,
    get_all_fixture_statistics,
    error_count
)
from main import session, BASE_DIR
from schema.schema import Fixture, Transfer


SEASON = 2022
install_cache('http_cache', backend='sqlite', expire_after=86400)

LEAGUE_SEASONS = [
    {"id": 39, "season": 2021},
    {"id": 39, "season": 2020},
    {"id": 39, "season": 2019},
    {"id": 39, "season": 2018},
    {"id": 39, "season": 2017},
    {"id": 39, "season": 2016},
    {"id": 39, "season": 2015},
    {"id": 39, "season": 2014},
]

def seed_db():
    # TODO figure out a way to never have duplicate transfers or events
    # Transfer.query.all().delete()
    
    for obj in LEAGUE_SEASONS:
        
        league_id, season = obj["id"], obj["season"]
        teams = import_teams(league_id, season)
        fixtures = import_fixtures(league_id, season)
        session.commit()
        _ = import_players(league_id, season)
        _ = create_transfers(teams)
        _ = import_events(fixtures)
        _ = get_all_fixture_statistics(fixtures)
        print(f"SEASON: {obj["season"]} FINISHED")
        session.commit()


if __name__ == "__main__":
    # seed_db()
    # seed_db()
    print(BASE_DIR)
