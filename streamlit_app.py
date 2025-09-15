"""
Game Analytics Dashboard - Refactored Modular Version

A comprehensive Streamlit dashboard for game analytics including:
- Player acquisition analysis
- Engagement metrics
- Monetisation analytics  
- A/B testing insights
- LTV analysis
- AI-powered assistant

Command line usage:
    streamlit run streamlit_app.py -- --enable-ai
    streamlit run streamlit_app.py -- --disable-ai
"""

import streamlit as st
import sys

# Import tab modules
from dashboard.tabs.acquisition.main import render_acquisition_tab
from dashboard.tabs.engagement.main import render_engagement_tab
from dashboard.tabs.monetization.main import render_monetization_tab
from dashboard.tabs.abtest.main import render_abtest_tab
from dashboard.tabs.ltv.main import render_ltv_tab
from dashboard.tabs.assistant.main import render_assistant_tab
from dashboard.tabs.contact.main import render_contact_tab

# Import utilities
from dashboard.utils.ai_explainer import DashboardExplainer


def get_ai_enabled_setting():
    """Get AI enabled setting from command line args, session state, or secrets."""
    # Check command line arguments first
    if '--enable-ai' in sys.argv:
        return True
    elif '--disable-ai' in sys.argv:
        return False
    
    # Check session state (dashboard toggle)
    if 'ai_enabled_override' in st.session_state:
        return st.session_state.ai_enabled_override
    
    # Fall back to secrets.toml
    if hasattr(st, 'secrets') and 'enable_ai_calls' in st.secrets:
        return st.secrets["enable_ai_calls"]
    
    # Default to False (testing mode)
    return False


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="Game Analytics Showcase",
        layout="wide"
    )

    # Centered dashboard title without icon
    st.markdown(
        """
        <h1 style='text-align: center; margin-top: 0; margin-bottom: 2rem;'>GAME ANALYTICS SHOWCASE</h1>
        """,
        unsafe_allow_html=True
    )
    
    # Get AI enabled setting from various sources
    ai_enabled_setting = get_ai_enabled_setting()
    
    # Initialize AI explainer for status check
    explainer = DashboardExplainer()
    
    # Top right creator name
    col_spacer, col_creator = st.columns([6, 2])
    with col_creator:
        st.markdown("<div style='text-align: right;'>Creator: Lily Le</div>", unsafe_allow_html=True)

    # Create tabs with bold styling
    tab_names = [
        "ACQUISITION",
        "ENGAGEMENT", 
        "MONETISATION",
        "A/B TEST",
        "LTV", 
        "AI ASSISTANT",
        "CONTACT ME!"
    ]
    
    # Enhanced tab styling to match A/B test sub-tabs with orange active tab
    tab_styles = """
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: center;
        margin: 20px 0;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        height: 60px;
        padding: 12px 24px;
        background: #f8f9fa;
        color: #6c757d;
        border: 2px solid #dee2e6;
        border-radius: 12px;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        min-width: 180px;
    }
    
    .stTabs [data-baseweb="tab-list"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        background: #e9ecef;
        border-color: #adb5bd;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: #ff8c00 !important;
        color: white !important;
        border-color: #ff8c00 !important;
        box-shadow: 0 4px 15px rgba(255, 140, 0, 0.4) !important;
        transform: translateY(-2px);
    }
    
    .stTabs [data-baseweb="tab-list"] button p {
        margin: 0;
        font-size: 18px;
        font-weight: bold;
    }
    </style>
    """
    st.markdown(tab_styles, unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tab_names)

    # Render each tab
    with tab1:
        render_acquisition_tab()

    with tab2:
        render_engagement_tab()

    with tab3:
        render_monetization_tab()

    with tab4:
        render_abtest_tab()

    with tab5:
        render_ltv_tab()

    with tab6:
        render_assistant_tab()
        
    with tab7:
        render_contact_tab()
        
    # Create a footer area for the AI toggle at the bottom right
    st.markdown("<hr style='margin-top: 50px'>", unsafe_allow_html=True)  # Add divider before footer
    _, col_footer = st.columns([6, 2])
    with col_footer:
        current_state = st.session_state.get('ai_enabled_override', ai_enabled_setting)
        st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
        if st.button(f"{'Disable AI' if current_state else 'Enable AI'}", key="ai_toggle_btn", 
                    help="Toggle AI insights on/off to save API costs during testing"):
            st.session_state.ai_enabled_override = not current_state
            st.rerun()
        final_ai_enabled = get_ai_enabled_setting() and explainer.ai_enabled
        if final_ai_enabled:
            st.success("AI Enabled")
        else:
            current_setting = get_ai_enabled_setting()
            if not current_setting:
                st.info("AI Disabled")
            else:
                st.error("API Key Issue")
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()