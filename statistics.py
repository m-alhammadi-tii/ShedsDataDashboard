import numpy as np
import pandas as pd

from config import DELTA_FORMULAS, SHED_NAMES
from filters import filter_by_daterange, filter_by_timewindow


def stats_from_map(data_map):
    rows = []
    for key, cols in data_map.items():
        means = cols.mean(numeric_only=True)
        stds = cols.std(numeric_only=True)
        for col_name in cols.columns:
            rows.append({
                "Position": key,
                "Series": col_name,
                "Mean": round(float(means[col_name]), 2) if pd.notna(means.get(col_name)) else np.nan,
                "Std Dev": round(float(stds[col_name]), 2) if pd.notna(stds.get(col_name)) else np.nan,
                "Count": int(cols[col_name].count()),
            })
    return pd.DataFrame(rows)


def process_map(column_map, start_date, end_date, start_time, end_time, clean_fn=None):
    processed_map = {k: clean_fn(v) for k, v in column_map.items()} if clean_fn else column_map

    allday_map = {k: filter_by_daterange(v, start_date, end_date) for k, v in processed_map.items()}
    daytime_map = {k: filter_by_timewindow(v, start_date, end_date, start_time, end_time) for k, v in processed_map.items()}

    return (
        processed_map,
        allday_map,
        daytime_map,
        stats_from_map(allday_map),
        stats_from_map(daytime_map),
    )


def summarize_selected_series(data_map, selections, prefix):
    summary = {}

    for shed, column_names in selections.items():
        values = []
        for group_key, col_name in column_names:
            if group_key in data_map and col_name in data_map[group_key].columns:
                values.extend(data_map[group_key][col_name].dropna().tolist())

        if values:
            summary[shed] = {
                "Mean": round(np.mean(values), 2),
                "Std Dev": round(np.std(values, ddof=1), 2) if len(values) > 1 else 0.0,
            }
        else:
            summary[shed] = {"Mean": np.nan, "Std Dev": np.nan}

    summary_df = pd.DataFrame(summary).T.reset_index()
    summary_df.columns = ["Shed", f"{prefix} Mean", f"{prefix} Std Dev"]
    return summary_df


def make_internal_summary(map_data, sensor_prefix, prefix_label):
    selections = {
        shed: [(f"{sensor_prefix}{i}", f"{shed}-{sensor_prefix}{i}") for i in range(1, 5)]
        for shed in SHED_NAMES
    }
    return summarize_selected_series(map_data, selections, prefix_label)


def make_external_summary(map_data, positions, prefix_label):
    selections = {
        shed: [(pos, f"{shed}-TCO{pos.replace('O', '')}") for pos in positions]
        for shed in SHED_NAMES
    }
    return summarize_selected_series(map_data, selections, prefix_label)


def make_internal_surface_summary(map_data, positions, prefix_label):
    selections = {
        shed: [(pos, f"{shed}-TCI{pos.replace('I', '')}") for pos in positions]
        for shed in SHED_NAMES
    }
    return summarize_selected_series(map_data, selections, prefix_label)


def calculate_delta_summary(summary_df, mean_col, selected_deltas):
    means = summary_df.set_index("Shed")[mean_col]
    results = []

    for delta in selected_deltas:
        if delta not in DELTA_FORMULAS:
            continue
        formula, left, right = DELTA_FORMULAS[delta]
        if left in means.index and right in means.index:
            results.append({"Delta": delta, "Formula": formula, "Value": means[left] - means[right]})

    return pd.DataFrame(results)


def summarize_weather(df):
    rows = []
    for col in ["Outdoor Temperature(ºC)", "Outdoor Humidity(%RH)"]:
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        rows.append({
            "Parameter": col,
            "Mean": round(series.mean(), 2) if not series.empty else np.nan,
            "Std Dev": round(series.std(), 2) if len(series) > 1 else np.nan,
            "Count": int(series.count()),
        })
    return pd.DataFrame(rows)
