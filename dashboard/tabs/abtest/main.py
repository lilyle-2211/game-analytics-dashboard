"""A/B testing analytics tab."""
import streamlit as st
from .goal_metrics import render_goal_metrics_tab
from .sample_size_calculator import render_sample_size_calculator_tab
from .interpretation import render_interpretation_tab


def render_abtest_tab():
    """Render the A/B testing analytics tab."""
    
    # Create tabs with distinctive styling
    tab1, tab2, tab3 = st.tabs(["1. Set Goal Metrics", "2. Sample Size Calculator", "3. Interpretation"])
    
    with tab1:
        render_goal_metrics_tab()
    
    with tab2:
        render_sample_size_calculator_tab()
    
    with tab3:
        render_interpretation_tab()
    
    # Add custom CSS for A/B test sub-tabs only
    st.markdown("""
    <style>
    /* Target only the A/B test sub-tabs by using a more specific selector */
    div[data-testid="stTabs"] .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: center;
        margin: 20px 0;
        background: transparent;
    }
    
    div[data-testid="stTabs"] .stTabs [data-baseweb="tab-list"] button {
        height: 60px;
        padding: 12px 24px;
        background: #f8f9fa !important;
        color: #6c757d !important;
        border: 2px solid #dee2e6 !important;
        border-radius: 12px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
        min-width: 250px !important;
    }
    
    div[data-testid="stTabs"] .stTabs [data-baseweb="tab-list"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        background: #e9ecef !important;
        border-color: #adb5bd !important;
    }
    
    div[data-testid="stTabs"] .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: #28a745 !important;
        color: white !important;
        border-color: #28a745 !important;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    
    div[data-testid="stTabs"] .stTabs [data-baseweb="tab-list"] button p {
        margin: 0 !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }
    
    /* Tab content styling for A/B test tabs only */
    div[data-testid="stTabs"] .stTabs [data-baseweb="tab-panel"] {
        padding-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True)