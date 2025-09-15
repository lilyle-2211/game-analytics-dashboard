"""BigQuery database configuration and client setup."""
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import json
import os


# CSV file mapping for different queries
CSV_FILE_MAPPING = {
    # Engagement queries
    "DAILY_ENGAGEMENT_QUERY": "data/daily_engagement.csv",
    "DAILY_RETURN_RATE_QUERY": "data/daily_return_rate.csv", 
    "TWO_WEEK_RETENTION_QUERY": "data/two_week_retention.csv",
    "PROGRESSION_MILESTONE_QUERY": "data/progression_milestone.csv",
    
    # LTV queries
    "REVENUE_SEGMENTATION_QUERY": "data/revenue_segmentation.csv",
    "RETENTION_RATE_QUERY": "data/retention_rate.csv",
    
    # Monetization queries
    "REVENUE_BY_SOURCE_QUERY": "data/revenue_by_source.csv",
    "ANOMALY_TRANSACTIONS_QUERY": "data/anomaly_transactions.csv",
    
    # Acquisition queries
    "PLAYER_DISTRIBUTION_QUERY": "data/player_distribution.csv",
}


@st.cache_resource
def get_bigquery_client():
    """Get BigQuery client with multiple authentication methods."""
    try:
        # Method 1: Check if running on Streamlit Community Cloud with secrets
        if hasattr(st, 'secrets') and "GOOGLE_CLOUD_CREDENTIALS" in st.secrets:
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["GOOGLE_CLOUD_CREDENTIALS"]
            )
            return bigquery.Client(
                credentials=credentials,
                project=st.secrets["GOOGLE_CLOUD_CREDENTIALS"]["project_id"]
            )
        
        # Method 2: Try Application Default Credentials (gcloud auth)
        try:
            return bigquery.Client(project="tactile-471816")
        except Exception:
            pass
            
        # Method 3: Check for local service account file
        if os.path.exists("service-account-key.json"):
            credentials = service_account.Credentials.from_service_account_file(
                "service-account-key.json"
            )
            return bigquery.Client(credentials=credentials, project="tactile-471816")
        
        return None
        
    except Exception as e:
        return None


def identify_query_type(query):
    """Identify which CSV file to use based on the query content."""
    query_lower = query.lower().strip()
    
    # Check for specific table patterns or query characteristics
    if "daily_active_users" in query_lower and "levels_played" in query_lower:
        return "DAILY_ENGAGEMENT_QUERY"
    elif "daily_return_rate_pct" in query_lower or "returned_next_day" in query_lower:
        return "DAILY_RETURN_RATE_QUERY"
    elif "two_week_retention_pct" in query_lower or "active_week_2" in query_lower:
        return "TWO_WEEK_RETENTION_QUERY"
    elif "milestone_level" in query_lower or "completion_rate" in query_lower:
        return "PROGRESSION_MILESTONE_QUERY"
    elif "revenue_day1_20" in query_lower:
        return "REVENUE_SEGMENTATION_QUERY"
    elif "retention_rate_day1_20" in query_lower:
        return "RETENTION_RATE_QUERY"
    elif "revenue_type" in query_lower and "eventdate" in query_lower:
        return "REVENUE_BY_SOURCE_QUERY"
    elif "anomaly" in query_lower or "threshold_100x" in query_lower:
        return "ANOMALY_TRANSACTIONS_QUERY"
    elif "install_date" in query_lower and "platform" in query_lower:
        return "PLAYER_DISTRIBUTION_QUERY"
    
    return None


@st.cache_data
def get_bigquery_data(query):
    """Execute BigQuery query and return DataFrame, fallback to CSV files."""
    # First try BigQuery
    client = get_bigquery_client()
    if client is not None:
        try:
            query_job = client.query(query)
            return query_job.to_dataframe()
        except Exception as e:
            pass
    
    # Fallback to CSV files
    query_type = identify_query_type(query)
    if query_type and query_type in CSV_FILE_MAPPING:
        csv_file = CSV_FILE_MAPPING[query_type]
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)
                return df
            except Exception as e:
                pass
    
    # If no matching CSV file found
    return pd.DataFrame()