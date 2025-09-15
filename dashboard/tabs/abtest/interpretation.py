"""Interpretation module for A/B testing results."""
import streamlit as st
import plotly.graph_objects as go


def render_interpretation_tab():
    """Render the interpretation tab."""
    st.markdown("### How to Interpret A/B Test Results")
    
    # Show both test types without toggle
    st.markdown("## Standard A/B Test")
    _render_standard_ab_test_scenarios()
    
    st.markdown("---")
    
    st.markdown("## Multiple Treatment Test")  
    _render_multiple_treatment_scenarios()
    
    st.markdown("---")
    
    st.markdown("### Key Concepts")
    
    st.markdown("""
    **Uplift** is calculated as: **Treatment Rate - Control Rate**
    - Example: 72% - 65% = +7% uplift
    - Positive uplift = treatment performs better
    - Negative uplift = treatment performs worse
    - Zero uplift = no difference between groups
    """)


def _render_standard_ab_test_scenarios():
    """Render scenarios for standard A/B test."""
    # Create mock scenarios for standard A/B test
    scenarios = [
        {
            "name": "Clear Winner",
            "control_rate": 0.65,
            "treatment_rate": 0.72,
            "p_value": 0.003,
            "ci_lower": 0.04,
            "ci_upper": 0.10,
            "interpretation": "LAUNCH - Treatment significantly outperforms control",
            "color": "green"
        },
        {
            "name": "No Effect",
            "control_rate": 0.65,
            "treatment_rate": 0.66,
            "p_value": 0.34,
            "ci_lower": -0.02,
            "ci_upper": 0.04,
            "interpretation": "NO LAUNCH - No significant difference detected",
            "color": "gray"
        },
        {
            "name": "Negative Effect",
            "control_rate": 0.65,
            "treatment_rate": 0.58,
            "p_value": 0.001,
            "ci_lower": -0.11,
            "ci_upper": -0.03,
            "interpretation": "DO NOT LAUNCH - Treatment significantly hurts performance",
            "color": "red"
        },
        {
            "name": "Below MDE",
            "control_rate": 0.65,
            "treatment_rate": 0.67,
            "p_value": 0.02,
            "ci_lower": 0.005,
            "ci_upper": 0.035,
            "interpretation": "INCONCLUSIVE - Significant but below minimum detectable effect",
            "color": "orange"
        }
    ]
    alpha_threshold = 0.05
    
    _render_scenarios(scenarios, alpha_threshold, "Standard A/B Test")


def _render_multiple_treatment_scenarios():
    """Render scenarios for multiple treatment test."""
    # Create scenarios for multiple treatment test
    scenarios = [
        {
            "name": "Treatment A - Strong Winner",
            "control_rate": 0.65,
            "treatment_rate": 0.74,
            "p_value": 0.001,
            "ci_lower": 0.06,
            "ci_upper": 0.12,
            "interpretation": "LAUNCH - Treatment A significantly outperforms control (Bonferroni-adjusted)",
            "color": "green"
        },
        {
            "name": "Treatment B - Marginal (would be significant in standard A/B)",
            "control_rate": 0.65,
            "treatment_rate": 0.69,
            "p_value": 0.03,
            "ci_lower": 0.01,
            "ci_upper": 0.07,
            "interpretation": "NO LAUNCH - Not significant with Bonferroni correction (p > 0.0167)",
            "color": "orange"
        },
        {
            "name": "Treatment C - Clear Winner",
            "control_rate": 0.65,
            "treatment_rate": 0.72,
            "p_value": 0.008,
            "ci_lower": 0.04,
            "ci_upper": 0.10,
            "interpretation": "LAUNCH - Treatment C significantly outperforms control (Bonferroni-adjusted)",
            "color": "green"
        }
    ]
    alpha_threshold = 0.0167  # 0.05/3 for 3 treatments
    
    _render_scenarios(scenarios, alpha_threshold, "Multiple Treatment Test")
    
    st.markdown("### Multiple Treatment Test Considerations")
    st.markdown(f"""
    **Bonferroni Correction Applied:**
    - Standard significance level: α = 0.05
    - Adjusted significance level: α = {alpha_threshold:.3f} (0.05/3 treatments)
    - **Critical**: Each treatment must have p < {alpha_threshold:.3f} to be considered significant
    
    **Key Differences from Standard A/B Tests:**
    - Higher bar for significance due to multiple comparisons
    - Only compare each treatment vs control (not treatments vs each other)
    - Can have multiple winners, or no winners
    - Requires larger sample sizes than standard A/B tests
    """)


def _render_scenarios(scenarios, alpha_threshold, test_type):
    """Render scenarios with confidence interval plots and metrics."""
    for i, scenario in enumerate(scenarios):
        with st.expander(f"Scenario {i+1}: {scenario['name']}"):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Create mock confidence interval plot
                fig = go.Figure()
                
                # Add confidence interval
                fig.add_shape(
                    type="line",
                    x0=scenario["ci_lower"], y0=0.5,
                    x1=scenario["ci_upper"], y1=0.5,
                    line=dict(color=scenario["color"], width=8)
                )
                
                # Add point estimate
                uplift = scenario["treatment_rate"] - scenario["control_rate"]
                fig.add_trace(go.Scatter(
                    x=[uplift], y=[0.5],
                    mode='markers',
                    marker=dict(size=15, color=scenario["color"]),
                    showlegend=False,
                    name="Point Estimate"
                ))
                
                # Add zero line
                fig.add_vline(x=0, line_dash="dash", line_color="black", annotation_text="No Effect")
                
                # Add MDE line (5%)
                fig.add_vline(x=0.05, line_dash="dot", line_color="blue", annotation_text="MDE (5%)")
                
                # Add significance threshold line for multiple treatment tests
                if test_type == "Multiple Treatment Test":
                    fig.add_annotation(x=0.08, y=0.8, text=f"α = {alpha_threshold:.3f}", 
                                     showarrow=False, font=dict(color="red"))
                
                fig.update_layout(
                    title=f"95% Confidence Interval",
                    xaxis_title="Uplift (Treatment - Control)",
                    yaxis=dict(showticklabels=False, range=[0, 1]),
                    height=300,
                    showlegend=False
                )
                
                fig.update_layout(xaxis=dict(tickformat=".1%"))
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Test Results:**")
                st.metric("Control Rate", f"{scenario['control_rate']:.1%}")
                st.metric("Treatment Rate", f"{scenario['treatment_rate']:.1%}")
                st.metric("Uplift", f"{(scenario['treatment_rate'] - scenario['control_rate']):.1%}")
                st.metric("P-value", f"{scenario['p_value']:.3f}")
                st.markdown(f"**95% CI:** [{scenario['ci_lower']:.1%}, {scenario['ci_upper']:.1%}]")
                
                st.markdown("---")
                st.markdown(f"**Decision:** {scenario['interpretation']}")
