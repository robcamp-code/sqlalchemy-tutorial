""" preprocessing.py """
import sys
sys.path.append('/Users/robertcampbell/sqlalchemy-tutorial/')
print(sys.path)
import pandas as pd
import numpy as np
from sqlalchemy.sql import text
from sqlalchemy import inspect
from joblib import load
from geopy.geocoders import Nominatim
from geopy import distance
from tqdm import tqdm

from main import engine
tqdm.pandas()

# TODO speed up a CPU Bound program
average_cols = [
    'rating', 'tackles', 'blocks', 
    'interceptions', 'dribble_success_percentage', 
    'duels_won_percentage', 'passing_accuracy', 'key_passes', 
    'fouls_drawn', 'fouls_committed'
]

to_remove = [
    'home_team_id', 'away_team_id', 'fouls_committed', 
    'fouls_drawn', 'yellow_cards', 'red_cards', 
    'season', 'team_id', 'player_id', 'minutes', 
    'substitute', 'position', 'goals_total',
    'goals_conceded', 'assists', 'saves', 
    'key_passes', 'total_passes',
    'tackles', 'blocks', 'interceptions', 'dribble_attempts',
    'successful_dribbles', 'captain', 'total_duels', 'duels_won',
    'home_win', 'away_win', 'is_draw', 'penalties_saved',
    "penalties_scored", "penalties_commited", "penalties_missed", 
    "penalties_won", "winner_id"
]

sum_cols = [
    'key_passes', 'total_passes', 'accurate_passes',
    'saves', 'fouls_drawn', 'fouls_committed',
    'yellow_cards', 'red_cards', 'goals_total',
    'assists'
]

CLEAN_DF = None
STATS_WINDOWS = None
TOP_PLAYER_STATS = None

coordinates_cache = load('./cache/coordinates_cache.joblib')
distance_cache = dict()
d_error_cache = dict()
c_error_cache = set()
geolocator = Nominatim(user_agent="soccer-ml")


def get_data():
    """ retrieve data from SQLite database """
    
    stats_statement = text("SELECT * FROM statistic")
    fix_statement = text("SELECT * FROM annotated_fixture")
    with engine.connect() as conn:
        stats = conn.execute(stats_statement)
        fixtures = conn.execute(fix_statement)

    stats_df = pd.DataFrame(stats)
    fix_df = pd.DataFrame(fixtures)
    return stats_df, fix_df


def get_lat_long(row, col):
    global coordinates_cache
    global c_error_cache
    suffix = ""
    if "away" in col:
        suffix = "_away"
    address, city = f"address{suffix}", f"city{suffix}" 
    # return cached result
    if row[col] in coordinates_cache:
        return coordinates_cache[row[col]]
    
    if row[col] in c_error_cache:
        return None
    
    # get lattitude and longitude locations
    location = None
    try:
        location = geolocator.geocode(f'{row[address]} {row[city]}, UK')
    except Exception:
        c_error_cache.add(row[col])
        return None

    if location:
        coordinates = (location.latitude, location.longitude)
        coordinates_cache[row[col]] = (location.latitude, location.longitude)
        return coordinates
    return None


def get_distance_traveled():
    CLEAN_DF["home_coordinates"] = CLEAN_DF.progress_apply(lambda row: get_lat_long(row, "home_team_id"), axis=1)
    CLEAN_DF.reset_index(inplace=True)
    CLEAN_DF["away_coordinates"] = CLEAN_DF.progress_apply(lambda row: get_lat_long(row, "away_team_id"), axis=1)
    CLEAN_DF["distance_traveled"] = CLEAN_DF.progress_apply(get_distance, axis=1)
    CLEAN_DF.drop(["home_coordinates", "away_coordinates", "address", "address_away", "name"], axis=1, inplace=True)


