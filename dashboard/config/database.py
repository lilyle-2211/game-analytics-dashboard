"""BigQuery database configuration and client setup."""
import streamlit as st
from google.cloud import bigquery
import pandas as pd


@st.cache_resource
def get_bigquery_client():
    """Get BigQuery client with cloud deployment support."""
    try:
        return bigquery.Client(project="tactile-471816")
    except Exception:
        return None


@st.cache_data
def get_bigquery_data(query):
    """Execute BigQuery query and return DataFrame."""
    client = get_bigquery_client()
    if client is None:
        st.error("BigQuery client not available. Please check your credentials.")
        return pd.DataFrame()
    
    query_job = client.query(query)
    return query_job.to_dataframe()