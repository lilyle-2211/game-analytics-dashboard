"""Sample size calculator for A/B testing using statistical packages."""
import streamlit as st

from .calculators.ab_test_calculator import (
    render_ab_test_configuration,
    render_ab_test_metric_parameters,
    render_ab_test_results,
    render_ab_test_traffic_timeline,
)
from .calculators.code_generators import (
    render_ab_test_python_code,
    render_multiple_treatment_python_code,
)
from .calculators.multiple_treatment_calculator import (
    render_multiple_treatment_configuration,
    render_multiple_treatment_metric_parameters,
    render_multiple_treatment_results,
    render_multiple_treatment_traffic_timeline,
)


def render_sample_size_calculator_tab():
    """Render the sample size calculator tab."""

    # Initialize session state for both calculators
    if "ab_params" not in st.session_state:
        st.session_state.ab_params = {}
    if "multi_params" not in st.session_state:
        st.session_state.multi_params = {}

    # Add custom CSS for blue section headers
    st.markdown(
        """
        <style>
        .section-header {
            background: linear-gradient(90deg, #2E86C1, #5DADE2);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin: 20px 0 15px 0;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section-divider {
            margin: 40px 0;
            border-top: 2px solid #E8F4FD;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Section 1: Simple A/B Test (1 Control vs 1 Treatment)
    st.markdown(
        '<div class="section-header">1 Control vs 1 Treatment</div>',
        unsafe_allow_html=True,
    )

    # Render A/B test calculator in 3 columns
    col1, col2, col3 = st.columns(3)

    with col1:
        render_ab_test_configuration()
    with col2:
        render_ab_test_traffic_timeline()
    with col3:
        render_ab_test_metric_parameters()

    render_ab_test_results()

    # Add Python code section for simple A/B test
    if st.session_state.ab_params:
        with st.expander("View Python Code for This Calculation", expanded=False):
            # Get calculated values from session state (you may need to adjust based on actual implementation)
            ab_params = st.session_state.ab_params
            # Note: You'll need to get these values from the actual calculation results
            sample_size_control = ab_params.get("calculated_sample_control", 1000)
            sample_size_treatment = ab_params.get("calculated_sample_treatment", 1000)
            total_sample = sample_size_control + sample_size_treatment
            duration = ab_params.get("calculated_duration", 14)

            render_ab_test_python_code(
                ab_params,
                sample_size_control,
                sample_size_treatment,
                total_sample,
                duration,
            )

    # Section divider
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Section 2: Multiple Treatment Test
    st.markdown(
        '<div class="section-header">1 Control vs Multiple Treatments</div>',
        unsafe_allow_html=True,
    )

    # Render multiple treatment calculator in 3 columns
    col1, col2, col3 = st.columns(3)

    with col1:
        render_multiple_treatment_configuration()
    with col2:
        render_multiple_treatment_traffic_timeline()
    with col3:
        render_multiple_treatment_metric_parameters()

    render_multiple_treatment_results()

    # Add Python code section for multiple treatment test
    if st.session_state.multi_params:
        with st.expander("View Python Code for This Calculation", expanded=False):
            # Get calculated values from session state (you may need to adjust based on actual implementation)
            multi_params = st.session_state.multi_params
            # Note: You'll need to get these values from the actual calculation results
            sample_size_control = multi_params.get("calculated_sample_control", 1000)
            sample_size_per_treatment = multi_params.get(
                "calculated_sample_per_treatment", 1000
            )
            total_sample = multi_params.get("calculated_total_sample", 4000)
            duration = multi_params.get("calculated_duration", 21)

            render_multiple_treatment_python_code(
                multi_params,
                sample_size_control,
                sample_size_per_treatment,
                total_sample,
                duration,
            )
