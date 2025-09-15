"""Visualization functions for the acquisition tab."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from dashboard.components.insights import render_ai_insights
from dashboard.utils.ai_explainer import DashboardExplainer


def plot_timeseries(df_clean, explainer):
    """Render player acquisition time series analysis."""
    timeseries_data = df_clean.groupby("install_date")["num_player"].sum().reset_index()

    # Assign regions for visualization
    def assign_region(date):
        month = date.month
        if month < 4:
            return "Canada"
        elif month >= 6:
            return "US"
        else:
            return "Other"

    timeseries_data["region"] = timeseries_data["install_date"].apply(assign_region)

    # Create plot
    fig = px.bar(
        timeseries_data,
        x="install_date",
        y="num_player",
        color="region",
        color_discrete_map={"Canada": "red", "US": "blue", "Other": "gray"},
        title="",
    )

    fig.update_layout(
        xaxis_title="Install Date",
        yaxis_title="Number of Players",
        xaxis_tickangle=-45,
        height=400,
    )

    st.plotly_chart(fig, use_container_width=True)

    # AI Analysis
    explanation = explainer.explain_chart(
        "timeseries",
        timeseries_data,
        "Player acquisition by launch phase showing regional launch strategy",
    )
    render_ai_insights(explanation, explainer)


def plot_weekly_patterns(df_clean, explainer):
    """Render weekly patterns analysis."""
    df_us = df_clean[df_clean["country"] == "US"].copy()
    df_us = df_us[df_us["install_date"].dt.month >= 6]  # June onward

    if df_us.empty:
        st.write("No US data available for weekly analysis")
        return False

    df_us["day_of_week"] = df_us["install_date"].dt.day_name()
    df_us["week_start"] = df_us["install_date"] - pd.to_timedelta(
        df_us["install_date"].dt.weekday, unit="d"
    )
    df_us["week_label"] = df_us["week_start"].dt.strftime("%Y-%m-%d")

    # Exclude specific week
    df_us = df_us[df_us["week_label"] != "2022-06-27"]

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    df_us["day_of_week"] = pd.Categorical(
        df_us["day_of_week"], categories=weekday_order, ordered=True
    )

    weekly_summary = (
        df_us.groupby(["week_label", "day_of_week"])["num_player"].sum().reset_index()
    )

    # Plot
    fig = px.line(
        weekly_summary,
        x="day_of_week",
        y="num_player",
        color="week_label",
        markers=True,
        title="",
    )

    fig.update_layout(
        xaxis_title="Day of Week",
        yaxis_title="Number of Players",
        legend_title="Week Starting",
        height=400,
    )

    st.plotly_chart(fig, use_container_width=True)

    # AI Analysis - analyze trends and patterns from the weekly summary data
    try:
        # Pass the weekly_summary data that shows week-by-week patterns for trend analysis
        # This preserves the weekly breakdown so AI can identify trends like "Monday shows upward trend"
        explanation = explainer.explain_chart(
            "weekly_pattern",
            weekly_summary,
            "US player acquisition weekly patterns showing trends by day of week across different weeks",
        )
        render_ai_insights(explanation, explainer)
    except Exception as e:
        # Log the error and show a user-friendly message
        print(f"Error generating AI insights for weekly patterns: {str(e)}")
        error_message = "⚠️ Configure OpenAI API key in .streamlit/secrets.toml to enable AI insights"
        render_ai_insights(None, explainer, error_message=error_message)

    return True


def plot_demographics(df_clean, explainer):
    """Render demographics distribution analysis."""
    df_us_dist = df_clean[df_clean["country"] == "US"].copy()

    if df_us_dist.empty:
        st.write("No distribution data available")
        return False

    def prepare_data(column, sort_by_value=True, custom_order=None):
        data = df_us_dist.groupby(column)["num_player"].sum().reset_index()
        if custom_order:
            data[column] = pd.Categorical(
                data[column], categories=custom_order, ordered=True
            )
            data = data.sort_values(column)
        elif sort_by_value:
            data = data.sort_values("num_player", ascending=False)
        else:
            data = data.sort_values(column)
        return data

    datasets = {
        "Platform": prepare_data("platform"),
        "Gender": prepare_data("gender"),
        "Channel Type": prepare_data("channel_type"),
        "Age Group": prepare_data(
            "age_group",
            sort_by_value=False,
            custom_order=["<=30", "31-40", "41-50", "51-60", "60+", "unknown"],
        ),
    }

    # Plot
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Platform Distribution",
            "Gender Distribution",
            "Channel Type Distribution",
            "Age Group Distribution",
        ),
        specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "bar"}, {"type": "bar"}]],
    )

    data_list = list(datasets.values())

    fig.add_trace(
        go.Bar(x=data_list[0]["platform"], y=data_list[0]["num_player"]), row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=data_list[1]["gender"], y=data_list[1]["num_player"]), row=1, col=2
    )
    fig.add_trace(
        go.Bar(x=data_list[2]["channel_type"], y=data_list[2]["num_player"]),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Bar(x=data_list[3]["age_group"], y=data_list[3]["num_player"]), row=2, col=2
    )

    fig.update_layout(height=600, showlegend=False, title_text="")

    st.plotly_chart(fig, use_container_width=True)

    # AI Analysis - analyze each subplot individually
    platform_explanation = explainer.analyze_distribution_subplot(
        df_us_dist, "platform", "Mobile platform distribution for US players"
    )
    gender_explanation = explainer.analyze_distribution_subplot(
        df_us_dist, "gender", "Gender distribution for US players"
    )
    channel_explanation = explainer.analyze_distribution_subplot(
        df_us_dist, "channel_type", "Acquisition channel distribution for US players"
    )
    age_explanation = explainer.analyze_distribution_subplot(
        df_us_dist, "age_group", "Age group distribution for US players"
    )

    if any(
        [platform_explanation, gender_explanation, channel_explanation, age_explanation]
    ):
        with st.expander("🤖 AI Analysis", expanded=False):
            if platform_explanation:
                st.success(f"**Platform:** {platform_explanation}")
            if gender_explanation:
                st.success(f"**Gender:** {gender_explanation}")
            if channel_explanation:
                st.success(f"**Channel Type:** {channel_explanation}")
            if age_explanation:
                st.success(f"**Age Groups:** {age_explanation}")
    else:
        render_ai_insights(None, explainer)

    return True
