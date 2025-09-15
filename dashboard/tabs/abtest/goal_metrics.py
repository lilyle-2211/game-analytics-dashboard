"""Goal metrics module for A/B testing."""
import streamlit as st


def render_goal_metrics_tab():
    """Render the goal metrics setting tab."""
    
    st.markdown("""
    ## A/B Test Planning: New Level Design Experiment
    
    We are conducting an A/B test to evaluate a new level design in our initial levels, 
    targeting the U.S. player population. This test aims to optimize early-game engagement 
    while maintaining technical performance.
    
    ### Treatment Definition
    
    **Control Group:** Players experience the current initial level design
    
    **Treatment Group:** Players experience the redesigned initial levels with isolated 
    impact. Only level design changes, all other factors remain constant
    
    ### Hypothesis Framework

    **Null Hypothesis:** The new level design has no significant impact on player
    engagement, retention, or technical issues compared to the current design.

    **Alternative Hypothesis:** The new level design improves early-game engagement
    and retention without negatively affecting technical performance of the game.
    
    ### Primary Success Metrics
    
    **Day 1 Retention**
    - Definition: Percentage of players returning the day after install
    - Target: Statistically significant improvement
    
    **Level Completion Rate**
    - Definition: Percentage of players completing the first Xth level
    - Target: Higher completion without compromising difficulty

    
    ### Guardrail Metrics
    
    These metrics must not worsen significantly:
    
    **Session Length**
    - Monitor: Average minutes per session
    - Threshold: No decrease greater than X percent.
    
    **Technical Stability**
    - Monitor: Crash rate and error events
    - Threshold: No increase in technical issues
    
    ### Tracking Metrics
    
    Additional metrics to understand the impact: Player advancement speed

    
    ### Expected Outcomes

    Success will be measured by improved retention and engagement without technical issues. Launch decision will be based on statistical
    significance and business impact assessment.
    """)
    