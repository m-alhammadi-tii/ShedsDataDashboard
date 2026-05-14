import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


def build_plot_figure(cols, title):
    fig, ax = plt.subplots(figsize=(9, 4))

    # This protects raw plots from text rows like 'Value'.
    numeric_cols = cols.copy().apply(pd.to_numeric, errors="coerce")

    for col in numeric_cols.columns:
        ax.scatter(numeric_cols.index, numeric_cols[col], s=6, label=col)

    ax.set_title(title, pad=18)
    ax.tick_params(axis="x", rotation=30)
    legend_columns = min(len(numeric_cols.columns), 3)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=legend_columns, frameon=False)
    fig.tight_layout()
    return fig


def plot_map(data_map, title_prefix):
    for key, cols in data_map.items():
        fig = build_plot_figure(cols, f"{title_prefix} - {key}")
        st.pyplot(fig)
        plt.close(fig)
