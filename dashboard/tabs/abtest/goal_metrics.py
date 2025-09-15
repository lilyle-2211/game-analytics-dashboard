"""Goal metrics module for A/B testing."""
import streamlit as st


def render_goal_metrics_tab():
    """Render the goal metrics setting tab."""

    st.markdown(
        """
    ## A/B Test Planning: New Level Design Experiment

    This A/B test evaluates a new level design in the opening levels, specifically
    targeting U.S. players. The goal is to boost early-game engagement while keeping
    technical performance stable.

    ### Treatment Definition

    **Control Group:** Players see the current initial level design

    **Treatment Group:** Players experience redesigned initial levels with isolated changes.
    Only the level design changes, everything else stays exactly the same.

    ### Hypothesis Framework

    **Null Hypothesis:** The new level design doesn't significantly impact player
    engagement, retention, or technical performance compared to the current design.

    **Alternative Hypothesis:** The new level design improves early-game engagement
    and retention without hurting the game's technical performance.

    ### Primary Success Metrics

    **Day 1 Retention**
    - Measurement: Percentage of players who return the day after installing
    - Target: A statistically significant improvement

    **Level Completion Rate**
    - Measurement: Percentage of players who complete the first X levels
    - Target: Higher completion rates without making the game too easy

    ### Guardrail Metrics
    (These metrics shouldn't be worsen during the test)

    **Session Length**
    - Monitor: Average minutes per session. Threshold: No decrease greater than X%

    **Technical Stability**
    - Monitor: Crash rates and error events. Threshold: No increase in technical problems

    ### Tracking Metrics

    Player Advancement Speed: How quickly players progress through levels

    ### Expected Outcomes

    The test will be considered successful if improved retention and engagement occur
    without any technical issues. Launch decisions will depend on both statistical
    significance and overall business impact.

    ### Unit of Randomization

    Randomization occurs at the player level. Every new U.S. player who installs or opens
    the game for the first time gets randomly assigned to either the control (current design)
    or treatment (new design). Each player only ever sees one version.

    ### When Players Enter the Experiment

    Players enter the experiment the moment they start the game for the first time.
    The test includes only:
    - New installs start from the test window
    - Excludes returning players so prior experience doesn't bias results

    The rollout starts with a small portion of traffic (around 5-10%) to ensure
    everything runs smoothly, then scales up.

    ### Statistical Analysis Plan

    For Day 1 Retention as primary success metric, the analysis compares the proportion of players who return
    the next day in the treatment group versus the control group. Since this is a
    proportion outcome, a two-proportion z-test will check if the difference between groups is statistically significant.

    Similarly, for Level Completion Rate, a two-proportion z-test will compare the percentage of players who complete the first X levels in each group.
    """
    )
