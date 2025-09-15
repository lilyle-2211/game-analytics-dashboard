"""Engagement analytics tab."""
import streamlit as st

from dashboard.utils.ai_explainer import DashboardExplainer
from dashboard.components.insights import render_manual_insights
from .visualizations.charts import (
    plot_daily_active_users,
    plot_daily_engagement,
    plot_daily_return_rate, 
    plot_two_week_retention,
    plot_progression_milestones
)
from .insights.manual_insights import (
    DAILY_ENGAGEMENT_INSIGHTS,
    RETURN_RATE_INSIGHTS,
    TWO_WEEK_RETENTION_INSIGHTS,
    PROGRESSION_MILESTONES_INSIGHTS
)
from .queries import DAILY_ENGAGEMENT_QUERY, DAILY_RETURN_RATE_QUERY


def render_engagement_tab():
    """Render the engagement analytics tab."""
    
    # Initialize explainer
    explainer = DashboardExplainer()
    
    try:
        # Render analysis containers
        _render_daily_return_rate_analysis(explainer)
        _render_daily_engagement_analysis(explainer)
        _render_progression_milestone_analysis(explainer)
        _render_two_week_retention_analysis(explainer)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


def _render_daily_engagement_analysis(explainer):
    """Render daily engagement metrics analysis."""
    with st.container():
        st.markdown("### Daily Level Metrics")
        
        # Create two columns: plot + AI on left, manual insights on right
        col_plot, col_manual = st.columns([2, 1])
        
        with col_plot:
            plot_daily_engagement(explainer)
        
        with col_manual:
            st.markdown("**Key Notes**")
            render_manual_insights(
                DAILY_ENGAGEMENT_INSIGHTS,
                height=300,
                key_suffix="engagement"
            )


def _render_daily_return_rate_analysis(explainer):
    """Render daily user metrics analysis."""
    with st.container():
        st.markdown("### :blue[Daily User Metrics]")
        
        # Create three columns: DAU plot, Return Rate plot, manual insights
        col_dau, col_return, col_manual = st.columns([1, 1, 1])
        
        with col_dau:
            st.markdown("**Daily Active Users**")
            plot_daily_active_users(explainer)
        
        with col_return:
            st.markdown("**Daily Return Rate - Players Coming Back Each Day**")
            plot_daily_return_rate(explainer)
        
        with col_manual:
            st.markdown("**Key Notes**")
            render_manual_insights(
                RETURN_RATE_INSIGHTS,
                height=400,
                key_suffix="return_rate"
            )
        
        # Raw Data Sample & SQL Query section spanning across all columns
        with st.expander("Raw Data Sample & SQL Query", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Daily Active Users Data:**")
                st.markdown("**Data Source:** `tactile-471816.data_analyst_test_local.activity`")
                st.markdown("**SQL Query:**")
                st.code(DAILY_ENGAGEMENT_QUERY, language="sql")
                st.markdown("**Query Explanation:**")
                st.markdown("""
                - `COUNT(DISTINCT user_id)` - Counts unique users active each day
                - `GROUP BY date` - Groups data by date to get daily metrics
                - `WHERE date >= '2022-06-06'` - Filters to official launch period only
                """)
            
            with col2:
                st.markdown("**Daily Return Rate Data:**")
                st.markdown("**Data Source:** `tactile-471816.data_analyst_test_local.activity`")
                st.markdown("**SQL Query:**")
                st.code(DAILY_RETURN_RATE_QUERY, language="sql")
                st.markdown("**Query Explanation:**")
                st.markdown("""
                - `LAG(date) OVER (PARTITION BY user_id ORDER BY date)` - Gets previous date for each user
                - `DATE_DIFF(date, prev_date, DAY) = 1` - Checks if user returned next day
                - `COUNT(DISTINCT CASE WHEN ... THEN user_id END)` - Conditional count of returning users
                """)


def _render_two_week_retention_analysis(explainer):
    """Render two-week retention analysis."""
    with st.container():
        st.subheader("Two-Week Retention by Launch Phase")
        
        # Create two columns: plot + AI on left, manual insights on right
        col_plot, col_manual = st.columns([2, 1])
        
        with col_plot:
            plot_two_week_retention(explainer)
        
        with col_manual:
            st.markdown("**Key Notes**")
            render_manual_insights(
                TWO_WEEK_RETENTION_INSIGHTS,
                height=200,
                key_suffix="two_week_retention"
            )


def _render_progression_milestone_analysis(explainer):
    """Render player progression milestone analysis."""
    with st.container():
        st.markdown("### Player Progression Milestones")
        
        # Create two columns: analysis on left, manual insights on right
        col_analysis, col_manual = st.columns([2, 1])
        
        with col_analysis:
            plot_progression_milestones(explainer)
        
        with col_manual:
            st.markdown("**Key Notes**")
            render_manual_insights(
                PROGRESSION_MILESTONES_INSIGHTS,
                height=600,
                key_suffix="progression_milestones"
            )