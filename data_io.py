import pandas as pd
import streamlit as st


def read_excel_with_time_index(uploaded_file):
    """Read an uploaded Excel file and set Time as a datetime index."""
    if uploaded_file is None:
        return None

    df = pd.read_excel(uploaded_file, index_col="Time")
    df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[~df.index.isna()]
    return df


def build_group_map(df, group_map, label="data"):
    """Create a dictionary of grouped columns and show clear errors for missing columns."""
    output = {}

    for key, columns in group_map.items():
        missing = [col for col in columns if col not in df.columns]
        if missing:
            st.error(f"Missing columns in {label} for {key}: {missing}")
            with st.expander(f"Available columns in {label}"):
                st.write(df.columns.tolist())
            continue

        output[key] = df[columns].copy()

    return output
