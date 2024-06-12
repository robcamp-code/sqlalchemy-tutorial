""" transformers.py """
from datetime import datetime
from sklearn.base import TransformerMixin, BaseEstimator


import pandas as pd


weekdays = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}


class DateTransformer(BaseEstimator, TransformerMixin):
    """ Date Transformer """
    
    
    def fit(self, X, y=None):
        """ fit """
        return self
    
    def to_weekday(self, date:datetime) -> int:
        """ RETURN weekday as a string """
        return weekdays[date.weekday()].lower()
    
    def is_weekend(self, date:datetime) -> int:
        """ RETURN 1 if its a weekend and 0 otherwise """
        if date.weekday() >= 5:
            return 1
        return 0
    
    def time_of_day_classification(self, date:datetime) -> int:
        """ TODO implement time of day classification: Morning, Midday, Night """
        pass

    def transform(self, X:pd.DataFrame):
        """ transform """
        types = pd.Series(X.dtypes.apply(lambda x: str(x)))
        date_columns = types[types.str.contains('datetime')].index.to_list()
        
        return_cols = []
        for date_col in date_columns:
            # applying functions
            X[f"{date_col}_weekday"] = X[date_col].apply(self.to_weekday)
            X[f"{date_col}_is_weekend"] = X[date_col].apply(self.is_weekend)

            # add to return cols list
            return_cols.append(f"{date_col}_weekday")
            return_cols.append(f"{date_col}_is_weekend")

        print((X.columns))   
        return X.loc[:, return_cols]