def get_dist_features(row):
    # TODO extract func
    # print(row)
    
    # home team
    fixture_id, home_team_id, away_team_id = row["fixture_id"], row["home_team_id"], row["away_team_id"]
    
    # goals
    goals_dist = pd.Series(TOP_PLAYER_STATS.xs(fixture_id).xs(home_team_id).xs(0)['goals_total'].replace(np.nan, 0).nlargest(11).sort_values(ascending=False))
    goals_dist.index = [f"home_top_scorer_{val}" for val in range(1, 12)]
    goals_dist.loc["home_goals_dist_skewness"] = goals_dist.skew()
    goals_quant = goals_dist.quantile([0.25, 0.5, 0.75])
    goals_quant.index = [f"home_goals_{0.25 * i}_quant" for i in range(1, 4)]
    home_goals_features = pd.concat([goals_dist, goals_quant])
    
    # assists
    home_assists_dist = pd.Series(TOP_PLAYER_STATS.xs(fixture_id).xs(home_team_id).xs(0)['assists'].replace(np.nan, 0).nlargest(11).sort_values(ascending=False))
    home_assists_dist.index = [f"home_top_assistor_{val}" for val in range(1, 12)]
    home_assists_dist.loc["home_assists_dist_skewness"] = home_assists_dist.skew()
    home_assist_quant = home_assists_dist.quantile([0.25, 0.5, 0.75])
    home_assist_quant.index = [f"home_assists_{0.25 * i}_quant" for i in range(1, 4)]
    home_assist_features = pd.concat([home_assists_dist, home_assist_quant])
    
    # away team
    # goals
    goals_dist = pd.Series(TOP_PLAYER_STATS.xs(fixture_id).xs(away_team_id).xs(0)['goals_total'].replace(np.nan, 0).nlargest(11).sort_values(ascending=False))
    goals_dist.index = [f"away_top_scorer_{val}" for val in range(1, 12)]
    goals_dist.loc["away_goals_dist_skewness"] = goals_dist.skew()
    goals_quant = goals_dist.quantile([0.25, 0.5, 0.75])
    goals_quant.index = [f"away_goals_{0.25 * i}_quant" for i in range(1, 4)]
    away_goal_features = pd.concat([goals_dist, goals_quant])
    
    # assists
    away_assists_dist = pd.Series(TOP_PLAYER_STATS.xs(fixture_id).xs(away_team_id).xs(0)['assists'].replace(np.nan, 0).nlargest(11).sort_values(ascending=False))
    away_assists_dist.index = [f"away_top_assistor_{val}" for val in range(1, 12)]
    away_assists_dist.loc["away_assists_dist_skewness"] = away_assists_dist.skew()
    away_assist_quant = away_assists_dist.quantile([0.25, 0.5, 0.75])
    away_assist_quant.index = [f"away_assists_{0.25 * i}_quant" for i in range(1, 4)]
    away_assist_features = pd.concat([away_assists_dist, away_assist_quant])

    features = pd.concat([home_goals_features, home_assist_features, away_goal_features, away_assist_features])
    # print(features)
    return features


def set_indexes(stats_df, fix_df):
    """ correctly sets indices and modifies dataframe inplace """
    
    fix_df.set_index("id", inplace=True)
    stats_df.set_index("id", inplace=True)
    

def join_and_sort(stats_df, fix_df) -> pd.DataFrame:
    """ join statistics dataframe and fixture dataframe, remove unneccessary columns """
    
    df = stats_df.join(fix_df, "fixture_id")
    df['start_time'] = pd.to_datetime(df['start_time'])
    df.sort_values('start_time', inplace=True)
    df.drop(['away_team_id:1'], axis=1, inplace=True)
    
    return df


def join_venue():
    """ join venue """
    global CLEAN_DF

    conn = f"sqlite:///../db.sqlite3"
    venues_df = pd.read_sql("SELECT * FROM venue", conn)
    to_remove = ["id", "surface", "image"]
    # home team venue
    CLEAN_DF.reset_index(inplace=True)
    CLEAN_DF.set_index('home_team_id', inplace=True)
    CLEAN_DF = CLEAN_DF.join(venues_df.set_index("team_id"), lsuffix="_clean")
    CLEAN_DF.drop(to_remove, axis=1, inplace=True)
    
    # away team away team venue
    CLEAN_DF.reset_index(inplace=True)
    CLEAN_DF.set_index('away_team_id', inplace=True)
    CLEAN_DF = CLEAN_DF.join(venues_df.set_index("team_id"), rsuffix="_away")
    CLEAN_DF.drop(to_remove, axis=1, inplace=True)


