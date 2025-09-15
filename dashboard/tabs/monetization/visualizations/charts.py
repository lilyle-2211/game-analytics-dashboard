"""Visualization functions for the monetization tab."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.config.database import get_bigquery_data
from dashboard.utils.ai_explainer import DashboardExplainer
from dashboard.components.insights import render_ai_insights
from ..queries import REVENUE_BY_SOURCE_QUERY, ANOMALY_TRANSACTIONS_QUERY


def render_iap_metrics(df, anomaly_df):
    """Render IAP revenue metrics."""
    # Calculate anomaly metrics dynamically
    if not anomaly_df.empty and 'revenue_type' in anomaly_df.columns:
        anomaly_iap = anomaly_df[anomaly_df['revenue_type'] == 'iap']['transaction_value'].sum()
        anomaly_count = len(anomaly_df[anomaly_df['revenue_type'] == 'iap'])
    else:
        anomaly_iap = 0
        anomaly_count = 0
    
    # Calculate overall totals (add back the excluded anomaly for total display)
    total_iap = df['iap_revenue'].sum() + anomaly_iap
    total_ad = df['ad_revenue'].sum()
    total_rev = total_iap + total_ad
    
    # Track the anomaly transaction that was excluded from calculations
    adjusted_iap = total_iap - anomaly_iap  # IAP revenue without the anomaly
    
    # Metrics column
    st.metric("Total IAP Revenue", f"${total_iap:,.2f}")
    
    # Only show adjusted revenue if there are anomalies
    if anomaly_count > 0:
        st.metric(
            "Adjusted IAP Revenue", 
            f"${adjusted_iap:,.2f}",
            delta=f"-${anomaly_iap:,.2f}",
            delta_color="off"
        )
    
    st.metric("Percent of Total", f"{total_iap/total_rev:.1%}")
    
    return total_iap, anomaly_iap, anomaly_count


def plot_iap_chart(df, anomaly_df, explainer):
    """Render IAP revenue chart with AI analysis."""
    # Create line chart for IAP revenue including anomaly for visual evidence
    chart_df = df.copy()
    
    # Add back anomaly transactions for chart visualization
    if not anomaly_df.empty and 'revenue_type' in anomaly_df.columns:
        for _, anomaly_row in anomaly_df[anomaly_df['revenue_type'] == 'iap'].iterrows():
            anomaly_date = pd.to_datetime(anomaly_row['eventDate'])
            anomaly_amount = anomaly_row['transaction_value']
            
            if anomaly_date in chart_df['revenue_date'].values:
                # Add the anomaly amount back to that date
                mask = chart_df['revenue_date'] == anomaly_date
                chart_df.loc[mask, 'iap_revenue'] += anomaly_amount
            else:
                # If the date doesn't exist, add a new row for the anomaly
                new_row = chart_df.iloc[0].copy()  # Copy structure from first row
                new_row['revenue_date'] = anomaly_date
                new_row['iap_revenue'] = anomaly_amount
                new_row['ad_revenue'] = 0
                new_row['total_revenue'] = anomaly_amount
                chart_df = pd.concat([chart_df, new_row.to_frame().T], ignore_index=True)
                chart_df = chart_df.sort_values('revenue_date')
    
    fig = px.line(
        chart_df, 
        x="revenue_date", 
        y="iap_revenue",
        markers=True,
        labels={
            "revenue_date": "Date", 
            "iap_revenue": "IAP Revenue ($)"
        },
        title="IAP Revenue (including anomaly transaction)"
    )
    
    # Highlight all anomaly points
    if not anomaly_df.empty and 'revenue_type' in anomaly_df.columns:
        anomaly_dates = []
        anomaly_values = []
        for _, anomaly_row in anomaly_df[anomaly_df['revenue_type'] == 'iap'].iterrows():
            anomaly_date = pd.to_datetime(anomaly_row['eventDate'])
            if anomaly_date in chart_df['revenue_date'].values:
                anomaly_value = chart_df[chart_df['revenue_date'] == anomaly_date]['iap_revenue'].iloc[0]
                anomaly_dates.append(anomaly_date)
                anomaly_values.append(anomaly_value)
        
        if anomaly_dates:
            fig.add_scatter(
                x=anomaly_dates,
                y=anomaly_values,
                mode='markers',
                marker=dict(size=12, color='red', symbol='diamond'),
                name='Anomaly Transaction',
                hovertemplate='Anomaly: $%{y:,.2f}<extra></extra>',
                showlegend=False
            )
    
    fig.update_layout(height=350, margin=dict(t=30, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)
    
    # AI Analysis
    explanation = explainer.explain_chart("iap_revenue", df, "In-app purchase revenue analysis showing daily IAP performance and trends")
    render_ai_insights(explanation, explainer)
    
    return chart_df


def render_ad_metrics(df):
    """Render ad revenue metrics."""
    total_ad = df['ad_revenue'].sum()
    total_iap = df['iap_revenue'].sum()
    total_rev = total_iap + total_ad
    
    # Metrics
    st.metric("Total Ad Revenue", f"${total_ad:,.2f}")
    st.metric("Percent of Total", f"{total_ad/total_rev:.1%}")
    
    return total_ad, total_rev


def plot_ad_chart(df, explainer):
    """Render ad revenue chart with AI analysis."""
    # Create line chart for ad revenue
    fig = px.line(
        df, 
        x="revenue_date", 
        y="ad_revenue",
        markers=True,
        labels={
            "revenue_date": "Date", 
            "ad_revenue": "Ad Revenue ($)"
        }
    )
    fig.update_layout(height=350, margin=dict(t=10, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)
    
    # AI Analysis
    explanation = explainer.explain_chart("ad_revenue", df, "Advertisement revenue analysis showing daily ad performance and user engagement patterns")
    render_ai_insights(explanation, explainer)
    
    return df


def plot_revenue_per_user_metrics(df, anomaly_df):
    """Render revenue per user metrics analysis."""
    # Calculate anomaly metrics
    if not anomaly_df.empty and 'revenue_type' in anomaly_df.columns:
        anomaly_iap = anomaly_df[anomaly_df['revenue_type'] == 'iap']['transaction_value'].sum()
        anomaly_count = len(anomaly_df[anomaly_df['revenue_type'] == 'iap'])
    else:
        anomaly_iap = 0
        anomaly_count = 0
    
    # Calculate totals
    total_iap = df['iap_revenue'].sum() + anomaly_iap
    total_ad = df['ad_revenue'].sum()
    total_rev = total_iap + total_ad
    
    # Get unique user counts from REVENUE_BY_SOURCE_QUERY data (same value in all rows)
    unique_active_users = df['total_unique_active_users'].iloc[0]
    unique_iap_users = df['total_unique_paying_users_iap'].iloc[0]  # IAP-only users
    unique_iap_ad_users = df['total_unique_paying_users_all'].iloc[0]  # All revenue users (IAP + AD)
    
    # Calculate IAP user conversion rate (IAP users / total active users)
    iap_conversion_rate = unique_iap_users / unique_active_users if unique_active_users > 0 else 0
    
    # Calculate Average Revenue Per User (ARPU) across all days
    # ARPU = Total revenue / Total active users in the period
    avg_arpu = df['total_arpdau'].mean()
    
    # Create summary metrics in a row - exactly as requested
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("Unique IAP Users", f"{unique_iap_users:,}")
    with metric_cols[1]:
        st.metric("Unique IAP + AD Users", f"{unique_iap_ad_users:,}")
    with metric_cols[2]:
        st.metric("% IAP Users/DAU", f"{iap_conversion_rate:.2%}")
    with metric_cols[3]:
        st.metric("Average Revenue Per User (ARPU)", f"${avg_arpu:.4f}")

    
    # Table with daily data - simplified to show only requested columns
    st.markdown("#### US Revenue Per User Metrics")
    
    # Prepare the table data
    table_data = df.copy()
    table_data['revenue_date'] = table_data['revenue_date'].dt.date
    
    # Select only the requested columns: date | DAU | Revenue (iap + ad) | ARPDAU
    table_columns = [
        'revenue_date', 
        'DAU',
        'total_revenue',
        'total_arpdau'
    ]
    
    # Create display dataframe with only requested columns
    display_df = table_data[table_columns].rename(columns={
        'revenue_date': 'Date',
        'DAU': 'DAU',
        'total_revenue': 'Revenue (IAP + AD)',
        'total_arpdau': 'ARPDAU'
    })
    
    # Format numeric columns
    display_df['Revenue (IAP + AD)'] = display_df['Revenue (IAP + AD)'].map('${:,.2f}'.format)
    display_df['ARPDAU'] = display_df['ARPDAU'].map('${:,.4f}'.format)
    display_df['DAU'] = display_df['DAU'].map('{:,}'.format)
    
    # Display the table
    st.dataframe(display_df, use_container_width=True)
    
    return table_data


def display_raw_data_section(df, anomaly_df):
    """Display raw data and SQL query section."""
    with st.expander("📋 Raw Data & SQL Query", expanded=False):
        st.markdown("**Data Source:** `tactile-471816.data_analyst_test_local.revenues`")
        st.markdown("**SQL Query:**")
        st.code(REVENUE_BY_SOURCE_QUERY, language="sql")
        st.dataframe(df.head(10))
        
        # Add notes after the raw data section
        st.markdown("---")
        st.markdown("**📝 Important Notes:**")
        
        st.markdown("""
        <div style="font-size: 0.9em; color: #666; margin-bottom: 10px;">
        • Paying users are defined as users who made in-app purchases (IAP), not users who generated ad revenue.
        </div>
        """, unsafe_allow_html=True)
        
        # Calculate anomaly info
        if not anomaly_df.empty and 'revenue_type' in anomaly_df.columns:
            anomaly_iap = anomaly_df[anomaly_df['revenue_type'] == 'iap']['transaction_value'].sum()
            anomaly_count = len(anomaly_df[anomaly_df['revenue_type'] == 'iap'])
            
            if anomaly_count > 0:
                st.markdown(f"""
                <div style="font-size: 0.9em; color: #666; margin-bottom: 10px;">
                • {anomaly_count} anomaly transactions (over 100x average value, total ${anomaly_iap:,.2f}) are excluded 
                from user metrics calculations to avoid skewing the averages.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="font-size: 0.9em; color: #666; margin-bottom: 10px;">
                • Transactions ≥ $10,000 are excluded from user metrics calculations to avoid skewing averages.
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="font-size: 0.9em; color: #666; margin-bottom: 10px;">
            • Transactions ≥ $10,000 are excluded from user metrics calculations to avoid skewing averages.
            </div>
            """, unsafe_allow_html=True)