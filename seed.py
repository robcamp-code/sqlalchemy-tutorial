from requests_cache import install_cache

from etl.etl import *
from main import session, BASE_DIR
from schema.schema import Team

SEASON = 2022
install_cache('http_cache', backend='sqlite', expire_after=86400)

if __name__ == "__main__":
    league_id = import_league("Premier League", "England")
    teams = import_teams(league_id, SEASON)
    fixtures = import_fixtures(league_id, SEASON)
    _ = create_players_from_file(BASE_DIR / "etl/prem-players.json")
    _ = create_transfers(teams)
    _ = import_events(fixtures)
    session.commit()


