import pandas as pd
import streamlit as st

from cleaning import clean_solar_data, clean_temperature_data
from config import DEFAULT_DAY_END, DEFAULT_DAY_START, INTERNAL_GROUPS, SHEDS_GROUPS
from data_io import build_group_map, read_excel_with_time_index
from exports import export_excel_grouped
from filters import filter_by_daterange, filter_by_timewindow
from plotting import build_plot_figure, plot_map
from reporting import generate_detailed_report
from statistics import (
    calculate_delta_summary,
    make_external_summary,
    make_internal_summary,
    make_internal_surface_summary,
    process_map,
    summarize_weather,
)


st.set_page_config(page_title="Shed Data Dashboard", layout="wide")
st.title("Shed Data Dashboard")
st.caption("Unified web app for Internal Reading, Sheds Reading, and Weather Station analysis")


# =============================
# Sidebar controls
# =============================
st.sidebar.header("Controls")
start_date = st.sidebar.date_input("Start date")
end_date = st.sidebar.date_input("End date")
start_time = st.sidebar.time_input("Day window start", value=DEFAULT_DAY_START)
end_time = st.sidebar.time_input("Day window end", value=DEFAULT_DAY_END)
show_raw = st.sidebar.checkbox("Show raw plots", value=False)

if start_date > end_date:
    st.error("Start date must be on or before end date.")
    st.stop()


tab1, tab2, tab3 = st.tabs(["Detailed Data", "Weather Station", "Processed Data"])


# =============================
# Tab 1 uploads
# =============================
with tab1:
    st.subheader("Data Upload")
    internal_file = st.file_uploader("Upload internal sheds file", type=["xlsx", "xls"], key="internal")
    sheds_file = st.file_uploader("Upload sheds probe file", type=["xlsx", "xls"], key="sheds")

    t_min = st.number_input("Minimum valid temperature", value=0.0, key="tmin")
    t_max = st.number_input("Maximum valid temperature", value=75.0, key="tmax")
    t_change = st.number_input("Spike threshold", value=5.0, key="tchange")


# =============================
# Shared data preparation
# =============================
df_internal = read_excel_with_time_index(internal_file)
df_sheds = read_excel_with_time_index(sheds_file)

internal_column_map = build_group_map(df_internal, INTERNAL_GROUPS, label="internal file") if df_internal is not None else None
sheds_column_map = build_group_map(df_sheds, SHEDS_GROUPS, label="sheds probe file") if df_sheds is not None else None

internal_processed_map = internal_allday_map = internal_daytime_map = None
internal_allday_stats = internal_daytime_stats = None

sheds_cleaned_map = sheds_allday_map = sheds_daytime_map = None
sheds_allday_stats = sheds_daytime_stats = None

if internal_column_map:
    (
        internal_processed_map,
        internal_allday_map,
        internal_daytime_map,
        internal_allday_stats,
        internal_daytime_stats,
    ) = process_map(internal_column_map, start_date, end_date, start_time, end_time)

if sheds_column_map:
    (
        sheds_cleaned_map,
        sheds_allday_map,
        sheds_daytime_map,
        sheds_allday_stats,
        sheds_daytime_stats,
    ) = process_map(
        sheds_column_map,
        start_date,
        end_date,
        start_time,
        end_time,
        clean_fn=lambda df: clean_temperature_data(df, t_min, t_max, t_change),
    )


def display_stats_pair(all_df, day_df):
    c1, c2 = st.columns(2)
    with c1:
        st.write("All day statistics")
        st.dataframe(all_df, use_container_width=True)
    with c2:
        st.write("Day window statistics")
        st.dataframe(day_df, use_container_width=True)


