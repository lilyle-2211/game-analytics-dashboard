"""Player acquisition analytics tab."""
import streamlit as st

from dashboard.components.insights import render_manual_insights
from dashboard.tabs.acquisition.charts import (
    plot_demographics,
    plot_timeseries,
    plot_weekly_patterns,
)
from dashboard.tabs.acquisition.manual_insights import (
    DEMOGRAPHICS_INSIGHTS,
    TIMESERIES_INSIGHTS,
    WEEKLY_PATTERNS_INSIGHTS,
)
from dashboard.tabs.acquisition.processor import (
    display_raw_data_sample,
    load_and_process_acquisition_data,
)
from dashboard.utils.ai_explainer import DashboardExplainer


def render_acquisition_tab():
    """Render the player acquisition analytics tab."""

    # Initialize explainer
    explainer = DashboardExplainer()

    try:
        # Load and process data
        df, df_clean = load_and_process_acquisition_data()

        if df is None or df_clean is None:
            st.error("Failed to load acquisition data.")
            return

        # Render analysis containers
        _render_timeseries_analysis(df_clean, explainer)
        _render_weekly_patterns_analysis(df_clean, explainer)
        _render_demographics_analysis(df_clean, explainer)

        # Display raw data sample and SQL query at the bottom
        display_raw_data_sample(df)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


def _render_timeseries_analysis(df_clean, explainer):
    """Render player acquisition time series analysis."""
    with st.container():
        st.markdown(
            "<h3 style='color: #2196F3;'>Number of Players by Install Date</h3>",
            unsafe_allow_html=True,
        )

        # Create two columns: plot + AI on left, manual insights on right
        col_plot, col_manual = st.columns([2, 1])

        with col_plot:
            plot_timeseries(df_clean, explainer)

        with col_manual:
            st.markdown("**Key Notes**")
            render_manual_insights(
                TIMESERIES_INSIGHTS, height=400, key_suffix="timeseries"
            )


def _render_weekly_patterns_analysis(df_clean, explainer):
    """Render weekly patterns analysis."""
    with st.container():
        st.markdown(
            "<h3 style='color: #2196F3;'>US Player Installs by Day of Week</h3>",
            unsafe_allow_html=True,
        )

        # Create two columns: plot + AI on left, manual insights on right
        col_plot, col_manual = st.columns([2, 1])

        with col_plot:
            data_available = plot_weekly_patterns(df_clean, explainer)

        with col_manual:
            st.markdown("**Key Notes**")
            if data_available:
                render_manual_insights(
                    WEEKLY_PATTERNS_INSIGHTS, height=400, key_suffix="weekly"
                )


def _render_demographics_analysis(df_clean, explainer):
    """Render demographics distribution analysis."""
    with st.container():
        st.markdown(
            "<h3 style='color: #2196F3;'>US Player Distribution Analysis</h3>",
            unsafe_allow_html=True,
        )

        # Create two columns: plot + AI on left, manual insights on right
        col_plot, col_manual = st.columns([2, 1])

        with col_plot:
            data_available = plot_demographics(df_clean, explainer)

        with col_manual:
            st.markdown("**Key Notes**")
            if data_available:
                render_manual_insights(
                    DEMOGRAPHICS_INSIGHTS, height=600, key_suffix="demographics"
                )
