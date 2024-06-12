""" preprocessing.py """
import sys
sys.path.append('/Users/robertcampbell/sqlalchemy-tutorial/')
print(sys.path)
import pandas as pd
import numpy as np
from sqlalchemy.sql import text
from sqlalchemy import inspect
from main import engine

# TODO speed up a CPU Bound program
average_cols = [
    'rating', 'tackles', 'blocks', 
    'interceptions', 'dribble_success_percentage', 
    'duels_won_percentage'
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
    dataframe['CUM_HT_HW'] = dataframe.apply(lambda row: cummulate(row, col_name='home_win', current='home_name', historic='home_name', n=n_past_games), axis=1)
    dataframe['CUM_HT_HL'] = dataframe.apply(lambda row: cummulate(row, col_name='away_win', current='home_name', historic='home_name', n=n_past_games), axis=1)
    dataframe['CUM_HT_HD'] = dataframe.apply(lambda row: cummulate(row, col_name='is_draw', current='home_name', historic='home_name', n=n_past_games), axis=1)
    dataframe['CUM_HT_AW'] = dataframe.apply(lambda row: cummulate(row, col_name='away_win', current='home_name', historic='away_name', n=n_past_games), axis=1)
    dataframe['CUM_HT_AL'] = dataframe.apply(lambda row: cummulate(row, col_name='home_win', current='home_name', historic='away_name', n=n_past_games), axis=1)
    dataframe['CUM_HT_AD'] = dataframe.apply(lambda row: cummulate(row, col_name='is_draw', current='home_name', historic='away_name', n=n_past_games), axis=1)
    dataframe['CUM_AT_HW'] = dataframe.apply(lambda row: cummulate(row, col_name='home_win', current='away_name', historic='home_name', n=n_past_games), axis=1)
    dataframe['CUM_AT_HL'] = dataframe.apply(lambda row: cummulate(row, col_name='away_win', current='away_name', historic='home_name', n=n_past_games), axis=1)
    dataframe['CUM_AT_HD'] = dataframe.apply(lambda row: cummulate(row, col_name='is_draw', current='away_name', historic='home_name', n=n_past_games), axis=1)
    dataframe['CUM_AT_AW'] = dataframe.apply(lambda row: cummulate(row, col_name='away_win', current='away_name', historic='away_name', n=n_past_games), axis=1)
    dataframe['CUM_AT_AL'] = dataframe.apply(lambda row: cummulate(row, col_name='home_win', current='away_name', historic='away_name', n=n_past_games), axis=1)
    dataframe['CUM_AT_AD'] = dataframe.apply(lambda row: cummulate(row, col_name='is_draw', current='away_name', historic='away_name', n=n_past_games), axis=1)


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
    """ extract ration features """
    dataframe.loc[:, 'passing_accuracy'] = dataframe['passing_accuracy'].apply(percentage_to_int)
    dataframe.rename(columns={"passing_accuracy": "accurate_passes"}, inplace=True)
    dataframe.loc[:, 'dribble_success_percentage'] = np.round(dataframe['successful_dribbles'] * 100 / dataframe['dribble_attempts'], 3)
    dataframe.loc[:, 'duels_won_percentage'] = np.round(dataframe['duels_won'] * 100 / dataframe['total_duels'], 3)
    dataframe['accurate_passes'].replace(0, np.nan, inplace=True)
    dataframe['total_passes'].replace(0, np.nan, inplace=True)
    dataframe['passing_accuracy'] = np.round(dataframe['accurate_passes'] * 100 / dataframe['total_passes'], 3)


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
    fixture_id = row.name
    home_id, away_id = row.loc['home_team_id'], row.loc['away_team_id']
    
    home_stats = STATS_WINDOWS.xs(fixture_id).xs(home_id).xs(0).mean()
    home_stats.index = ["home_" + name for name in home_stats.index]
    
    away_stats = STATS_WINDOWS.xs(fixture_id).xs(away_id).xs(0).mean()
    away_stats.index = ["away_" + name for name in home_stats.index]
    
    return pd.concat([home_stats, away_stats])


def return_same(val):
    return int(val.iloc[0])


def get_top_player_stats(dataframe, n_past_games):
    agg_functions = {k: 'sum' for k in sum_cols}
    agg_functions['team_id'] = return_same
    groupby_player = dataframe[dataframe["substitute"] == 0][['player_id', 'team_id'] + sum_cols].groupby(['player_id'], as_index=False)
    top_player_statistics = groupby_player.rolling(n_past_games, min_periods=1).aggregate(agg_functions)
    return top_player_statistics


def get_top_n_stats(row, stat, team, n):
    """ get_top_n_goal_scorers """
    global TOP_PLAYER_STATS
    vals = TOP_PLAYER_STATS[TOP_PLAYER_STATS["team_id"] == row[team]].xs(row.name, level=1)[stat].nlargest(n).sort_values(ascending=False)
    top_goal_scorers = pd.Series(vals.values)
    return top_goal_scorers


def get_top_n(stat_col_name, team_col, n_past_games):
    """ get_top_n statistics """
    global CLEAN_DF
    top_home_scorers_df = CLEAN_DF.apply(lambda x: get_top_n_stats(x, stat_col_name, team_col, n_past_games), axis=1, result_type="expand")
    top_home_scorers_df.columns = [f"{team_col}_{stat_col_name}", f"{team_col}_{stat_col_name}_2", f"{team_col}_{stat_col_name}_3"]
    CLEAN_DF = pd.concat([CLEAN_DF, top_home_scorers_df], axis=1)
    

def agg_sums(row, team, stat):
    return TOP_PLAYER_STATS[TOP_PLAYER_STATS["team_id"] == row[team]].xs(row.name, level=1)[stat].sum()


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


def preprocess():
    """ preprocessing """
    # print(f"{engine.url}")
    # inspector = inspect(engine)
    # print(inspector.get_table_names())
    # return 
    # TODO add progress bars on all of my apply functions
    global STATS_WINDOWS
    global TOP_PLAYER_STATS
    global CLEAN_DF
    
    stats_df, fix_df = get_data()
    set_indexes(stats_df, fix_df)
    df = join_and_sort(stats_df, fix_df)
    CLEAN_DF = create_cleaned_df(df)
    get_cummulative_record(CLEAN_DF, 19)
    get_cummulative_goals(CLEAN_DF, 38)
    extract_ratio_features(df)
    
    # mean features
    STATS_WINDOWS = get_stats_windows(df, 38)

    mean_stats = CLEAN_DF.apply(get_stats, axis=1, result_type="expand")
    CLEAN_DF = pd.concat([CLEAN_DF, mean_stats], axis=1)
    
    # top goal scorers and assisters
    df.set_index('fixture_id', inplace=True)
    TOP_PLAYER_STATS = get_top_player_stats(df, 38)
    
    get_top_n('goals_total', 'home_team_id', 3)
    get_top_n('goals_total', 'away_team_id', 3)
    get_top_n('assists', 'home_team_id', 3)
    get_top_n('assists', 'away_team_id', 3)

    # cummulative stats
    agg_columns = ["saves", "yellow_cards", "red_cards", "fouls_committed", "fouls_drawn", "key_passes"]
    for col_name in agg_columns:
        CLEAN_DF[f"home_team_cummulative_{col_name}"] = CLEAN_DF.apply(lambda x: agg_sums(x, "home_team_id", col_name), axis=1)
        CLEAN_DF[f"away_team_cummulative_{col_name}"] = CLEAN_DF.apply(lambda x: agg_sums(x, "away_team_id", col_name), axis=1)

    # club history
    CLEAN_DF["winner_id"] = CLEAN_DF.apply(get_winner_id, axis=1)
    club_history_df = CLEAN_DF.apply(lambda x: get_club_history(x, 12), axis=1, result_type="expand")
    CLEAN_DF = pd.concat([CLEAN_DF, club_history_df], axis=1)

    CLEAN_DF.drop(to_remove, axis=1, inplace=True)
    CLEAN_DF.to_csv('../data/preprocessed.csv')


if __name__ == "__main__":
    preprocess()