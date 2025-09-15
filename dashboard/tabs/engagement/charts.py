"""Visualization functions for the engagement tab."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from dashboard.config.database import get_bigquery_data
from dashboard.utils.ai_explainer import DashboardExplainer
from dashboard.components.insights import render_ai_insights
from .queries import DAILY_ENGAGEMENT_QUERY, DAILY_RETURN_RATE_QUERY, TWO_WEEK_RETENTION_QUERY, PROGRESSION_MILESTONE_QUERY


def plot_daily_active_users(explainer):
    """Render daily active users analysis."""
    # Fetch data
    with st.spinner("Loading daily active users data..."):
        df = get_bigquery_data(DAILY_ENGAGEMENT_QUERY)
    
    if not df.empty:
        # Data preprocessing
        df['date'] = pd.to_datetime(df['date'])
        
        # Create DAU plot
        fig = px.line(df, x='date', y='daily_active_users',
                     title='',
                     markers=True)
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Daily Active Users",
            height=300
        )
        fig.update_traces(line_color='blue')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Get total unique users from return rate query (moved from return rate plot)
        try:
            return_df = get_bigquery_data(DAILY_RETURN_RATE_QUERY)
            total_unique_users = return_df['total_unique_users'].iloc[0] if not return_df.empty and 'total_unique_users' in return_df.columns else 0
        except:
            total_unique_users = 0
            
        avg_dau = df['daily_active_users'].mean()
        max_dau = df['daily_active_users'].max()
        st.info(f"**Average DAU: {avg_dau:.0f}** | **Peak DAU: {max_dau:,}** | **Total unique users: {total_unique_users:,}**")
        
        # AI Analysis - focus only on daily active users data
        dau_only_df = df[['date', 'daily_active_users']].copy()
        explanation = explainer.explain_chart("daily_active_users", dau_only_df, "Daily active users trend analysis focusing only on user count patterns")
        render_ai_insights(explanation, explainer)
    else:
        st.warning("No daily active users data available")
    
    return df if not df.empty else None


def plot_daily_engagement(explainer):
    """Render daily engagement metrics analysis."""
    # Fetch data
    with st.spinner("Loading daily engagement data..."):
        df = get_bigquery_data(DAILY_ENGAGEMENT_QUERY)
    
    if not df.empty:
        # Data preprocessing
        df['date'] = pd.to_datetime(df['date'])
        df['avg_levels_played_per_user'] = df['total_levels_played'] / df['daily_active_users']
        df['avg_levels_completed_per_user'] = df['total_levels_completed'] / df['daily_active_users']
        df['completion_rate'] = (df['total_levels_completed'] / df['total_levels_played']) * 100
        
        # Create 3 separate plots in columns
        plot_col1, plot_col2, plot_col3 = st.columns(3)
        
        with plot_col1:
            fig1 = px.line(df, x='date', y='avg_levels_played_per_user',
                          title='Levels Played per User',
                          markers=True)
            fig1.update_layout(yaxis_title='')
            fig1.update_traces(line_color='red')
            fig1.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
        
        with plot_col2:
            fig2 = px.line(df, x='date', y='avg_levels_completed_per_user',
                          title='Levels Completed per User', 
                          markers=True)
            fig2.update_layout(yaxis_title='')
            fig2.update_traces(line_color='green')
            fig2.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
        
        with plot_col3:
            fig3 = px.line(df, x='date', y='completion_rate',
                          title='Completion Rate (%)',
                          markers=True)
            fig3.update_layout(yaxis_title='')
            fig3.update_traces(line_color='black')
            fig3.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)
        
        # Display raw data sample and SQL query
        with st.expander("📋 Raw Data Sample & SQL Query", expanded=False):
            st.markdown("**Data Source:** `tactile-471816.data_analyst_test_local.activity`")
            st.markdown("**SQL Query:**")
            st.code(DAILY_ENGAGEMENT_QUERY, language="sql")
            st.markdown("**Query Explanation:**")
            st.markdown("""
            - `COUNT(DISTINCT user_id)` - Counts unique users active each day
            - `SUM(levels_played)` - Aggregates total levels played across all users per day
            - `SUM(levels_completed)` - Aggregates total levels completed across all users per day
            - `GROUP BY date` - Groups data by date to get daily metrics
            - `WHERE date >= '2022-06-06'` - Filters to official launch period only
            - Additional calculations in Python: completion rate = completed/played * 100
            """)
            st.markdown("**Data Sample:**")
            st.dataframe(df.head(20))
        
        # AI Analysis
        explanation = explainer.explain_chart("engagement_metrics", df, "Daily player engagement showing levels played, completed, and completion rates")
        render_ai_insights(explanation, explainer)
    else:
        st.warning("No engagement data available")
    
    return df if not df.empty else None


def plot_daily_return_rate(explainer):
    """Render daily return rate analysis."""
    # Fetch data
    with st.spinner("Loading return rate data..."):
        df = get_bigquery_data(DAILY_RETURN_RATE_QUERY)
    
    if not df.empty:
        # Data preprocessing
        df['date'] = pd.to_datetime(df['date'])
        
        # Single plot for daily return rate
        fig = px.line(df, x='date', y='daily_return_rate_pct', 
                     title='',
                     markers=True)
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Return Rate (%)",
            yaxis=dict(range=[0, 100]),
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary stats - only return rate related
        avg_return_rate = df['daily_return_rate_pct'].mean()
        max_return_rate = df['daily_return_rate_pct'].max()
        st.info(f"**Average return rate: {avg_return_rate:.1f}%** | **Peak return rate: {max_return_rate:.1f}%**")
        
        # AI Analysis - focus only on return rate data
        return_rate_only_df = df[['date', 'daily_return_rate_pct']].copy()
        explanation = explainer.explain_chart("return_rate", return_rate_only_df, "Daily return rate percentage trends showing player retention day-to-day")
        render_ai_insights(explanation, explainer)
    else:
        st.warning("No return rate data available")
    
    return df if not df.empty else None


def plot_two_week_retention(explainer):
    """Render two-week retention analysis."""
    # Fetch data
    with st.spinner("Loading two-week retention data..."):
        df = get_bigquery_data(TWO_WEEK_RETENTION_QUERY)
    
    if not df.empty:
        # Format the dataframe for display
        display_df = df.copy()
        display_df['total_installed_users'] = display_df['total_installed_users'].astype(int)
        display_df['users_active_week_2'] = display_df['users_active_week_2'].astype(int)
        display_df['two_week_retention_pct'] = display_df['two_week_retention_pct'].round(2)
        
        # Rename columns for better display
        display_df = display_df.rename(columns={
            'launch_phase': 'Launch Phase',
            'total_installed_users': 'Total Users Who Installed',
            'users_active_week_2': 'Active Week 2',
            'two_week_retention_pct': 'Retention Rate (%)'
        })
        
        st.dataframe(display_df, use_container_width=True)
        
        # Display SQL query
        with st.expander("📋 SQL Query", expanded=False):
            st.markdown("**Data Sources:** `tactile-471816.data_analyst_test_local.users`, `tactile-471816.data_analyst_test_local.activity`")
            st.markdown("**SQL Query:**")
            st.code(TWO_WEEK_RETENTION_QUERY, language="sql")
            st.markdown("**Query Explanation:**")
            st.markdown("""
            - `REGEXP_EXTRACT(u.user_id, r'_(\\d+)')` - Extracts numeric ID from user_id string format
            - `SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', u.install_date)` - Safely parses ISO timestamp, returns NULL if invalid
            - `DATE_DIFF(ua.activity_date, ui.install_date, DAY) BETWEEN 14 AND 20` - Checks if user was active in week 2 (days 14-20 after install)
            - `CASE WHEN ui.install_date < '2022-06-01' THEN 'Soft Launch' ELSE 'Official Launch'` - Categorizes users by launch phase
            - `LEFT JOIN` - Includes all users even if they have no activity data
            - `WHERE install_date <= DATE_SUB(CURRENT_DATE(), INTERVAL 21 DAY)` - Only users who had enough time to show week 2 retention
            - `MAX(CASE WHEN ... THEN 1 ELSE 0 END)` - Converts multiple activity records to single retention flag per user
            """)
        
        # AI Analysis
        explanation = explainer.explain_chart("retention_analysis", df, "Two-week retention rates comparing soft launch vs official launch phases")
        render_ai_insights(explanation, explainer)
    else:
        st.warning("No two-week retention data available")
    
    return df if not df.empty else None


def plot_progression_milestones(explainer):
    """Render player progression milestone analysis."""
    # Fetch data
    with st.spinner("Loading progression milestone data..."):
        df = get_bigquery_data(PROGRESSION_MILESTONE_QUERY)
    
    if not df.empty:
        # Data is already aggregated by milestone
        # Format the display dataframe (keep all milestones for table)
        display_df = df.copy()
        display_df['cumulative_avg_days_to_complete'] = display_df['cumulative_avg_days_to_complete'].round(1).astype(str) + ' days'
        
        display_df = display_df.rename(columns={
            'milestone': 'Milestone',
            'num_users_who_played': 'Players Who Played',
            'cumulative_avg_days_to_complete': 'Avg Days to Complete'
        })
        
        # Display summary table (all milestones)
        st.dataframe(display_df, use_container_width=True)
        
        # Plot removed - showing table only
        
        # Display raw data sample and SQL query
        with st.expander("📋 Raw Data Sample & SQL Query", expanded=False):
            st.markdown("**Data Source:** `tactile-471816.data_analyst_test_local.activity`")
            st.markdown("**SQL Query:**")
            st.code(PROGRESSION_MILESTONE_QUERY, language="sql")
            st.markdown("**Query Explanation:**")
            st.markdown("""
            - `MAX(max_level_completed)` - Gets highest level each user ever reached
            - `GENERATE_ARRAY(100, 5000, 100)` - Dynamically creates milestone levels (100, 200, 300, ..., 5000)
            - `CROSS JOIN` - Cartesian product to check every user against every milestone level
            - `CASE WHEN highest_level_reached >= ml.level THEN ... ELSE NULL END` - Conditional logic to mark milestone achievement
            - `COUNT(DISTINCT user_id)` vs `COUNT(milestone_achieved)` - Total users vs users who reached milestone
            - `HAVING COUNT(milestone_achieved) > 0` - Only show milestones at least one user reached
            - Performance optimization: Pre-aggregates by user instead of checking millions of individual activity records
            """)
            st.markdown("**Data Sample:**")
            st.dataframe(df.head(20))
        
        # AI Analysis
        explanation = explainer.explain_chart("progression_milestones", df, "Player progression milestone analysis showing completion times")
        render_ai_insights(explanation, explainer)
    else:
        st.warning("No progression data available")
    
    return df if not df.empty else None