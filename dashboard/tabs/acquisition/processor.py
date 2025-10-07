"""Data processing functions for acquisition tab."""
import pandas as pd
import streamlit as st

from dashboard.config.database import get_bigquery_data
from dashboard.tabs.acquisition.queries import PLAYER_DISTRIBUTION_QUERY


def load_and_process_acquisition_data():
    """
    Load player distribution data from BigQuery and perform necessary preprocessing.

    Returns:
        DataFrame: Cleaned and processed data ready for visualization
    """
    try:
        # Fetch data
        with st.spinner("Loading player distribution data..."):
            df = get_bigquery_data(PLAYER_DISTRIBUTION_QUERY)

        # Data preprocessing
        df_clean = df.dropna(subset=["install_date"])
        df_clean["install_date"] = pd.to_datetime(
            df_clean["install_date"], format="%Y-%m-%d", errors="coerce"
        )
        df_clean = df_clean.dropna(subset=["install_date"])
        df_clean = df_clean[
            (df_clean["install_date"] >= "2020-01-01")
            & (df_clean["install_date"] <= pd.Timestamp.now())
        ]

        return df, df_clean
    except Exception as e:
        st.error(f"An error occurred while loading data: {str(e)}")
        return None, None


def display_raw_data_sample(df):
    """Display raw data sample and SQL query."""
    with st.expander("📋 SQL Query & Data Sample", expanded=False):
        st.markdown("**Data Source:** `game-analytics.data.users`")
        st.markdown("**SQL Query:**")
        st.code(PLAYER_DISTRIBUTION_QUERY, language="sql")
        st.markdown("**Query Explanation:**")
        st.markdown(
            """
        - `SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', install_date)` - Safely parses ISO timestamp format, handles invalid dates
        - `CASE WHEN` statements - Categorizes install dates into launch phases (Soft Launch vs Official Launch)
        - `LEFT(channel_country,2)` - Extracts country code from channel_country field
        - `SPLIT(channel_country, '-')[OFFSET(1)]` - Extracts channel type after country code
        - `SAFE_CAST(age AS INT64)` - Safely converts age strings to integers, returns NULL if invalid
        - Complex age grouping logic - Handles null values and creates meaningful age brackets
        - `COUNT(DISTINCT user_id)` vs `COUNT(*)` - Unique users vs total device records
        - `GROUP BY 1, 2, 3...` - Groups by column positions for cleaner syntax
        """
        )
        st.markdown("**Data Sample:**")
        st.dataframe(df.head(100))