def download_grouped_excel(label, file_name, grouped_dict):
    st.download_button(
        label,
        data=export_excel_grouped(grouped_dict),
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# =============================
# Tab 1: Detailed Data
# =============================
with tab1:
    if internal_column_map:
        st.markdown("### Internal Reading")
        if show_raw:
            plot_map(internal_column_map, "Raw")
        plot_map(internal_allday_map, "Filtered")
        display_stats_pair(internal_allday_stats, internal_daytime_stats)

        download_grouped_excel(
            "Download internal Excel report",
            f"internal_stats_{start_date}_to_{end_date}.xlsx",
            {"Internal": [("All Day", internal_allday_stats), ("Day Window", internal_daytime_stats)]},
        )

    if sheds_column_map:
        st.markdown("### Sheds Reading")
        if show_raw:
            plot_map(sheds_column_map, "Raw")
        plot_map(sheds_allday_map, "Filtered")
        display_stats_pair(sheds_allday_stats, sheds_daytime_stats)

        download_grouped_excel(
            "Download sheds surface Excel report",
            f"sheds_stats_{start_date}_to_{end_date}.xlsx",
            {"Sheds": [("All Day", sheds_allday_stats), ("Day Window", sheds_daytime_stats)]},
        )

    if internal_column_map and sheds_column_map:
        st.markdown("### Detailed Word Report")
        report_buffer = generate_detailed_report(
            start_date,
            end_date,
            internal_allday_map,
            internal_daytime_map,
            internal_allday_stats,
            internal_daytime_stats,
            sheds_allday_map,
            sheds_daytime_map,
            sheds_allday_stats,
            sheds_daytime_stats,
        )
        st.download_button(
            "Download detailed Word report",
            data=report_buffer,
            file_name=f"detailed_report_{start_date}_to_{end_date}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    elif internal_column_map or sheds_column_map:
        st.info("Upload both the internal sheds file and the sheds probe file to enable the detailed Word report button.")


# =============================
# Tab 2: Weather Station
# =============================
with tab2:
    st.subheader("Data Upload")
    weather_file = st.file_uploader("Upload weather station file", type=["xlsx", "xls"], key="weather")
    solar_file = st.file_uploader("Upload solar irradiation file", type=["xlsx", "xls"], key="solar")

    solar_min = st.number_input("Minimum valid solar irradiance", value=-50.0, key="solar_min")
    solar_max = st.number_input("Maximum valid solar irradiance", value=1400.0, key="solar_max")
    solar_change = st.number_input("Solar spike threshold", value=300.0, key="solar_change")

    if weather_file is not None and solar_file is not None:
        df_weather = pd.read_excel(weather_file, index_col="Time", parse_dates=True)
        df_solar = pd.read_excel(solar_file, index_col="Time", parse_dates=True)

        df_weather.index = pd.to_datetime(df_weather.index, errors="coerce")
        df_solar.index = pd.to_datetime(df_solar.index, errors="coerce")
        df_solar = df_solar.apply(pd.to_numeric, errors="coerce")

        weather_cols = df_weather[["Outdoor Temperature(ºC)", "Outdoor Humidity(%RH)"]].copy()
        weather_allday = filter_by_daterange(weather_cols, start_date, end_date)
        weather_daytime = filter_by_timewindow(weather_cols, start_date, end_date, start_time, end_time)

        weather_allday_stats = summarize_weather(weather_allday)
        weather_daytime_stats = summarize_weather(weather_daytime)

        st.subheader("Outdoor Temperature and Humidity")
        display_stats_pair(weather_allday_stats, weather_daytime_stats)

        fig_weather = build_plot_figure(weather_allday, "Outdoor Temperature and Humidity")
        st.pyplot(fig_weather)

        solar_col = "Smart sensor 1 Average"
        solar_df = df_solar[[solar_col]].copy()
        solar_allday = filter_by_daterange(solar_df, start_date, end_date)
        solar_daytime = filter_by_timewindow(solar_df, start_date, end_date, start_time, end_time)

        if show_raw:
            st.write("Raw Solar Irradiance vs Date")
            st.pyplot(build_plot_figure(solar_allday, "Raw Solar Irradiance"))

        solar_allday = clean_solar_data(solar_allday, solar_col, solar_min=solar_min, solar_max=solar_max, max_step=solar_change)
        solar_daytime = clean_solar_data(solar_daytime, solar_col, solar_min=solar_min, solar_max=solar_max, max_step=solar_change)

        st.subheader("Solar Irradiance")
        st.pyplot(build_plot_figure(solar_allday, "Filtered Solar Irradiance"))

        solar_series = solar_allday[solar_col].dropna()
        if not solar_series.empty:
            max_irradiance = solar_series.max()
            max_time = solar_series.idxmax()
            st.success(
                f"Maximum irradiance in the selected range is {max_irradiance:.2f} "
                f"and it occurs on {max_time.strftime('%Y-%m-%d')} at {max_time.strftime('%H:%M:%S')}."
            )
        else:
            st.warning("No solar irradiance data available in the selected date range after filtering.")

        download_grouped_excel(
            "Download weather station Excel report",
            f"weather_station_stats_{start_date}_to_{end_date}.xlsx",
            {
                "Weather": [("All Day", weather_allday_stats), ("Day Window", weather_daytime_stats)],
                "Solar": [("All Day Filtered", solar_allday.reset_index()), ("Day Window Filtered", solar_daytime.reset_index())],
            },
        )


# =============================
# Tab 3: Processed Data
# =============================
with tab3:
    st.subheader("Important Information")
    st.info("O1 - out door, O2 - out right, O3 - out back, O4 - out left, O5 - out roof")
    st.info("I1 - in door, I2 - in right, I3 - in back, I4 - in left, I5 - in roof, I6 - in floor")

    if internal_allday_map is not None:
        st.subheader("Internal Reading")

        temp_all_summary = make_internal_summary(internal_allday_map, "T", "Temperature")
        temp_day_summary = make_internal_summary(internal_daytime_map, "T", "Temperature")
        hum_all_summary = make_internal_summary(internal_allday_map, "H", "Humidity")
        hum_day_summary = make_internal_summary(internal_daytime_map, "H", "Humidity")

        st.write("Average Internal Temperature (T1–T4)")
        display_stats_pair(temp_all_summary, temp_day_summary)

        st.write("Average Internal Humidity (H1–H4)")
        display_stats_pair(hum_all_summary, hum_day_summary)

        download_grouped_excel(
            "Download processed internal Excel report",
            f"processed_internal_stats_{start_date}_to_{end_date}.xlsx",
            {
                "Temperature": [("All Day", temp_all_summary), ("Day Window", temp_day_summary)],
                "Humidity": [("All Day", hum_all_summary), ("Day Window", hum_day_summary)],
            },
        )

    if sheds_allday_map is not None:
        st.subheader("External Surface Reading")
        shaded_positions = ["O2", "O3"]
        nonshaded_positions = ["O4", "O5"]

        external_shaded_all_summary = make_external_summary(sheds_allday_map, shaded_positions, "Ext Surface T")
        external_shaded_day_summary = make_external_summary(sheds_daytime_map, shaded_positions, "Ext Surface T")
        external_nonshaded_all_summary = make_external_summary(sheds_allday_map, nonshaded_positions, "Ext Surface T")
        external_nonshaded_day_summary = make_external_summary(sheds_daytime_map, nonshaded_positions, "Ext Surface T")

        st.write("Average Shaded External Surface Temperature (O2–O3)")
        display_stats_pair(external_shaded_all_summary, external_shaded_day_summary)

        st.write("Average Non-Shaded External Surface Temperature (O4–O5)")
        display_stats_pair(external_nonshaded_all_summary, external_nonshaded_day_summary)

        st.subheader("Internal Surface Reading")
        internal_shaded_positions = ["I2", "I3"]
        internal_nonshaded_positions = ["I4", "I5"]
        internal_floor = ["I6"]

        internal_shaded_surface_all_summary = make_internal_surface_summary(sheds_allday_map, internal_shaded_positions, "Int Surface T")
        internal_shaded_day_summary = make_internal_surface_summary(sheds_daytime_map, internal_shaded_positions, "Int Surface T")
        internal_nonshaded_surface_all_summary = make_internal_surface_summary(sheds_allday_map, internal_nonshaded_positions, "Int Surface T")
        internal_nonshaded_day_summary = make_internal_surface_summary(sheds_daytime_map, internal_nonshaded_positions, "Int Surface T")
        internal_floor_all_summary = make_internal_surface_summary(sheds_allday_map, internal_floor, "Int Floor T")
        internal_floor_day_summary = make_internal_surface_summary(sheds_daytime_map, internal_floor, "Int Floor T")

        st.write("Average Shaded Internal Surface Temperature (I2–I3)")
        display_stats_pair(internal_shaded_surface_all_summary, internal_shaded_day_summary)

        st.write("Average Non-Shaded Internal Surface Temperature (I4–I5)")
        display_stats_pair(internal_nonshaded_surface_all_summary, internal_nonshaded_day_summary)

        st.write("Average Internal Floor Temperature (I6)")
        display_stats_pair(internal_floor_all_summary, internal_floor_day_summary)

        download_grouped_excel(
            "Download processed sheds surface Excel report",
            f"processed_sheds_stats_{start_date}_to_{end_date}.xlsx",
            {
                "External Shaded": [("All Day", external_shaded_all_summary), ("Day Window", external_shaded_day_summary)],
                "External Non-Shaded": [("All Day", external_nonshaded_all_summary), ("Day Window", external_nonshaded_day_summary)],
                "Internal Shaded": [("All Day", internal_shaded_surface_all_summary), ("Day Window", internal_shaded_day_summary)],
                "Internal Non-Shaded": [("All Day", internal_nonshaded_surface_all_summary), ("Day Window", internal_nonshaded_day_summary)],
                "Internal Floor": [("All Day", internal_floor_all_summary), ("Day Window", internal_floor_day_summary)],
            },
        )

    if internal_allday_map is not None and sheds_allday_map is not None:
        st.subheader("Results")
        st.info("ΔT1 = TII - C, ΔT2 = TII - R, ΔT3 = C - R")

        delta_options = st.multiselect("Select delta(s) to calculate", ["ΔT1", "ΔT2", "ΔT3"])

        if delta_options:
            delta_sections = {
                "Internal Deltas": (
                    calculate_delta_summary(temp_all_summary, "Temperature Mean", delta_options),
                    calculate_delta_summary(temp_day_summary, "Temperature Mean", delta_options),
                ),
                "External Shaded": (
                    calculate_delta_summary(external_shaded_all_summary, "Ext Surface T Mean", delta_options),
                    calculate_delta_summary(external_shaded_day_summary, "Ext Surface T Mean", delta_options),
                ),
                "External Non-Shaded": (
                    calculate_delta_summary(external_nonshaded_all_summary, "Ext Surface T Mean", delta_options),
                    calculate_delta_summary(external_nonshaded_day_summary, "Ext Surface T Mean", delta_options),
                ),
                "Internal Shaded": (
                    calculate_delta_summary(internal_shaded_surface_all_summary, "Int Surface T Mean", delta_options),
                    calculate_delta_summary(internal_shaded_day_summary, "Int Surface T Mean", delta_options),
                ),
                "Internal Non-Shaded": (
                    calculate_delta_summary(internal_nonshaded_surface_all_summary, "Int Surface T Mean", delta_options),
                    calculate_delta_summary(internal_nonshaded_day_summary, "Int Surface T Mean", delta_options),
                ),
                "Internal Floor": (
                    calculate_delta_summary(internal_floor_all_summary, "Int Floor T Mean", delta_options),
                    calculate_delta_summary(internal_floor_day_summary, "Int Floor T Mean", delta_options),
                ),
            }

            excel_sections = {}
            for section_name, (all_df, day_df) in delta_sections.items():
                st.write(section_name)
                display_stats_pair(all_df, day_df)
                excel_sections[section_name] = [("All Day", all_df), ("Day Window", day_df)]

            download_grouped_excel(
                "Download deltas Excel report",
                f"deltas_stats_{start_date}_to_{end_date}.xlsx",
                excel_sections,
            )
