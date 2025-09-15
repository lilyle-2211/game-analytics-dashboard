"""Goal metrics module for A/B testing."""
import streamlit as st


def render_goal_metrics_tab():
    """Render the goal metrics setting tab."""
    
    st.markdown("""
    ## A/B Test Metrics for New Level Design
    
    ### Primary Success Metrics
    - **Level completion rate** - % of players who complete the new level
    
    ### Secondary Metrics
    - **Retry attempts** - Average number of attempts before completion
    
    ### Guardrail Metrics
    - **Overall session length** - Ensure new design doesn't hurt total playtime
    - **Day 1 retention** - % of players returning the next day
    - **Day 7 retention** - % of players still active after a week
    - **Technical performance** - Crash rates, load times
    """)
    