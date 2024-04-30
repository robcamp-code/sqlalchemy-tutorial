from requests_cache import install_cache
from etl.etl import (
    import_league, 
    import_teams, 
    create_players_from_file, 
    create_transfers, 
    import_events, 
    import_fixtures,
    get_all_fixture_statistics,
    error_count
)
from main import session, BASE_DIR
from schema.schema import Fixture


SEASON = 2022
install_cache('http_cache', backend='sqlite', expire_after=86400)


def seed_db():
    league_id = import_league("Premier League", "England")
    teams = import_teams(league_id, SEASON)
    fixtures = import_fixtures(league_id, SEASON)
    _ = create_players_from_file(BASE_DIR / "etl/prem-players.json")
    _ = create_transfers(teams)
    _ = import_events(fixtures)
    session.commit()


if __name__ == "__main__":
    # seed_db()
    fixtures = Fixture.query.all()
    # print(len(fixtures))
    get_all_fixture_statistics(fixtures)
    
    session.commit()

    


