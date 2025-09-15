"""Goal metrics module for A/B testing."""
import streamlit as st


def render_goal_metrics_tab():
    """Render the goal metrics setting tab."""

    st.markdown(
        """
    ## A/B Test Plan: Level Design Changes

    Testing new level design in opening levels for U.S. players to improve early
    engagement without affecting performance.

    ### Groups

    **Control:** Current level design

    **Treatment:** New level design (level changes only)

    ### Hypothesis

    **H0:** New design has no significant impact on engagement or retention

    **H1:** New design improves engagement and retention

    ### Success Metrics

    **Day 1 Retention**
    - Current: ~% baseline
    - Target: Significant improvement

    **Level Completion Rate**
    - Current: ~% complete first 5 levels
    - Target: Higher completion

    ### Guardrail Metrics

    **Session Length**
    - Threshold: No decrease >10%

    **Crash Rate**
    - Threshold: No increase

    ### Analysis Plan

    **Randomization:** Player level, U.S. new installs only

    **Traffic:** Start 5-10%, scale to 50/50

    **Test:** Two-proportion z-test for both retention and completion rates
    """
    )
