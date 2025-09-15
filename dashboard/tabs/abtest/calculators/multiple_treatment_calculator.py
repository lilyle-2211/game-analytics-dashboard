"""Multiple treatment calculator module for multi-arm A/B testing."""
import numpy as np
import streamlit as st
from statsmodels.stats.power import NormalIndPower, TTestIndPower
from statsmodels.stats.proportion import proportion_effectsize


def render_multiple_treatment_configuration():
    """Render Test Configuration section for multiple treatment calculator."""
    st.markdown("### Test Configuration")

    # Test type selection
    multi_test_metric = st.selectbox(
        "Test Type",
        ["Z-test (proportion)", "t-test (continuous)"],
        help="Choose the type of metric you're testing",
        key="multi_test_metric",
    )

    # Number of treatment groups
    num_treatments = st.slider(
        "Number of Treatment Groups",
        min_value=2,
        max_value=5,
        value=3,
        step=1,
        help="Number of treatment variations (excluding control)",
        key="multi_num_treatments",
    )

    # Multiple comparison correction method
    correction_method = st.selectbox(
        "Multiple Comparison Correction",
        ["Bonferroni Method", "False Discovery Rate (Benjamini-Hochberg)"],
        help="Method to control for multiple comparisons",
        key="multi_correction_method",
    )

    # Statistical parameters
    multi_alpha = st.slider(
        "Significance Level (α)",
        min_value=0.01,
        max_value=0.10,
        value=0.05,
        step=0.01,
        format="%.2f",
        help="Probability of Type I error (false positive)",
        key="multi_alpha",
    )

    multi_power = st.slider(
        "Statistical Power (1-β)",
        min_value=0.70,
        max_value=0.95,
        value=0.80,
        step=0.01,
        format="%.2f",
        help="Probability of detecting a true effect",
        key="multi_power",
    )

    # Store in session state
    st.session_state.multi_params.update(
        {
            "test_metric": multi_test_metric,
            "num_treatments": num_treatments,
            "correction_method": correction_method,
            "alpha": multi_alpha,
            "power": multi_power,
        }
    )


def render_multiple_treatment_traffic_timeline():
    """Render Traffic & Timeline section for multiple treatment calculator."""
    st.markdown("### Traffic & Timeline")

    multi_daily_users = st.number_input(
        "Daily New Users",
        min_value=100,
        max_value=100000,
        value=1000,
        step=100,
        help="Number of new users available per day for testing",
        key="multi_daily_users",
    )

    treatment_allocation = (
        st.slider(
            "Total Treatment Allocation (%)",
            min_value=50,
            max_value=90,
            value=75,
            step=5,
            help="Percentage of users allocated to all treatment groups combined",
            key="multi_treatment_allocation",
        )
        / 100
    )

    # Store in session state
    st.session_state.multi_params.update(
        {"daily_users": multi_daily_users, "treatment_allocation": treatment_allocation}
    )


def render_multiple_treatment_metric_parameters():
    """Render Metric Parameters section for multiple treatment calculator."""
    st.markdown("### Metric Parameters")

    multi_test_metric = st.session_state.multi_params.get(
        "test_metric", "Z-test (proportion)"
    )

    if "Z-test" in multi_test_metric:
        multi_current_rate = (
            st.number_input(
                "Current Completion Rate (%)",
                min_value=0.1,
                max_value=99.9,
                value=15.0,
                step=0.1,
                help="Current conversion/completion rate of your control group",
                key="multi_current_rate",
            )
            / 100
        )

        multi_mde_type = st.selectbox(
            "MDE Input Type",
            ["Absolute Change (percentage points)", "Relative Change (%)"],
            help="Specify MDE as absolute percentage points or relative percentage change",
            key="multi_mde_type",
        )

        if "Absolute" in multi_mde_type:
            multi_mde = (
                st.number_input(
                    "Minimum Detectable Effect (percentage points)",
                    min_value=0.1,
                    max_value=50.0,
                    value=2.0,
                    step=0.1,
                    help="Minimum absolute change in percentage points you want to detect",
                    key="multi_mde_abs",
                )
                / 100
            )
            multi_new_rate = multi_current_rate + multi_mde
        else:
            multi_relative_mde = st.number_input(
                "Minimum Detectable Effect (% relative change)",
                min_value=1.0,
                max_value=500.0,
                value=10.0,
                step=1.0,
                help="Minimum relative change percentage you want to detect",
                key="multi_mde_rel",
            )
            multi_new_rate = multi_current_rate * (1 + multi_relative_mde / 100)
            multi_mde = multi_new_rate - multi_current_rate

        # Store in session state
        st.session_state.multi_params.update(
            {
                "current_rate": multi_current_rate,
                "mde_type": multi_mde_type,
                "mde": multi_mde,
                "new_rate": multi_new_rate,
            }
        )
    else:
        multi_current_mean = st.number_input(
            "Current Mean Value",
            min_value=0.0,
            value=100.0,
            step=1.0,
            help="Current mean value of your metric",
            key="multi_current_mean",
        )

        multi_std_dev = st.number_input(
            "Standard Deviation",
            min_value=0.1,
            value=20.0,
            step=0.1,
            help="Standard deviation of your metric",
            key="multi_std_dev",
        )

        multi_effect_size_input = st.number_input(
            "Minimum Detectable Effect",
            min_value=0.1,
            value=5.0,
            step=0.1,
            help="Minimum change in mean you want to detect",
            key="multi_effect_size",
        )

        # Calculate Cohen's d for t-test
        multi_cohens_d = multi_effect_size_input / multi_std_dev

        # Store in session state
        st.session_state.multi_params.update(
            {
                "current_mean": multi_current_mean,
                "std_dev": multi_std_dev,
                "effect_size_input": multi_effect_size_input,
                "cohens_d": multi_cohens_d,
            }
        )


