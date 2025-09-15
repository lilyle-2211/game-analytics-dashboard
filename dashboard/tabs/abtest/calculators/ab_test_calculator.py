"""A/B test calculator module for simple two-group testing."""
import numpy as np
import streamlit as st
from statsmodels.stats.power import NormalIndPower, TTestIndPower
from statsmodels.stats.proportion import proportion_effectsize


def render_ab_test_configuration():
    """Render Test Configuration section for A/B test calculator."""
    st.markdown("### Test Configuration")

    # Test type selection
    test_metric = st.selectbox(
        "Test Type",
        ["Z-test (proportion)", "t-test (continuous)"],
        help="Choose the type of metric you're testing",
        key="ab_test_metric",
    )

    # Statistical parameters
    alpha = st.slider(
        "Significance Level (α)",
        min_value=0.01,
        max_value=0.10,
        value=0.05,
        step=0.01,
        help="Probability of Type I error (false positive). Common values: 0.05, 0.01",
        key="ab_alpha",
    )

    power = st.slider(
        "Statistical Power (1-β)",
        min_value=0.70,
        max_value=0.95,
        value=0.80,
        step=0.05,
        help="Probability of detecting an effect if it exists. Common values: 0.80, 0.90",
        key="ab_power",
    )

    # Store in session state
    st.session_state.ab_params.update(
        {"test_metric": test_metric, "alpha": alpha, "power": power}
    )


def render_ab_test_traffic_timeline():
    """Render Traffic & Timeline section for A/B test calculator."""
    st.markdown("### Traffic & Timeline")

    daily_users = st.number_input(
        "Daily New Users",
        min_value=100,
        max_value=1000000,
        value=1000,
        step=100,
        help="Number of new users per day available for testing",
        key="ab_daily_users",
    )

    treatment_size = (
        st.slider(
            "Treatment Allocation (%)",
            min_value=10,
            max_value=90,
            value=50,
            step=5,
            help="Percentage of users allocated to treatment group",
            key="ab_treatment_size",
        )
        / 100
    )

    # Store in session state
    st.session_state.ab_params.update(
        {"daily_users": daily_users, "treatment_size": treatment_size}
    )


def render_ab_test_metric_parameters():
    """Render Metric Parameters section for A/B test calculator."""
    st.markdown("### Metric Parameters")

    test_metric = st.session_state.ab_params.get("test_metric", "Z-test (proportion)")

    if "Z-test" in test_metric:
        current_rate = (
            st.number_input(
                "Current Completion Rate (%)",
                min_value=0.1,
                max_value=99.9,
                value=15.0,
                step=0.1,
                help="Current conversion/completion rate of your control group",
                key="ab_current_rate",
            )
            / 100
        )

        mde_type = st.selectbox(
            "MDE Input Type",
            ["Absolute Change (percentage points)", "Relative Change (%)"],
            help="Specify MDE as absolute percentage points or relative percentage change",
            key="ab_mde_type",
        )

        if "Absolute" in mde_type:
            mde = (
                st.number_input(
                    "Minimum Detectable Effect (percentage points)",
                    min_value=0.1,
                    max_value=50.0,
                    value=2.0,
                    step=0.1,
                    help="Minimum absolute change in percentage points you want to detect",
                    key="ab_mde_abs",
                )
                / 100
            )
            new_rate = current_rate + mde
        else:
            relative_mde = st.number_input(
                "Minimum Detectable Effect (% relative change)",
                min_value=1.0,
                max_value=500.0,
                value=10.0,
                step=1.0,
                help="Minimum relative change percentage you want to detect",
                key="ab_mde_rel",
            )
            new_rate = current_rate * (1 + relative_mde / 100)
            mde = new_rate - current_rate

        # Store in session state
        st.session_state.ab_params.update(
            {
                "current_rate": current_rate,
                "mde_type": mde_type,
                "mde": mde,
                "new_rate": new_rate,
            }
        )

    else:  # Continuous metric
        current_mean = st.number_input(
            "Current Mean Value",
            min_value=0.0,
            value=100.0,
            step=1.0,
            help="Current mean value of your metric",
            key="ab_current_mean",
        )

        std_dev = st.number_input(
            "Standard Deviation",
            min_value=0.1,
            value=20.0,
            step=0.1,
            help="Standard deviation of your metric",
            key="ab_std_dev",
        )

        effect_size_input = st.number_input(
            "Minimum Detectable Effect",
            min_value=0.1,
            value=5.0,
            step=0.1,
            help="Minimum change in mean you want to detect",
            key="ab_effect_size",
        )

        # Calculate Cohen's d for t-test
        cohens_d = effect_size_input / std_dev

        # Store in session state
        st.session_state.ab_params.update(
            {
                "current_mean": current_mean,
                "std_dev": std_dev,
                "effect_size_input": effect_size_input,
                "cohens_d": cohens_d,
            }
        )


