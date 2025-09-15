"""BigQuery database configuration and client setup."""
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import json
import os


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
        st.warning(f"BigQuery authentication failed: {str(e)}")
        return None


@st.cache_data
def get_bigquery_data(query):
    """Execute BigQuery query and return DataFrame."""
    client = get_bigquery_client()
    if client is None:
        st.info("📊 Running in demo mode - BigQuery not available. The A/B testing calculators work independently!")
        # Return empty DataFrame for demo purposes
        return pd.DataFrame()
    
    try:
        query_job = client.query(query)
        return query_job.to_dataframe()
    except Exception as e:
        st.warning(f"BigQuery query failed: {str(e)}. Running in demo mode.")
        return pd.DataFrame()