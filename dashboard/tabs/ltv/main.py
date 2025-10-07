"""Lifetime Value (LTV) analytics tab."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.components.insights import render_manual_insights
from dashboard.config.database import get_bigquery_data
from dashboard.utils.ai_explainer import DashboardExplainer

from .data_processing import (
    create_retention_curve_data,
    create_revenue_segmentation,
    create_segment_plot_data,
    project_90_day_ltv_simple,
)
from .manual_insights import RETENTION_RATE_INSIGHTS, REVENUE_SEGMENTATION_INSIGHTS
from .queries import RETENTION_RATE_QUERY, REVENUE_SEGMENTATION_QUERY


def render_ltv_tab():
    """Render the LTV analytics tab."""

    # Initialize explainer
    explainer = DashboardExplainer()

    # Load all data at the beginning
    revenue_df = None
    retention_df = None

    try:
        with st.spinner("Loading data..."):
            revenue_df = get_bigquery_data(REVENUE_SEGMENTATION_QUERY)
            retention_df = get_bigquery_data(RETENTION_RATE_QUERY)
    except Exception as e:
        st.error(f"Error loading data: {e}")

    # Revenue Segmentation Analysis
    with st.container():
        # Create header with question mark popup
        col_header, col_help = st.columns([6, 1])
        with col_header:
            st.markdown(
                "<h3 style='color: #0066cc;'>Revenue Segmentation Analysis</h3>",
                unsafe_allow_html=True,
            )
        with col_help:
            with st.popover("❓"):
                st.markdown("**Spender Quantile Segmentation Explained:**")
                st.markdown(
                    """
                - **Low Spender (25%)**: Bottom 25% of paying users by revenue
                - **Medium Spender (50%)**: 25th-50th percentile of paying users
                - **High Spender (75%)**: 50th-75th percentile of paying users
                - **Premium (90%)**: 75th-90th percentile of paying users
                - **VIP (95%)**: 90th-95th percentile of paying users
                - **Whale (95%+)**: Top 5% of paying users by revenue

                Segments are based on 20-day cumulative revenue quantiles among paying users only.
                """
                )

        try:
            if revenue_df is not None and not revenue_df.empty:
                # Create segmentation table
                segmentation_table = create_revenue_segmentation(revenue_df)

                if not segmentation_table.empty:
                    # Create layout with charts on left and manual insights on right
                    col_charts, col_insights = st.columns([3, 1])

                    with col_charts:
                        # Define segment order without percent signs
                        segment_order = [
                            "Low Spender",
                            "Medium Spender",
                            "High Spender",
                            "Premium",
                            "VIP",
                            "Whale",
                        ]

                        # Add quantile info to segment names for display (without % in segment names)
                        segmentation_display = segmentation_table.copy()
                        segment_mapping = {
                            "Low Spender": "Low Spender",
                            "Medium Spender": "Medium Spender",
                            "High Spender": "High Spender",
                            "Premium": "Premium",
                            "VIP": "VIP",
                            "Whale": "Whale",
                        }
                        segmentation_display["segment_display"] = segmentation_display[
                            "segment"
                        ].map(segment_mapping)

                        # Filter out Non-Payer for the first chart
                        segmentation_display_filtered = segmentation_display[
                            segmentation_display["segment"] != "Non-Payer"
                        ].copy()

                        # Calculate percentages
                        total_users = segmentation_display["num_user"].sum()
                        total_revenue = segmentation_display["ltv_20_day"].sum()

                        segmentation_display["user_pct"] = (
                            segmentation_display["num_user"] / total_users
                        ) * 100
                        segmentation_display["revenue_pct"] = (
                            segmentation_display["ltv_20_day"] / total_revenue
                        ) * 100
                        segmentation_display_filtered["user_pct"] = (
                            segmentation_display_filtered["num_user"] / total_users
                        ) * 100
                        segmentation_display_filtered["revenue_pct"] = (
                            segmentation_display_filtered["ltv_20_day"] / total_revenue
                        ) * 100

                        # Sort by segment order
                        segmentation_display_filtered[
                            "segment_order"
                        ] = segmentation_display_filtered["segment_display"].map(
                            {seg: i for i, seg in enumerate(segment_order)}
                        )
                        segmentation_display_filtered = (
                            segmentation_display_filtered.sort_values("segment_order")
                        )
                        segmentation_display["segment_order"] = segmentation_display[
                            "segment_display"
                        ].map(
                            {
                                seg: i
                                for i, seg in enumerate(["Non-Payer"] + segment_order)
                            }
                        )
                        segmentation_display = segmentation_display.sort_values(
                            "segment_order"
                        )

                        # Add importance weight for color scaling (higher value segments get darker colors)
                        importance_mapping = {
                            "Low Spender": 1,
                            "Medium Spender": 2,
                            "High Spender": 3,
                            "Premium": 4,
                            "VIP": 5,
                            "Whale": 6,
                        }
                        segmentation_display_filtered[
                            "importance"
                        ] = segmentation_display_filtered["segment_display"].map(
                            importance_mapping
                        )

                        # Create side-by-side charts
                        chart_col1, chart_col2 = st.columns(2)

                        with chart_col1:
                            # Chart 1: Number of users by segment (%) - excluding Non-Payer
                            fig1 = px.bar(
                                segmentation_display_filtered,
                                x="segment_display",
                                y="user_pct",
                                title="Number of Payers (IAP + AD) Users / DAU by Segment (%)",
                                labels={
                                    "segment_display": "",
                                    "user_pct": "Percentage of Users (%)",
                                },
                                color="importance",
                                color_continuous_scale=[
                                    [0, "#C6DBEF"],
                                    [0.2, "#9ECAE1"],
                                    [0.4, "#6BAED6"],
                                    [0.6, "#4292C6"],
                                    [0.8, "#2171B5"],
                                    [1, "#08519C"],
                                ],
                            )
                            # Add value labels on top of bars
                            fig1.update_traces(
                                texttemplate="%{y:.1f}%", textposition="outside"
                            )
                            fig1.update_layout(showlegend=False, xaxis_tickangle=-45)
                            fig1.update_coloraxes(showscale=False)
                            st.plotly_chart(fig1, use_container_width=True)

                        with chart_col2:
                            # Chart 2: Revenue by segment (%) - all segments
                            fig2 = px.bar(
                                segmentation_display,
                                x="segment_display",
                                y="revenue_pct",
                                title="Revenue (20 Days) by Segment (%)",
                                labels={
                                    "segment_display": "",
                                    "revenue_pct": "Percentage of Revenue (%)",
                                },
                                color="revenue_pct",
                                color_continuous_scale="Greens",
                            )
                            # Add value labels on top of bars
                            fig2.update_traces(
                                texttemplate="%{y:.1f}%", textposition="outside"
                            )
                            fig2.update_layout(showlegend=False, xaxis_tickangle=-45)
                            fig2.update_coloraxes(showscale=False)
                            st.plotly_chart(fig2, use_container_width=True)

                    with col_insights:
                        st.markdown("**Key Notes**")
                        render_manual_insights(
                            REVENUE_SEGMENTATION_INSIGHTS,
                            height=400,
                            key_suffix="segmentation",
                        )
                else:
                    st.warning("No segmentation data available")

            else:
                st.info("Revenue segmentation data will be displayed here")
                st.write("Revenue segment analysis will be added here")

        except Exception as e:
            st.error(f"Error loading revenue segmentation data: {e}")
            st.info("Revenue segmentation data will be displayed here")
            st.write("Revenue segment analysis will be added here")

    # Retention Rate Analysis
    with st.container():
        st.markdown(
            "<h3 style='color: #0066cc;'>Retention Rate Analysis</h3>",
            unsafe_allow_html=True,
        )

        try:
            if retention_df is not None and not retention_df.empty:
                # Create retention curve data
                retention_curve_data = create_retention_curve_data(retention_df)

                if not retention_curve_data.empty:
                    # Create layout with plot on left and manual insights on right
                    col_plot, col_insights = st.columns([3, 1])

                    with col_plot:
                        # Plot: Retention rate curve with actual and projected data
                        fig = px.line(
                            retention_curve_data,
                            x="day",
                            y="retention_rate",
                            color="type",
                            title="Actual vs Projected User Retention Rate (Weibull Model - 90 Days)",
                            labels={
                                "day": "Days Since Install",
                                "retention_rate": "Retention Rate (%)",
                                "type": "Data Type",
                            },
                            markers=True,
                        )

                        # Update styling for different line types
                        fig.update_traces(
                            line=dict(width=3),
                            marker=dict(size=6),
                            selector=dict(name="Actual"),
                        )

                        fig.update_traces(
                            line=dict(width=2, dash="dash"),
                            marker=dict(size=4),
                            selector=dict(name="Projected"),
                        )

                        fig.update_layout(
                            xaxis_title="Days Since Install",
                            yaxis_title="Retention Rate (%)",
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1,
                            ),
                        )

                        st.plotly_chart(fig, use_container_width=True)

                    with col_insights:
                        st.markdown("**Key Notes**")
                        render_manual_insights(
                            RETENTION_RATE_INSIGHTS, height=300, key_suffix="retention"
                        )

                    # Expandable Retention Rate Table
                    with st.expander(
                        "Retention Rate Data - Actual vs Projected", expanded=False
                    ):
                        st.markdown(
                            """
                            **How is the projected retention rate calculated?**

                            - **Projection method:**
                                1. Fit a Weibull curve to the actual retention data from Days 1-20.
                                2. Use the fitted curve to estimate retention for Days 21-90.
                                3. Apply a conservative decay adjustment for days beyond 20 (an extra 15% decay per 10 days) to avoid overestimating long-term retention.


                            - **Why Weibull?**
                                1. The Weibull model is commonly used for survival analysis. In game analytics, it can flexibly fit both the sharp early drop and the slower long-term decline seen in commonly real user data. This makes projections more realistic than a simple straight-line or exponential fit.
                                2. [Weibull distribution: Wikipedia](https://en.wikipedia.org/wiki/Weibull_distribution)
                            """
                        )
                        # Create table view of the data
                        table_data = retention_curve_data.pivot(
                            index="day", columns="type", values="retention_rate"
                        ).reset_index()

                        # Clean up column names and fill NaN values
                        if (
                            "Actual" in table_data.columns
                            and "Projected" in table_data.columns
                        ):
                            table_data["Actual"] = table_data["Actual"].fillna("")
                            table_data = table_data.rename(
                                columns={
                                    "day": "Day",
                                    "Actual": "Actual Retention (%)",
                                    "Projected": "Projected Retention (%)",
                                }
                            )

                            # Format the projected column to 2 decimal places
                            table_data["Projected Retention (%)"] = table_data[
                                "Projected Retention (%)"
                            ].round(2)

                            # Display the table
                            st.dataframe(
                                table_data, use_container_width=True, hide_index=True
                            )
                        else:
                            # Fallback if pivot fails
                            st.dataframe(
                                retention_curve_data,
                                use_container_width=True,
                                hide_index=True,
                            )

                    # 90-Day LTV Projection Table
                    st.markdown("### :blue[90-Day LTV Projection by Segment]")

                    st.markdown(
                        """
                    **How 90-day projection is calculated:**
                    1. Fit Weibull model to retention data (days 1-20)
                    2. Project retention rates to day 90
                    3. Calculate daily revenue per segment
                    4. Sum projected revenues: Day 20 LTV + (avg daily revenue × retention day 21) + (avg daily revenue × retention day 22) + ... + (avg daily revenue × retention day 90)
                    """
                    )

                    # Create 90-day projection using segmentation, retention and raw revenue data
                    projection_table = project_90_day_ltv_simple(
                        segmentation_table, retention_df, revenue_df
                    )

                    # Display simplified table with only requested columns
                    display_projection_cols = [
                        "segment",
                        "num_user",
                        "ltv_20_day",
                        "avg_daily_revenue_per_user",
                        "avg_ltv_20_day_per_user",
                        "projected_avg_90_day_per_user",
                    ]

                    # Format the projection table for better display
                    projection_display = projection_table[
                        display_projection_cols
                    ].copy()
                    projection_display.columns = [
                        "Segment",
                        "Number of Users",
                        "Total LTV (20 Days)",
                        "Avg Daily Revenue per User",
                        "Avg LTV per User (20 Days)",
                        "Projected Avg LTV per User (90 Days)",
                    ]

                    st.dataframe(
                        projection_display, use_container_width=True, hide_index=True
                    )
                else:
                    st.warning("No retention curve data available")

            else:
                st.info("Retention rate data will be displayed here")
                st.write("Retention curve analysis will be added here")

        except Exception as e:
            st.error(f"Error loading retention rate data: {e}")
            st.info("Retention rate data will be displayed here")
            st.write("Retention curve analysis will be added here")

    # LTV 1-20 Day by Segment Table (moved to bottom and made expandable)
    if revenue_df is not None and not revenue_df.empty:
        segmentation_table = create_revenue_segmentation(revenue_df)
        if not segmentation_table.empty:
            with st.expander(
                "LTV 1-20 Day by Segment - Detailed Table", expanded=False
            ):
                st.markdown(
                    "**Complete LTV breakdown by segment showing daily progression from day 1 to day 20**"
                )

                # Format the table for better display
                display_cols = ["segment", "num_user", "ltv_20_day"]

                # Add avg LTV columns (from day 20 down to day 1)
                for i in range(20, 0, -1):
                    col_name = f"avg_ltv_{i}_day_per_user"
                    if col_name in segmentation_table.columns:
                        display_cols.append(col_name)

                # Add percentage columns if they exist
                if "pct_user" in segmentation_table.columns:
                    display_cols.append("pct_user")
                if "pct_ltv_20_day_per_segment" in segmentation_table.columns:
                    display_cols.append("pct_ltv_20_day_per_segment")

                # Display the table
                st.dataframe(
                    segmentation_table[display_cols],
                    use_container_width=True,
                    hide_index=True,
                )

    # SQL Query & Data Sample (moved to bottom)
    with st.expander("SQL Query & Data Sample", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Revenue LTV Data Generation:**")
            st.markdown(
                "**Data Source:** `game-analytics.data.users_view`, `game-analytics.data.revenue_view`"
            )
            st.markdown("**SQL Query:**")
            ltv_query = """WITH user_installs AS (
  SELECT
    user_id,
    DATE(install_date) AS install_date
  FROM `game-analytics.data.users_view`
  WHERE DATE(install_date) >= '2022-06-06'
    AND install_date IS NOT NULL
),

revenue_20 AS (
  SELECT
    ui.user_id,
    r.transaction_value,
    DATE_DIFF(DATE(r.date), ui.install_date, DAY) AS day_offset
  FROM user_installs ui
  LEFT JOIN `game-analytics.data.revenue_view` r
    ON ui.user_id = r.user_id
   AND DATE_DIFF(DATE(r.date), ui.install_date, DAY) BETWEEN 0 AND 19
)

SELECT
  user_id,
  SUM(IF(day_offset = 0, transaction_value, 0)) AS revenue_day_1,
  SUM(IF(day_offset = 1, transaction_value, 0)) AS revenue_day_2,
  SUM(IF(day_offset = 2, transaction_value, 0)) AS revenue_day_3,
  SUM(IF(day_offset = 3, transaction_value, 0)) AS revenue_day_4,
  SUM(IF(day_offset = 4, transaction_value, 0)) AS revenue_day_5,
  SUM(IF(day_offset = 5, transaction_value, 0)) AS revenue_day_6,
  SUM(IF(day_offset = 6, transaction_value, 0)) AS revenue_day_7,
  SUM(IF(day_offset = 7, transaction_value, 0)) AS revenue_day_8,
  SUM(IF(day_offset = 8, transaction_value, 0)) AS revenue_day_9,
  SUM(IF(day_offset = 9, transaction_value, 0)) AS revenue_day_10,
  SUM(IF(day_offset = 10, transaction_value, 0)) AS revenue_day_11,
  SUM(IF(day_offset = 11, transaction_value, 0)) AS revenue_day_12,
  SUM(IF(day_offset = 12, transaction_value, 0)) AS revenue_day_13,
  SUM(IF(day_offset = 13, transaction_value, 0)) AS revenue_day_14,
  SUM(IF(day_offset = 14, transaction_value, 0)) AS revenue_day_15,
  SUM(IF(day_offset = 15, transaction_value, 0)) AS revenue_day_16,
  SUM(IF(day_offset = 16, transaction_value, 0)) AS revenue_day_17,
  SUM(IF(day_offset = 17, transaction_value, 0)) AS revenue_day_18,
  SUM(IF(day_offset = 18, transaction_value, 0)) AS revenue_day_19,
  SUM(IF(day_offset = 19, transaction_value, 0)) AS revenue_day_20
FROM revenue_20
GROUP BY user_id
ORDER BY user_id;"""
            st.code(ltv_query, language="sql")

        with col2:
            st.markdown("**Query Explanation:**")
            st.markdown(
                """
            - **user_installs CTE:** Gets user install dates from the users_view table, filtering for launch period (2022-06-06+)
            - **revenue_20 CTE:** Joins revenue data with install dates, calculating day offset for each transaction within 20 days
            - **Main Query:** Pivots revenue by day using conditional SUM statements to create columns for each day (1-20)
            - **DATE_DIFF():** Calculates days between transaction date and install date to determine day offset
            - **IF() statements:** Conditionally sum revenue for each specific day to create day-wise LTV columns
            """
            )

            st.markdown("**Sample Data Structure:**")
            sample_data = pd.DataFrame(
                {
                    "user_id": ["12345", "67890", "11111"],
                    "revenue_day_1": [0.00, 4.99, 0.00],
                    "revenue_day_2": [2.99, 0.00, 0.00],
                    "revenue_day_3": [0.00, 9.99, 1.99],
                    "revenue_day_4": [0.00, 0.00, 0.00],
                    "revenue_day_5": [1.99, 0.00, 4.99],
                }
            )
            st.dataframe(sample_data, use_container_width=True, hide_index=True)
