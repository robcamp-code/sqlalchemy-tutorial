from etl.etl import import_league, import_teams, import_fixtures, create_players_from_file
from utilities.functions import create_db
from main import session, BASE_DIR
SEASON = 2022


if __name__ == "__main__":
    _ = create_db()
    league_id = import_league("Premier League", "England")
    _ = import_teams(league_id, SEASON)
    _ = import_fixtures(league_id, SEASON)
    _ = create_players_from_file(BASE_DIR / "etl/prem-players.json")
    session.commit()