def render_ab_test_results():
    """Render Calculation Results section for A/B test calculator."""
    try:
        # Get parameters from session state
        ab_params = st.session_state.ab_params
        test_metric = ab_params.get("test_metric", "Z-test (proportion)")
        alpha = ab_params.get("alpha", 0.05)
        power = ab_params.get("power", 0.80)
        treatment_size = ab_params.get("treatment_size", 0.5)
        daily_users = ab_params.get("daily_users", 1000)

        # Always use two-sided test
        alternative = "two-sided"

        # Calculate sample size using statsmodels
        if "Z-test" in test_metric:
            power_analysis = NormalIndPower()

            current_rate = ab_params.get("current_rate", 0.15)
            mde = ab_params.get("mde", 0.02)

            # Calculate effect size using Cohen's h (correct for proportions)
            p1 = current_rate
            p2 = current_rate + mde
            effect_size = proportion_effectsize(p2, p1)  # Cohen's h

            # Calculate ratio for unequal allocation
            allocation_ratio = treatment_size / (1 - treatment_size)

            sample_size_control = power_analysis.solve_power(
                effect_size=effect_size,
                power=power,
                alpha=alpha,
                alternative=alternative,
                ratio=allocation_ratio,
            )
            sample_size_control = int(np.ceil(sample_size_control))
            sample_size_treatment = int(np.ceil(sample_size_control * allocation_ratio))

        else:  # Continuous metric
            power_analysis = TTestIndPower()
            cohens_d = ab_params.get("cohens_d", 0.25)

            allocation_ratio = treatment_size / (1 - treatment_size)

            sample_size_control = power_analysis.solve_power(
                effect_size=cohens_d,
                power=power,
                alpha=alpha,
                alternative=alternative,
                ratio=allocation_ratio,
            )
            sample_size_control = int(np.ceil(sample_size_control))
            sample_size_treatment = int(np.ceil(sample_size_control * allocation_ratio))

        st.markdown("---")
        st.markdown("### Calculation Results")

        # Horizontal layout for results
        total_sample = sample_size_control + sample_size_treatment

        # Duration calculation
        control_users_per_day = daily_users * (1 - treatment_size)
        treatment_users_per_day = daily_users * treatment_size

        # Duration is determined by whichever group takes longer to fill
        # Both groups must run for the same duration for validity
        days_for_control = np.ceil(sample_size_control / control_users_per_day)
        days_for_treatment = np.ceil(sample_size_treatment / treatment_users_per_day)
        duration = max(days_for_control, days_for_treatment)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Control Group Size",
                f"{sample_size_control:,}",
                help="Number of users needed in control group",
            )

        with col2:
            st.metric(
                "Treatment Group Size",
                f"{sample_size_treatment:,}",
                help="Number of users needed in treatment group",
            )

        with col3:
            st.metric(
                "Total Sample Size",
                f"{total_sample:,}",
                help="Total users needed for the test",
            )

        with col4:
            st.metric(
                "Test Duration",
                f"{int(duration)} days ({duration/7:.1f} weeks)",
                help="Test duration in days",
            )

        # Add Python code section
        from .code_generators import render_ab_test_python_code

        with st.expander("📋 Python Code", expanded=False):
            render_ab_test_python_code(
                ab_params,
                sample_size_control,
                sample_size_treatment,
                total_sample,
                duration,
            )

    except Exception as e:
        st.error(f"Error calculating A/B test sample size: {str(e)}")
