import pandas as pd


def filter_by_daterange(df, start_date, end_date):
    start_dt = pd.Timestamp(start_date)
    end_dt = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    return df[(df.index >= start_dt) & (df.index <= end_dt)]


def filter_by_timewindow(df, start_date, end_date, start_time, end_time):
    filtered = filter_by_daterange(df, start_date, end_date)
    return filtered.between_time(start_time.strftime("%H:%M"), end_time.strftime("%H:%M"))
