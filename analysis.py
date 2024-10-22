import pandas as pd


def find_temporal_slots(dto, inactivity_threshold=pd.Timedelta("1m")):
    change = (dto["Begin"] - dto["End"].shift()) > inactivity_threshold
    return change.cumsum()

def expand_slots(df, temporal_slots, column='Case'):
    def expand(x):
        uni = x.dropna().unique()
        if len(uni) == 1:
            return uni[0]
        else:
            return x

    case_expand = df.groupby(temporal_slots)[column].transform(expand)
    return case_expand