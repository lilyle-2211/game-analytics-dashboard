"""Monetization analytics tab."""
import streamlit as st
import pandas as pd

from dashboard.config.database import get_bigquery_data
from dashboard.utils.ai_explainer import DashboardExplainer
from dashboard.components.insights import render_manual_insights
from .charts import (
    render_iap_metrics,
    plot_iap_chart,
    render_ad_metrics,
    plot_ad_chart,
    plot_revenue_per_user_metrics,
    render_revenue_per_user_metrics_boxes,
    render_revenue_per_user_table,
    display_raw_data_section
)
from .manual_insights import (
    IAP_REVENUE_INSIGHTS,
    AD_REVENUE_INSIGHTS,
    REVENUE_PER_USER_INSIGHTS
)
from .queries import REVENUE_BY_SOURCE_QUERY, ANOMALY_TRANSACTIONS_QUERY


def render_monetization_tab():
    """Render the monetization analytics tab."""
    
    # Initialize explainer
    explainer = DashboardExplainer()
    
    try:
        # Load the data once
        with st.spinner("Loading revenue data..."):
            df = get_bigquery_data(REVENUE_BY_SOURCE_QUERY)
            anomaly_df = get_bigquery_data(ANOMALY_TRANSACTIONS_QUERY)
        
        if not df.empty:
            # Convert date column to datetime
            df['revenue_date'] = pd.to_datetime(df['revenue_date'])
            
            # Render analysis sections
            _render_iap_revenue_analysis(df, anomaly_df, explainer)
            _render_ad_revenue_analysis(df, explainer)
            _render_revenue_per_user_analysis(df, anomaly_df)
            
            # Raw data section
            display_raw_data_section(df, anomaly_df)
        else:
            st.warning("No monetization data available")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


def _render_iap_revenue_analysis(df, anomaly_df, explainer):
    """Render IAP revenue analysis section."""
    with st.container():
        st.markdown("### :blue[In-App Purchase Revenue]")
        
        # Create three columns: metrics, chart, and insights
        col_metrics, col_chart, col_insights = st.columns([1, 2, 1])
        
        with col_metrics:
            render_iap_metrics(df, anomaly_df)
        
        with col_chart:
            plot_iap_chart(df, anomaly_df, explainer)
        
        with col_insights:
            st.markdown("**Key Notes**")
            render_manual_insights(
                IAP_REVENUE_INSIGHTS,
                height=350,
                key_suffix="iap_revenue"
            )


def _render_ad_revenue_analysis(df, explainer):
    """Render ad revenue analysis section."""
    with st.container():
        st.markdown("### :blue[Advertisement Revenue]")
        
        # Create three columns: metrics, chart, and insights
        col_metrics, col_chart, col_insights = st.columns([1, 2, 1])
        
        with col_metrics:
            render_ad_metrics(df)
        
        with col_chart:
            plot_ad_chart(df, explainer)
        
        with col_insights:
            st.markdown("**Key Notes**")
            render_manual_insights(
                AD_REVENUE_INSIGHTS,
                height=350,
                key_suffix="ad_revenue"
            )


def _render_revenue_per_user_analysis(df, anomaly_df):
    """Render revenue per user metrics analysis section."""
    with st.container():
        st.markdown("### :blue[Revenue Per User Metrics]")
        
        # Create three columns: metrics boxes on left, table in middle, key notes on right
        col_metrics, col_table, col_manual = st.columns([1, 2, 1])
        
        with col_metrics:
            render_revenue_per_user_metrics_boxes(df, anomaly_df)
        
        with col_table:
            st.markdown("#### Revenue Per User Metrics")
            render_revenue_per_user_table(df, anomaly_df)
        
        with col_manual:
            st.markdown("**Key Notes**")
            render_manual_insights(
                REVENUE_PER_USER_INSIGHTS,
                height=300,
                key_suffix="revenue_per_user"
            )