def create_cleaned_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    """ 
    creates dataframe without duplicate fixtures that were created during the joins.
    We will have one row per game and we can add as many features/columns to the df as we need.
    """
    
    cleaned_df = dataframe.copy()
    cleaned_df.drop_duplicates('fixture_id', inplace=True)
    cleaned_df.sort_values('start_time', inplace=True)
    cleaned_df.set_index('fixture_id', inplace=True)
    return cleaned_df


def cummulate(row: pd.Series, col_name, current, historic, n):
    """ cumulate """
    global CLEAN_DF

    all_fixtures: pd.DataFrame = CLEAN_DF[CLEAN_DF[historic] == row[current]]
    res = np.nan
    agg = all_fixtures[all_fixtures["start_time"] < row["start_time"]][col_name]
    if len(agg) > 1:
        res = agg.rolling(n, min_periods=1).sum().shift().iloc[-1]
    return res


def get_cummulative_record(dataframe, n_past_games):
    """ get cummulative record """
    dataframe['CUM_HT_HW'] = dataframe.progress_apply(lambda row: cummulate(row, col_name='home_win', current='home_name', historic='home_name', n=n_past_games), axis=1)
    dataframe['CUM_HT_HL'] = dataframe.progress_apply(lambda row: cummulate(row, col_name='away_win', current='home_name', historic='home_name', n=n_past_games), axis=1)
    dataframe['CUM_HT_HD'] = dataframe.progress_apply(lambda row: cummulate(row, col_name='is_draw', current='home_name', historic='home_name', n=n_past_games), axis=1)
    dataframe['CUM_HT_AW'] = dataframe.progress_apply(lambda row: cummulate(row, col_name='away_win', current='home_name', historic='away_name', n=n_past_games), axis=1)
    dataframe['CUM_HT_AL'] = dataframe.progress_apply(lambda row: cummulate(row, col_name='home_win', current='home_name', historic='away_name', n=n_past_games), axis=1)
    dataframe['CUM_HT_AD'] = dataframe.progress_apply(lambda row: cummulate(row, col_name='is_draw', current='home_name', historic='away_name', n=n_past_games), axis=1)
    dataframe['CUM_AT_HW'] = dataframe.progress_apply(lambda row: cummulate(row, col_name='home_win', current='away_name', historic='home_name', n=n_past_games), axis=1)
    dataframe['CUM_AT_HL'] = dataframe.progress_apply(lambda row: cummulate(row, col_name='away_win', current='away_name', historic='home_name', n=n_past_games), axis=1)
    dataframe['CUM_AT_HD'] = dataframe.progress_apply(lambda row: cummulate(row, col_name='is_draw', current='away_name', historic='home_name', n=n_past_games), axis=1)
    dataframe['CUM_AT_AW'] = dataframe.progress_apply(lambda row: cummulate(row, col_name='away_win', current='away_name', historic='away_name', n=n_past_games), axis=1)
    dataframe['CUM_AT_AL'] = dataframe.progress_apply(lambda row: cummulate(row, col_name='home_win', current='away_name', historic='away_name', n=n_past_games), axis=1)
    dataframe['CUM_AT_AD'] = dataframe.progress_apply(lambda row: cummulate(row, col_name='is_draw', current='away_name', historic='away_name', n=n_past_games), axis=1)


