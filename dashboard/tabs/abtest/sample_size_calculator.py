"""Sample size calculator for A/B testing using statistical packages."""
import streamlit as st

from .calculators.ab_test_calculator import (
    render_ab_test_configuration,
    render_ab_test_metric_parameters,
    render_ab_test_results,
    render_ab_test_traffic_timeline,
)
from .calculators.multiple_treatment_calculator import (
    render_multiple_treatment_configuration,
    render_multiple_treatment_metric_parameters,
    render_multiple_treatment_results,
    render_multiple_treatment_traffic_timeline,
)


def render_sample_size_calculator_tab():
    """Render the sample size calculator tab."""

    # Test type selector with updated options
    test_type = st.selectbox(
        "Select Test Type",
        [
            "1 Control vs 1 Treatment",
            "1 Control vs Multiple Treatments (with Multiple Comparison Correction)",
        ],
        index=0,
        help="Choose between simple A/B test or multiple treatment experiment with correction methods",
    )

    # Initialize session state for both calculators
    if "ab_params" not in st.session_state:
        st.session_state.ab_params = {}
    if "multi_params" not in st.session_state:
        st.session_state.multi_params = {}

    # Render based on selection
    if "Multiple" in test_type:
        # Render multiple treatment calculator in 3 columns
        col1, col2, col3 = st.columns(3)

        with col1:
            render_multiple_treatment_configuration()
        with col2:
            render_multiple_treatment_traffic_timeline()
        with col3:
            render_multiple_treatment_metric_parameters()

        render_multiple_treatment_results()
    else:
        # Render A/B test calculator in 3 columns
        col1, col2, col3 = st.columns(3)

        with col1:
            render_ab_test_configuration()
        with col2:
            render_ab_test_traffic_timeline()
        with col3:
            render_ab_test_metric_parameters()

        render_ab_test_results()

    # Add explanations at the end of the page
    render_correction_methods_explanation()


def render_correction_methods_explanation():
    """Render explanations for multiple comparison correction methods."""
    st.markdown("---")
    st.markdown("### Multiple Comparison Correction Methods")

    with st.expander("📖 Understanding Correction Methods", expanded=False):
        st.markdown(
            """
        **Sample Size Calculation:**

        - **1 Control vs 1 Treatment:** Uses α = 0.05
        - **Multiple Treatments with Bonferroni:** Uses α_adjusted = 0.05 / number_of_treatments (smaller α = larger sample size)
        - **Multiple Treatments with FDR:** Uses α = 0.05 (same as single comparison)

        **Test Duration:**

        - **1 Control vs 1 Treatment:** Standard duration based on sample size
        - **Multiple Treatments with Bonferroni:** Longer duration (due to larger sample size)
        - **Multiple Treatments with FDR:** Same duration as single comparison
        """
        )
