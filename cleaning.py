import numpy as np
import pandas as pd


def to_numeric_frame(df):
    """Force dataframe values to numeric. Text rows like 'Value' become NaN."""
    return df.copy().apply(pd.to_numeric, errors="coerce")


def sync_columns(cols_df):
    return cols_df.dropna(how="any")


def clean_temperature_data(cols_df, t_min, t_max, t_change):
    """Clean grouped temperature columns.

    Important fix: Excel exports sometimes contain repeated header rows such as 'Value'.
    Converting to numeric first prevents: TypeError '<' not supported between str and float.
    """
    cleaned = to_numeric_frame(cols_df)

    rows_to_remove = pd.Series(False, index=cleaned.index)

    out_of_range = (cleaned < t_min) | (cleaned > t_max)
    rows_to_remove |= out_of_range.any(axis=1)

    diffs = cleaned.diff().abs()
    spike_mask = diffs > t_change
    rows_to_remove |= spike_mask.any(axis=1)

    cleaned.loc[rows_to_remove, :] = np.nan
    return sync_columns(cleaned)


def clean_solar_data(df, col_name, solar_min=-50, solar_max=1400, max_step=300):
    cleaned = df.copy()
    cleaned[col_name] = pd.to_numeric(cleaned[col_name], errors="coerce")

    cleaned.loc[cleaned[col_name] < solar_min, col_name] = np.nan
    cleaned.loc[cleaned[col_name] > solar_max, col_name] = np.nan

    diffs = cleaned[col_name].diff().abs()
    cleaned.loc[diffs > max_step, col_name] = np.nan

    return cleaned.dropna(subset=[col_name])