def get_cummulative_goals(dataframe, n_past_games):
    """ get cummulative goals """
    dataframe['H_GF_AH'] = dataframe.apply(lambda row: cummulate(row, col_name='home_goals', current='home_name', historic='home_name', n=n_past_games), axis=1)
    dataframe['H_GF_OTR'] = dataframe.apply(lambda row: cummulate(row, col_name='away_goals', current='home_name', historic='away_name', n=n_past_games), axis=1)
    dataframe['H_GA_AH'] = dataframe.apply(lambda row: cummulate(row, col_name='away_goals', current='home_name', historic='home_name', n=n_past_games), axis=1)
    dataframe['H_GA_OTR'] = dataframe.apply(lambda row: cummulate(row, col_name='home_goals', current='home_name', historic='away_name', n=n_past_games), axis=1)
    dataframe['A_GF_AH'] = dataframe.apply(lambda row: cummulate(row, col_name='home_goals', current='away_name', historic='home_name', n=n_past_games), axis=1)
    dataframe['A_GF_OTR'] = dataframe.apply(lambda row: cummulate(row, col_name='away_goals', current='away_name', historic='away_name', n=n_past_games), axis=1)
    dataframe['A_GA_AH'] = dataframe.apply(lambda row: cummulate(row, col_name='away_goals', current='away_name', historic='home_name', n=n_past_games), axis=1)
    dataframe['A_GA_OTR'] = dataframe.apply(lambda row: cummulate(row, col_name='home_goals', current='away_name', historic='away_name', n=n_past_games), axis=1)


def percentage_to_int(val):
    " convert string expressed as percentage to an integer value "
    if isinstance(val, str):
        return int(val.replace('%', ''))
    return val


def extract_ratio_features(dataframe):
    """ extract ratio features """
    dataframe.loc[:, 'passing_accuracy'] = dataframe['passing_accuracy'].apply(percentage_to_int)
    dataframe.rename(columns={"passing_accuracy": "accurate_passes"}, inplace=True)
    dataframe.loc[:, 'dribble_success_percentage'] = np.round(dataframe['successful_dribbles'] / dataframe['dribble_attempts'], 3)
    dataframe.loc[:, 'duels_won_percentage'] = np.round(dataframe['duels_won'] / dataframe['total_duels'], 3)
    dataframe['accurate_passes'].replace(0, np.nan, inplace=True)
    dataframe['total_passes'].replace(0, np.nan, inplace=True)
    dataframe['passing_accuracy'] = np.round(dataframe['accurate_passes'] / dataframe['total_passes'], 3)


def get_stats_windows(dataframe, n_past_games):
    """ get_stats_windows """
    group_cols = ['fixture_id','team_id','substitute']
    grouped = dataframe[group_cols + average_cols].groupby(group_cols)
    aggregated: pd.DataFrame = grouped.aggregate(["mean", "median", "min", "max", "std"])
    aggregated.columns = ['_'.join(reversed(col)) for col in aggregated.columns]
    mean_windows = grouped.rolling(n_past_games, min_periods=1).aggregate(["mean", "min", "max", "std"]).shift()
    mean_windows.columns = ['_'.join(reversed(col)) for col in mean_windows.columns]
    return mean_windows


def get_stats(row):
    """ For every col in average_cols grab the average mean, std, min and max """
    fixture_id, home_id, away_id = row.loc["fixture_id"], row.loc['home_team_id'], row.loc['away_team_id']
    try:
        home_stats = STATS_WINDOWS.xs(fixture_id).xs(home_id).xs(0).mean()
        
        home_stats.index = ["home_" + name for name in home_stats.index]
        
        away_stats = STATS_WINDOWS.xs(fixture_id).xs(away_id).xs(0).mean()
        away_stats.index = ["away_" + name for name in away_stats.index]
        
        return pd.concat([home_stats, away_stats])
    except Exception as error:
        print(f"ERROR AT {fixture_id}")
        return None


def return_same(val):
    return int(val.iloc[0])


def get_top_stats(dataframe, n_past_games):
    
    sum_cols = [
        "player_id", "assists", "goals_total", 
        "saves", "yellow_cards", "red_cards", 
        "fouls_committed", "fouls_drawn", "key_passes"
    ]
    
    grouped = dataframe.set_index(["fixture_id", "team_id", "substitute"])[sum_cols].groupby(["player_id"], as_index=False)
    sums = grouped.rolling(n_past_games, min_periods=1, closed='left').sum()
    
    return sums

    
