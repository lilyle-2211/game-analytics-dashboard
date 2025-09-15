"""AI-powered chart explanation using OpenAI."""
import os
import sys

import streamlit as st
from openai import OpenAI


class DashboardExplainer:
    """AI-powered explanation system for dashboard insights."""

    def __init__(self):
        self.ai_enabled = self._setup_openai()
        self.rate_limit_exceeded = False

    def _get_ai_enabled_setting(self):
        """Get AI enabled setting from command line args, session state, or secrets."""
        # Check command line arguments first
        if "--enable-ai" in sys.argv:
            return True
        elif "--disable-ai" in sys.argv:
            return False

        # Check session state (dashboard toggle)
        if "ai_enabled_override" in st.session_state:
            return st.session_state.ai_enabled_override

        # Fall back to secrets.toml
        if hasattr(st, "secrets") and "enable_ai_calls" in st.secrets:
            return st.secrets["enable_ai_calls"]

        # Default to False (testing mode)
        return False

    def _setup_openai(self):
        """Setup OpenAI API."""
        try:
            # Check if AI calls are enabled (check session state and command line args)
            enable_ai = self._get_ai_enabled_setting()
            print(f"AI calls enabled: {enable_ai}")

            if not enable_ai:
                print(
                    "AI calls disabled - use command line --enable-ai or dashboard toggle to enable"
                )
                return False

            api_key = None
            if hasattr(st, "secrets") and "openai_api_key" in st.secrets:
                api_key = st.secrets["openai_api_key"]
                print(f"Found OpenAI API key in secrets: {api_key[:10]}...")
            elif "OPENAI_API_KEY" in os.environ:
                api_key = os.environ["OPENAI_API_KEY"]
                print(f"Found OpenAI API key in env: {api_key[:10]}...")

            if api_key:
                self.client = OpenAI(api_key=api_key)
                # Test the API key with a simple request
                test_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10,
                )
                print("OpenAI API test successful")
                return True
            else:
                print("No OpenAI API key found")
                return False
        except Exception as e:
            print(f"OpenAI setup error: {e}")
            if (
                "429" in str(e)
                or "quota" in str(e).lower()
                or "rate limit" in str(e).lower()
            ):
                self.rate_limit_exceeded = True
            return False

    def explain_chart(self, chart_type, dataframe, description):
        """Generate AI explanation for chart data using full dataframe analysis."""
        if not self.ai_enabled:
            return None

        try:
            # Convert full dataframe to string representation for LLM analysis
            if dataframe is not None and not dataframe.empty:
                # Get basic info about the dataframe
                data_info = f"DataFrame shape: {dataframe.shape}\n"
                data_info += f"Columns: {list(dataframe.columns)}\n"

                # Include meaningful sample of data for LLM analysis
                if len(dataframe) > 200:
                    # For very large datasets, show substantial sample with patterns
                    data_sample = (
                        f"First 50 rows:\n{dataframe.head(50).to_string()}\n\n"
                    )
                    data_sample += (
                        f"Last 20 rows:\n{dataframe.tail(20).to_string()}\n\n"
                    )
                    data_sample += (
                        f"Summary statistics:\n{dataframe.describe().to_string()}\n\n"
                    )
                    # Add some middle sampling to capture patterns
                    if len(dataframe) > 100:
                        mid_start = len(dataframe) // 2 - 10
                        mid_end = len(dataframe) // 2 + 10
                        data_sample += f"Middle sample (rows {mid_start}-{mid_end}):\n{dataframe.iloc[mid_start:mid_end].to_string()}"
                    data_representation = data_info + data_sample
                elif len(dataframe) > 50:
                    # For medium datasets, show first 100 rows
                    data_representation = (
                        data_info
                        + f"Data sample (first 100 rows):\n{dataframe.head(100).to_string()}\n\nSummary statistics:\n{dataframe.describe().to_string()}"
                    )
                else:
                    # For smaller datasets, show all data
                    data_representation = (
                        data_info + f"Full data:\n{dataframe.to_string()}"
                    )
            else:
                data_representation = "No data available"

            prompt = f"""
            You are an expert game analytics advisor. Analyze this {chart_type} data and provide specific, data-driven insights:

            Chart Description: {description}

            Data Analysis:
            {data_representation}

            Based ONLY on the specific numbers and patterns in the data above:
            1. Identify 2-3 key insights with specific numbers/percentages/trends from the data
            2. Explain what these numbers mean for game performance and player behavior

            IMPORTANT: Reference actual values, dates, and specific trends you see in the data. Don't give generic advice - focus on what THIS specific data shows. Keep response under 150 words but include concrete numbers.
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.5,
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            if (
                "429" in str(e)
                or "quota" in str(e).lower()
                or "rate limit" in str(e).lower()
            ):
                self.rate_limit_exceeded = True
            return None

    def analyze_distribution_subplot(self, dataframe, column_name, description):
        """Analyze a specific distribution column from a dataframe."""
        if not self.ai_enabled:
            return None

        try:
            # Create distribution data for the specific column
            distribution_data = (
                dataframe.groupby(column_name)["num_player"]
                .agg(["sum", "count"])
                .reset_index()
            )
            distribution_data = distribution_data.sort_values("sum", ascending=False)
            distribution_data["percentage"] = (
                distribution_data["sum"] / distribution_data["sum"].sum() * 100
            ).round(2)

            # Format the distribution data
            data_representation = f"Distribution of {column_name}:\n"
            data_representation += (
                f"Total players: {distribution_data['sum'].sum():,}\n\n"
            )
            data_representation += distribution_data.to_string(index=False)

            prompt = f"""
            Analyze this {column_name} distribution data for US players:

            Context: {description}

            Data:
            {data_representation}

            Provide 1-2 specific insights about this {column_name} distribution, focusing on:
            1. The actual numbers and percentages you see
            2. What the distribution pattern reveals about the player base

            Keep response brief (under 80 words) and reference specific values from the data.
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.5,
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error in subplot analysis: {e}")
            if (
                "429" in str(e)
                or "quota" in str(e).lower()
                or "rate limit" in str(e).lower()
            ):
                self.rate_limit_exceeded = True
            return None
