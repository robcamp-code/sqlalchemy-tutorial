from src.etl.etl import import_league, import_teams, import_fixtures
from src.utilities.functions import create_db
from src.main import session
SEASON = 2022

if __name__ == "__main__":
    _ = create_db()
    league_id = import_league("Premier League", "England")
    _ = import_teams(league_id, SEASON)
    _ = import_fixtures()
    session.commit()