def agg_sums(row, team, stat):
    return TOP_PLAYER_STATS.xs(row["fixture_id"]).xs(row.name[team]).xs(0)[stat].sum()


def get_winner_id(row):
    """ GET WINNER """
    if row["home_win"] == 1:
        return row["home_team_id"]
    elif row["away_win"] == 1:
        return row["away_team_id"]
    else:
        return np.nan
    

def get_club_history(row, n):
    """ get home_wins, away_wins, draw between two current clubs for the last n games """
    global CLEAN_DF

    ch = CLEAN_DF[
        ((CLEAN_DF["home_team_id"] == row["away_team_id"]) & (CLEAN_DF["away_team_id"] == row["home_team_id"])) | 
        ((CLEAN_DF["home_team_id"] == row["home_team_id"]) & (CLEAN_DF["away_team_id"] == row["away_team_id"]))
    ]
    history = ch[ch["start_time"] < row["start_time"]]
    home_wins = (history["winner_id"] == row["home_team_id"]).sum()
    away_wins = (history["winner_id"] == row["away_team_id"]).sum()
    draws = history["winner_id"].isna().sum()
    res = pd.Series([home_wins, away_wins, draws], index=["club_history_home_wins", "club_history_away_wins", "club_history_draws"])
    return res



def get_distance(row):
    """ get distance """
    if not row["home_coordinates"] or not row["away_coordinates"]:
        return None
    key = (row["home_team_id"], row["away_team_id"])
    if key in distance_cache:
        return distance_cache[key]

    d = distance.distance(row["home_coordinates"], row["away_coordinates"]).miles
    distance_cache[key] = d
    return d


def preprocess():
    """ preprocessing """
    global STATS_WINDOWS
    global TOP_PLAYER_STATS
    global CLEAN_DF
    
    stats_df, fix_df = get_data()
    
    set_indexes(stats_df, fix_df)
    df = join_and_sort(stats_df, fix_df)
    extract_ratio_features(df)
    CLEAN_DF = create_cleaned_df(df)
    join_venue()
    get_distance_traveled()
    get_cummulative_record(CLEAN_DF, 19)
    get_cummulative_goals(CLEAN_DF, 38)
    
    
    # mean features
    STATS_WINDOWS = get_stats_windows(df, 38)
    mean_stats = CLEAN_DF.progress_apply(get_stats, axis=1, result_type="expand")
    CLEAN_DF = pd.concat([CLEAN_DF, mean_stats], axis=1)
    
    # distribution of goal scorers and assisters
    CLEAN_DF.reset_index(inplace=True)
    TOP_PLAYER_STATS = get_top_stats(df, 38)
    dist_features = CLEAN_DF.apply(get_dist_features, result_type='expand', axis=1)
    CLEAN_DF = pd.concat([CLEAN_DF, dist_features], axis=1)

    # cummulative stats
    agg_columns = []
    for col_name in agg_columns:
        CLEAN_DF[f"home_team_cummulative_{col_name}"] = CLEAN_DF.apply(lambda x: agg_sums(x, "home_team_id", col_name), axis=1)
        CLEAN_DF[f"away_team_cummulative_{col_name}"] = CLEAN_DF.apply(lambda x: agg_sums(x, "away_team_id", col_name), axis=1)

    # club history TODO: parameterize lag features
    CLEAN_DF["winner_id"] = CLEAN_DF.apply(get_winner_id, axis=1)
    club_history_df = CLEAN_DF.apply(lambda x: get_club_history(x, 12), axis=1, result_type="expand")
    CLEAN_DF = pd.concat([CLEAN_DF, club_history_df], axis=1)

    CLEAN_DF.drop(to_remove, axis=1, inplace=True)
    print(CLEAN_DF.columns)
    CLEAN_DF.to_csv('../data/preprocessed.csv')


if __name__ == "__main__":
    preprocess()