def render_multiple_treatment_results():
    """Render Calculation Results section for multiple treatment calculator."""
    try:
        # Get parameters from session state
        multi_params = st.session_state.multi_params
        test_metric = multi_params.get("test_metric", "Z-test (proportion)")
        alpha = multi_params.get("alpha", 0.05)
        power = multi_params.get("power", 0.80)
        num_treatments = multi_params.get("num_treatments", 3)
        correction_method = multi_params.get("correction_method", "Bonferroni Method")
        treatment_allocation = multi_params.get("treatment_allocation", 0.75)
        daily_users = multi_params.get("daily_users", 1000)

        # Calculate adjusted alpha based on correction method
        if "Bonferroni" in correction_method:
            alpha_adjusted = alpha / num_treatments
            correction_label = "Bonferroni"
        else:  # False Discovery Rate
            # For sample size calculation, FDR is applied post-hoc, so we use original alpha
            # This provides a conservative sample size estimate
            alpha_adjusted = alpha
            correction_label = "FDR (B-H)"

        # Calculate sample size using statsmodels
        if "Z-test" in test_metric:
            power_analysis = NormalIndPower()

            current_rate = multi_params.get("current_rate", 0.15)
            mde = multi_params.get("mde", 0.02)

            # Calculate effect size using Cohen's h (correct for proportions)
            p1 = current_rate
            p2 = current_rate + mde
            effect_size = proportion_effectsize(p2, p1)  # Cohen's h

            # Equal allocation among treatment groups
            treatment_per_group = treatment_allocation / num_treatments
            control_allocation = 1 - treatment_allocation
            allocation_ratio = treatment_per_group / control_allocation

            sample_size_control = power_analysis.solve_power(
                effect_size=effect_size,
                power=power,
                alpha=alpha_adjusted,
                alternative="two-sided",
                ratio=allocation_ratio,
            )
            sample_size_control = int(np.ceil(sample_size_control))
            sample_size_per_treatment = int(
                np.ceil(sample_size_control * allocation_ratio)
            )

        else:  # Continuous metric
            power_analysis = TTestIndPower()
            cohens_d = multi_params.get("cohens_d", 0.25)

            treatment_per_group = treatment_allocation / num_treatments
            control_allocation = 1 - treatment_allocation
            allocation_ratio = treatment_per_group / control_allocation

            sample_size_control = power_analysis.solve_power(
                effect_size=cohens_d,
                power=power,
                alpha=alpha_adjusted,
                alternative="two-sided",
                ratio=allocation_ratio,
            )
            sample_size_control = int(np.ceil(sample_size_control))
            sample_size_per_treatment = int(
                np.ceil(sample_size_control * allocation_ratio)
            )

        st.markdown("---")
        st.markdown("### Calculation Results")

        # Horizontal layout for results
        total_sample = sample_size_control + (
            sample_size_per_treatment * num_treatments
        )

        # Duration calculation
        control_users_per_day = daily_users * (1 - treatment_allocation)
        treatment_users_per_day_per_group = daily_users * (
            treatment_allocation / num_treatments
        )

        # Duration is determined by whichever group takes longer to fill
        # All groups must run for the same duration for validity
        days_for_control = np.ceil(sample_size_control / control_users_per_day)
        days_for_treatment = np.ceil(
            sample_size_per_treatment / treatment_users_per_day_per_group
        )
        duration = max(days_for_control, days_for_treatment)

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Control Group Size",
                f"{sample_size_control:,}",
                help="Number of users needed in control group",
            )

        with col2:
            st.metric(
                "Per Treatment Group",
                f"{sample_size_per_treatment:,}",
                help="Number of users needed in each treatment group",
            )

        with col3:
            st.metric(
                "Total Sample Size",
                f"{total_sample:,}",
                help="Total users needed for the test",
            )

        with col4:
            st.metric(
                f"Adjusted Alpha ({correction_label})",
                f"{alpha_adjusted:.4f}",
                help=f"Alpha level after {correction_label} correction for multiple comparisons",
            )

        with col5:
            st.metric(
                "Test Duration",
                f"{int(duration)} days ({duration/7:.1f} weeks)",
                help="Test duration in days",
            )

        # Add Python code section
        from .code_generators import render_multiple_treatment_python_code

        with st.expander("📋 Python Code", expanded=False):
            render_multiple_treatment_python_code(
                multi_params,
                sample_size_control,
                sample_size_per_treatment,
                total_sample,
                duration,
                alpha_adjusted,
                correction_label,
            )

    except Exception as e:
        st.error(f"Error calculating multiple treatment sample size: {str(e)}")
