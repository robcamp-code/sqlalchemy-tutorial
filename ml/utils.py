""" utils.py """
from pathlib import Path
import shutil

from category_encoders import OneHotEncoder
from joblib import load, dump
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.metrics import make_scorer, mean_absolute_error

from transformers import DateTransformer



def get_columns_by_type(dataframe: pd.DataFrame):
    """ 
    takes a dataframe and converts to dictionary with 
    different datatypes as keys and lists of column names as values for each data type
    """
    numeric_cols = set(dataframe.describe().columns.to_list())
    all_cols = set(dataframe.columns.to_list())
    categorical_set = all_cols - numeric_cols
    numeric_cols.remove('start_time')

    res = dict()
    res['numeric'] = list(numeric_cols)
    res['targets'] = [res['numeric'].pop(res['numeric'].index('home_goals'))]
    res['targets'].append(res['numeric'].pop(res['numeric'].index('away_goals')))
    res['timestamp'] = ['start_time']
    res['categorical'] = list(categorical_set)
    return res


def create_pipeline(col_types: dict, scorer, model_type: str, parameters: dict) -> Pipeline:
    """ create elastic Net pipeline """
    model_types = {
        "Elastic Net": ElasticNet()
    }

    date_transformer = Pipeline(steps=[
        ('transformer', DateTransformer()),
        ('encoder', OneHotEncoder(use_cat_names=True))])

    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())])

    feature_preprocessor = ColumnTransformer(transformers=[
        ('numerical', numeric_transformer, col_types["numeric"]),
        ('datetime', date_transformer, col_types["timestamp"])
    ])

    pipeline = Pipeline(steps=[
        ('preprocessor', feature_preprocessor),
        ('regressor', GridSearchCV(model_types[model_type], param_grid=parameters, refit=True, scoring=scorer))
    ])

    return pipeline


def create_trial_folder(dataset, trial_number:int):
    # increment trial number on disk
    Path.mkdir(f'../data/trial_{trial_number}')
    shutil.copy(dataset, f'../data/trial_{trial_number}/dataset.csv')
    
    
def run_trial():
    """ 
    
    1. take csv file load dataframe
    2. train test split dataframe
    3. define pipeline
    4. train data
    5. evaluate results
    6. create hyperparameter table
    7. TODO: bootstrap ci
    8. TODO: bias variance tradeoff
    
    """

    # create trial
    test_size = 0.2
    with open("../trial_number.txt", 'r+') as f:
        trial_number = int(f.read().strip())
        next_trial = trial_number + 1
        f.seek(0)
        f.write(str(next_trial))
    
    create_trial_folder('../data/prem_data.csv', trial_number)
    
    # TODO: pull sql tables and run them through preprocess functions. Store preprocessor to joblib
    df = pd.read_csv(f"../data/trial_{trial_number}/dataset.csv")
    df['start_time'] = pd.to_datetime(df['start_time'])
    col_types = get_columns_by_type(df)
    print(col_types)
    # train test split
    X = df.drop(['home_goals', 'away_goals'], axis=1)
    home_goals = df['home_goals'].to_numpy()
    away_goals = df['away_goals'].to_numpy()
    X_train, X_test, y_home_train, y_home_test, y_away_train, y_away_test = train_test_split(X, home_goals, away_goals, test_size=test_size, shuffle=False)

    params = {
        'alpha': [0.03, 0.05, 0.1],
        'l1_ratio': [0.1, 0.3, 0.5, 0.7]
    }
    mae_scorer = make_scorer(mean_absolute_error)
    home_pipeline = create_pipeline(col_types, 
                                    mae_scorer, 
                                    model_type="Elastic Net", 
                                    parameters=params)
    away_pipeline = create_pipeline(col_types, 
                                    mae_scorer, 
                                    model_type="Elastic Net", 
                                    parameters=params)
    
    # train fit predict
    home_pipeline["preprocessor"].fit(X_train)
    home_pipeline.fit(X_train, y_home_train)
    home_train_pred = home_pipeline.predict(X_train).round()
    away_pipeline.fit(X_train, y_away_train)
    away_train_pred = away_pipeline.predict(X_train).round()

    # test predictions
    home_test_pred = home_pipeline.predict(X_test).round()
    away_test_pred = away_pipeline.predict(X_test).round()
    
    # evaluate TODO add adjusted r2
    home_train_mae = mean_absolute_error(home_train_pred, y_home_train)
    home_test_mae = mean_absolute_error(home_test_pred, y_home_test)

    away_train_mae = mean_absolute_error(away_train_pred, y_away_train)
    away_test_mae = mean_absolute_error(away_test_pred, y_away_test)

    # store model with joblib
    dump(home_pipeline, f'../data/trial_{trial_number}/home_pipeline.joblib')
    dump(away_pipeline, f'../data/trial_{trial_number}/away_pipeline.joblib')
    
    # create hyperparameter table
    trial_results = pd.DataFrame({
        'home_train_mae': [home_train_mae],
        'home_test_mae': [home_test_mae],
        'away_train_mae': [away_train_mae],
        'away_test_mae': [away_test_mae],
        'dataset_path': [f'../data/trial_{trial_number}/prem_data.csv'],
        'home_model_path': [f'../data/trial_{trial_number}/home_pipeline.joblib'],
        'away_model_path': [f'../data/trial_{trial_number}/away_pipeline.joblib'],
        'test_size': [test_size],
    })
    
    home_ht = Path(f'../data/trial_{trial_number}/hyperparameter_table.csv')
    if home_ht.exists():
        ht = pd.concat([pd.read_csv(home_ht), trial_results])
        ht.to_csv(f'../data/hyperparameter_table.csv')
    else:
        trial_results.to_csv(f'../data/trial_{trial_number}/hyperparameter_table.csv')



if __name__ == "__main__":
    run_trial()