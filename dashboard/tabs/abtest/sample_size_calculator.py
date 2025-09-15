"""Sample size calculator for A/B testing using statistical packages."""
import streamlit as st
import numpy as np
import scipy.stats as stats
import pandas as pd
from statsmodels.stats.power import TTestIndPower, NormalIndPower


def render_sample_size_calculator_tab():
    """Render the sample size calculator tab."""
    
    # Create two main columns for different calculators with smaller gap
    left_col, gap_col, right_col = st.columns([4, 1, 4])
    
    # Initialize session state for both calculators
    if 'ab_params' not in st.session_state:
        st.session_state.ab_params = {}
    if 'multi_params' not in st.session_state:
        st.session_state.multi_params = {}
    
    # Render headers
    with left_col:
        st.markdown("""
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 10px; border-left: 5px solid #2196f3;">
        <p style="color: #1976d2; margin-bottom: 0;"><strong>1 CONTROL VS 1 TREATMENT</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with right_col:
        st.markdown("""
        <div style="background-color: #f3e5f5; padding: 15px; border-radius: 10px; border-left: 5px solid #9c27b0;">
        <p style="color: #7b1fa2; margin-bottom: 0;"><strong>1 CONTROL VS MULTIPLE TREATMENTS (BONFERRONI METHOD)</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Section 1: Test Configuration
    render_test_configuration_section(left_col, right_col)
    
    # Section 2: Traffic & Timeline
    render_traffic_timeline_section(left_col, right_col)
    
    # Section 3: Metric Parameters
    render_metric_parameters_section(left_col, right_col)
    
    # Section 4: Calculation Results
    render_calculation_results_section(left_col, right_col)


def render_test_configuration_section(left_col, right_col):
    """Render Test Configuration section for both calculators."""
    
    with left_col:
        st.markdown("### Test Configuration")
        
        # Test type selection
        test_metric = st.selectbox(
            "Test Type",
            ["Z-test (proportion)", "t-test (continuous)"],
            help="Choose the type of metric you're testing",
            key="ab_test_metric"
        )
        
        # Statistical parameters
        alpha = st.slider(
            "Significance Level (α)",
            min_value=0.01,
            max_value=0.10,
            value=0.05,
            step=0.01,
            help="Probability of Type I error (false positive). Common values: 0.05, 0.01",
            key="ab_alpha"
        )
        
        power = st.slider(
            "Statistical Power (1-β)",
            min_value=0.70,
            max_value=0.95,
            value=0.80,
            step=0.05,
            help="Probability of detecting an effect if it exists. Common values: 0.80, 0.90",
            key="ab_power"
        )
        
        # Store in session state
        st.session_state.ab_params.update({
            'test_metric': test_metric,
            'alpha': alpha,
            'power': power
        })
    
    with right_col:
        st.markdown("### Test Configuration")
        
        # Test type selection
        multi_test_metric = st.selectbox(
            "Test Type",
            ["Z-test (proportion)", "t-test (continuous)"],
            help="Choose the type of metric you're testing",
            key="multi_test_metric"
        )
        
        # Number of treatment groups
        num_treatments = st.slider(
            "Number of Treatment Groups",
            min_value=2,
            max_value=5,
            value=3,
            step=1,
            help="Number of treatment variations (excluding control)",
            key="multi_num_treatments"
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
            key="multi_alpha"
        )
        
        multi_power = st.slider(
            "Statistical Power (1-β)",
            min_value=0.70,
            max_value=0.95,
            value=0.80,
            step=0.01,
            format="%.2f",
            help="Probability of detecting a true effect",
            key="multi_power"
        )
        
        # Store in session state
        st.session_state.multi_params.update({
            'test_metric': multi_test_metric,
            'num_treatments': num_treatments,
            'alpha': multi_alpha,
            'power': multi_power
        })


def render_traffic_timeline_section(left_col, right_col):
    """Render Traffic & Timeline section for both calculators."""
    
    with left_col:
        st.markdown("### Traffic & Timeline")
        
        daily_users = st.number_input(
            "Daily New Users",
            min_value=100,
            max_value=1000000,
            value=1000,
            step=100,
            help="Number of new users per day available for testing",
            key="ab_daily_users"
        )
        
        treatment_size = st.slider(
            "Treatment Allocation (%)",
            min_value=10,
            max_value=90,
            value=50,
            step=5,
            help="Percentage of users allocated to treatment group",
            key="ab_treatment_size"
        ) / 100
        
        # Store in session state
        st.session_state.ab_params.update({
            'daily_users': daily_users,
            'treatment_size': treatment_size
        })
    
    with right_col:
        st.markdown("### Traffic & Timeline")
        
        multi_daily_users = st.number_input(
            "Daily New Users",
            min_value=100,
            max_value=100000,
            value=1000,
            step=100,
            help="Number of new users available per day for testing",
            key="multi_daily_users"
        )
        
        treatment_allocation = st.slider(
            "Total Treatment Allocation (%)",
            min_value=50,
            max_value=90,
            value=75,
            step=5,
            help="Percentage of users allocated to all treatment groups combined",
            key="multi_treatment_allocation"
        ) / 100
        
        # Store in session state
        st.session_state.multi_params.update({
            'daily_users': multi_daily_users,
            'treatment_allocation': treatment_allocation
        })


def render_metric_parameters_section(left_col, right_col):
    """Render Metric Parameters section for both calculators."""
    
    with left_col:
        st.markdown("### Metric Parameters")
        
        test_metric = st.session_state.ab_params.get('test_metric', 'Z-test (proportion)')
        
        if "Z-test" in test_metric:
            current_rate = st.number_input(
                "Current Completion Rate (%)",
                min_value=0.1,
                max_value=99.9,
                value=15.0,
                step=0.1,
                help="Current conversion/completion rate of your control group",
                key="ab_current_rate"
            ) / 100
            
            mde_type = st.selectbox(
                "MDE Input Type",
                ["Absolute Change (percentage points)", "Relative Change (%)"],
                help="Specify MDE as absolute percentage points or relative percentage change",
                key="ab_mde_type"
            )
            
            if "Absolute" in mde_type:
                mde = st.number_input(
                    "Minimum Detectable Effect (percentage points)",
                    min_value=0.1,
                    max_value=50.0,
                    value=2.0,
                    step=0.1,
                    help="Minimum absolute change in percentage points you want to detect",
                    key="ab_mde_abs"
                ) / 100
                new_rate = current_rate + mde
            else:
                relative_mde = st.number_input(
                    "Minimum Detectable Effect (% relative change)",
                    min_value=1.0,
                    max_value=500.0,
                    value=10.0,
                    step=1.0,
                    help="Minimum relative change percentage you want to detect",
                    key="ab_mde_rel"
                )
                new_rate = current_rate * (1 + relative_mde / 100)
                mde = new_rate - current_rate
                
            # Store in session state
            st.session_state.ab_params.update({
                'current_rate': current_rate,
                'mde_type': mde_type,
                'mde': mde,
                'new_rate': new_rate
            })
                
        else:  # Continuous metric
            current_mean = st.number_input(
                "Current Mean Value",
                min_value=0.0,
                value=100.0,
                step=1.0,
                help="Current mean value of your metric",
                key="ab_current_mean"
            )
            
            std_dev = st.number_input(
                "Standard Deviation",
                min_value=0.1,
                value=20.0,
                step=0.1,
                help="Standard deviation of your metric",
                key="ab_std_dev"
            )
            
            effect_size_input = st.number_input(
                "Minimum Detectable Effect",
                min_value=0.1,
                value=5.0,
                step=0.1,
                help="Minimum change in mean you want to detect",
                key="ab_effect_size"
            )
            
            # Calculate Cohen's d for t-test
            cohens_d = effect_size_input / std_dev
            
            # Store in session state
            st.session_state.ab_params.update({
                'current_mean': current_mean,
                'std_dev': std_dev,
                'effect_size_input': effect_size_input,
                'cohens_d': cohens_d
            })
    
    with right_col:
        st.markdown("### Metric Parameters")
        
        multi_test_metric = st.session_state.multi_params.get('test_metric', 'Z-test (proportion)')
        
        if "Z-test" in multi_test_metric:
            multi_current_rate = st.number_input(
                "Current Completion Rate (%)",
                min_value=0.1,
                max_value=99.9,
                value=15.0,
                step=0.1,
                help="Current conversion/completion rate of your control group",
                key="multi_current_rate"
            ) / 100
            
            multi_mde_type = st.selectbox(
                "MDE Input Type",
                ["Absolute Change (percentage points)", "Relative Change (%)"],
                help="Specify MDE as absolute percentage points or relative percentage change",
                key="multi_mde_type"
            )
            
            if "Absolute" in multi_mde_type:
                multi_mde = st.number_input(
                    "Minimum Detectable Effect (percentage points)",
                    min_value=0.1,
                    max_value=50.0,
                    value=2.0,
                    step=0.1,
                    help="Minimum absolute change in percentage points you want to detect",
                    key="multi_mde_abs"
                ) / 100
                multi_new_rate = multi_current_rate + multi_mde
            else:
                multi_relative_mde = st.number_input(
                    "Minimum Detectable Effect (% relative change)",
                    min_value=1.0,
                    max_value=500.0,
                    value=10.0,
                    step=1.0,
                    help="Minimum relative change percentage you want to detect",
                    key="multi_mde_rel"
                )
                multi_new_rate = multi_current_rate * (1 + multi_relative_mde / 100)
                multi_mde = multi_new_rate - multi_current_rate
                
            # Store in session state
            st.session_state.multi_params.update({
                'current_rate': multi_current_rate,
                'mde_type': multi_mde_type,
                'mde': multi_mde,
                'new_rate': multi_new_rate
            })
        else:
            multi_current_mean = st.number_input(
                "Current Mean Value",
                min_value=0.0,
                value=100.0,
                step=1.0,
                help="Current mean value of your metric",
                key="multi_current_mean"
            )
            
            multi_std_dev = st.number_input(
                "Standard Deviation",
                min_value=0.1,
                value=20.0,
                step=0.1,
                help="Standard deviation of your metric",
                key="multi_std_dev"
            )
            
            multi_effect_size_input = st.number_input(
                "Minimum Detectable Effect",
                min_value=0.1,
                value=5.0,
                step=0.1,
                help="Minimum change in mean you want to detect",
                key="multi_effect_size"
            )
            
            # Calculate Cohen's d for t-test
            multi_cohens_d = multi_effect_size_input / multi_std_dev
            
            # Store in session state
            st.session_state.multi_params.update({
                'current_mean': multi_current_mean,
                'std_dev': multi_std_dev,
                'effect_size_input': multi_effect_size_input,
                'cohens_d': multi_cohens_d
            })


def render_calculation_results_section(left_col, right_col):
    """Render Calculation Results section for both calculators."""
    
    with left_col:
        try:
            # Get parameters from session state
            ab_params = st.session_state.ab_params
            test_metric = ab_params.get('test_metric', 'Z-test (proportion)')
            alpha = ab_params.get('alpha', 0.05)
            power = ab_params.get('power', 0.80)
            treatment_size = ab_params.get('treatment_size', 0.5)
            daily_users = ab_params.get('daily_users', 1000)
            
            # Always use two-sided test
            alternative = 'two-sided'
            
            # Calculate sample size using statsmodels
            if "Z-test" in test_metric:
                power_analysis = NormalIndPower()
                
                current_rate = ab_params.get('current_rate', 0.15)
                mde = ab_params.get('mde', 0.02)
                
                # Calculate effect size (standardized difference)
                diff = mde
                p1 = current_rate
                p2 = current_rate + diff
                pooled_var = np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
                effect_size = diff / pooled_var
                
                # Calculate ratio for unequal allocation
                allocation_ratio = treatment_size / (1 - treatment_size)
                
                sample_size_control = power_analysis.solve_power(
                    effect_size=effect_size,
                    power=power,
                    alpha=alpha,
                    alternative=alternative,
                    ratio=allocation_ratio
                )
                sample_size_control = int(np.ceil(sample_size_control))
                sample_size_treatment = int(np.ceil(sample_size_control * allocation_ratio))
                
            else:  # Continuous metric
                power_analysis = TTestIndPower()
                cohens_d = ab_params.get('cohens_d', 0.25)
                
                allocation_ratio = treatment_size / (1 - treatment_size)
                
                sample_size_control = power_analysis.solve_power(
                    effect_size=cohens_d,
                    power=power,
                    alpha=alpha,
                    alternative=alternative,
                    ratio=allocation_ratio
                )
                sample_size_control = int(np.ceil(sample_size_control))
                sample_size_treatment = int(np.ceil(sample_size_control * allocation_ratio))
            
            st.markdown("---")
            st.markdown("### Calculation Results")
            
            st.metric(
                "Control Group Size",
                f"{sample_size_control:,}",
                help="Number of users needed in control group"
            )
            
            st.metric(
                "Treatment Group Size", 
                f"{sample_size_treatment:,}",
                help="Number of users needed in treatment group"
            )
            
            total_sample = sample_size_control + sample_size_treatment
            st.metric(
                "Total Sample Size",
                f"{total_sample:,}",
                help="Total users needed for the test"
            )
            
            # Duration calculation
            st.markdown("### Timeline")
            
            duration = np.ceil(total_sample / daily_users)
            st.metric(
                "Test Duration",
                f"{int(duration)} days",
                help="Estimated days to reach required sample size"
            )
            
            # Show Python code used for A/B test
            with st.expander("Python Code Used", expanded=False):
                if "Z-test" in test_metric:
                    st.markdown("**Z-test for Proportions:**")
                    
                    # Calculate the actual values for display
                    mde_type = ab_params.get('mde_type', 'Absolute Change (percentage points)')
                    if "Absolute" in mde_type:
                        mde_display = f"mde = {mde:.4f}"
                    else:
                        current_rate = ab_params.get('current_rate', 0.15)
                        new_rate = ab_params.get('new_rate', 0.165)
                        relative_change = ((new_rate - current_rate) / current_rate) * 100
                        mde_display = f"relative_change = {relative_change:.1f}%\nnew_rate = {current_rate:.3f} * (1 + {relative_change/100:.3f}) = {new_rate:.3f}\nmde = {new_rate:.3f} - {current_rate:.3f} = {mde:.4f}"
                    
                    st.code(f"""
from statsmodels.stats.power import NormalIndPower
import numpy as np

# Parameters
current_rate = {current_rate:.3f}
{mde_display}
power = {power}
alpha = {alpha}
allocation_ratio = {treatment_size:.2f} / {1-treatment_size:.2f} = {treatment_size/(1-treatment_size):.3f}

# Standardized effect size for proportions
p1 = {current_rate:.3f}
p2 = {current_rate:.3f} + {mde:.4f} = {current_rate + mde:.3f}
pooled_var = sqrt(p1 * (1 - p1) + p2 * (1 - p2)) = {np.sqrt(current_rate * (1 - current_rate) + (current_rate + mde) * (1 - (current_rate + mde))):.4f}
effect_size = {mde:.4f} / {np.sqrt(current_rate * (1 - current_rate) + (current_rate + mde) * (1 - (current_rate + mde))):.4f} = {mde / np.sqrt(current_rate * (1 - current_rate) + (current_rate + mde) * (1 - (current_rate + mde))):.4f}

# Sample size calculation (two-sided test)
power_analysis = NormalIndPower()
sample_size_control = power_analysis.solve_power(
    effect_size={effect_size:.4f},
    power={power},
    alpha={alpha},
    alternative='two-sided',
    ratio={treatment_size/(1-treatment_size):.3f}
)

sample_size_control = {sample_size_control}
sample_size_treatment = {sample_size_treatment}
total_sample = {total_sample}
""", language="python")
                else:
                    st.markdown("**t-test for Continuous Metrics:**")
                    cohens_d = ab_params.get('cohens_d', 0.25)
                    current_mean = ab_params.get('current_mean', 100)
                    std_dev = ab_params.get('std_dev', 20)
                    effect_size_input = ab_params.get('effect_size_input', 5)
                    
                    st.code(f"""
from statsmodels.stats.power import TTestIndPower

# Parameters
current_mean = {current_mean}
std_dev = {std_dev}
effect_size = {effect_size_input}
power = {power}
alpha = {alpha}
allocation_ratio = {treatment_size:.2f} / {1-treatment_size:.2f} = {treatment_size/(1-treatment_size):.3f}

# Cohen's d calculation
cohens_d = effect_size / std_dev = {effect_size_input} / {std_dev} = {cohens_d:.3f}

# Sample size calculation (two-sided test)
power_analysis = TTestIndPower()
sample_size_control = power_analysis.solve_power(
    effect_size={cohens_d:.3f},
    power={power},
    alpha={alpha},
    alternative='two-sided',
    ratio={treatment_size/(1-treatment_size):.3f}
)

sample_size_control = {sample_size_control}
sample_size_treatment = {sample_size_treatment}
total_sample = {total_sample}
""", language="python")
            
        except Exception as e:
            st.error(f"Error calculating A/B test sample size: {str(e)}")
    
    with right_col:
        try:
            # Get parameters from session state
            multi_params = st.session_state.multi_params
            test_metric = multi_params.get('test_metric', 'Z-test (proportion)')
            alpha = multi_params.get('alpha', 0.05)
            power = multi_params.get('power', 0.80)
            num_treatments = multi_params.get('num_treatments', 3)
            treatment_allocation = multi_params.get('treatment_allocation', 0.75)
            daily_users = multi_params.get('daily_users', 1000)
            
            # Bonferroni correction for multiple comparisons
            alpha_adjusted = alpha / num_treatments
            
            # Calculate sample size using statsmodels
            if "Z-test" in test_metric:
                power_analysis = NormalIndPower()
                
                current_rate = multi_params.get('current_rate', 0.15)
                mde = multi_params.get('mde', 0.02)
                
                # Calculate effect size (standardized difference)
                diff = mde
                p1 = current_rate
                p2 = current_rate + diff
                pooled_var = np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
                effect_size = diff / pooled_var
                
                # Equal allocation among treatment groups
                treatment_per_group = treatment_allocation / num_treatments
                control_allocation = 1 - treatment_allocation
                allocation_ratio = treatment_per_group / control_allocation
                
                sample_size_control = power_analysis.solve_power(
                    effect_size=effect_size,
                    power=power,
                    alpha=alpha_adjusted,
                    alternative='two-sided',
                    ratio=allocation_ratio
                )
                sample_size_control = int(np.ceil(sample_size_control))
                sample_size_per_treatment = int(np.ceil(sample_size_control * allocation_ratio))
                
            else:  # Continuous metric
                power_analysis = TTestIndPower()
                cohens_d = multi_params.get('cohens_d', 0.25)
                
                treatment_per_group = treatment_allocation / num_treatments
                control_allocation = 1 - treatment_allocation
                allocation_ratio = treatment_per_group / control_allocation
                
                sample_size_control = power_analysis.solve_power(
                    effect_size=cohens_d,
                    power=power,
                    alpha=alpha_adjusted,
                    alternative='two-sided',
                    ratio=allocation_ratio
                )
                sample_size_control = int(np.ceil(sample_size_control))
                sample_size_per_treatment = int(np.ceil(sample_size_control * allocation_ratio))
            
            st.markdown("---")
            st.markdown("### Calculation Results")
            
            st.metric(
                "Control Group Size",
                f"{sample_size_control:,}",
                help="Number of users needed in control group"
            )
            
            st.metric(
                "Per Treatment Group",
                f"{sample_size_per_treatment:,}",
                help="Number of users needed in each treatment group"
            )
            
            total_sample = sample_size_control + (sample_size_per_treatment * num_treatments)
            st.metric(
                "Total Sample Size",
                f"{total_sample:,}",
                help="Total users needed for the test"
            )
            
            # Duration calculation
            st.markdown("### Timeline")
            
            duration = np.ceil(total_sample / daily_users)
            st.metric(
                "Test Duration",
                f"{int(duration)} days",
                help="Estimated days to reach required sample size"
            )
            
            st.metric(
                "Adjusted Alpha",
                f"{alpha_adjusted:.4f}",
                help="Alpha level after Bonferroni correction for multiple comparisons"
            )
            
            # Show Python code used for Multiple Treatment test
            with st.expander("Python Code Used", expanded=False):
                if "Z-test" in test_metric:
                    st.markdown("**Z-test for Multiple Treatments:**")
                    
                    # Calculate the actual values for display
                    mde_type = multi_params.get('mde_type', 'Absolute Change (percentage points)')
                    if "Absolute" in mde_type:
                        mde_display = f"mde = {mde:.4f}"
                    else:
                        current_rate = multi_params.get('current_rate', 0.15)
                        new_rate = multi_params.get('new_rate', 0.165)
                        relative_change = ((new_rate - current_rate) / current_rate) * 100
                        mde_display = f"relative_change = {relative_change:.1f}%\nnew_rate = {current_rate:.3f} * (1 + {relative_change/100:.3f}) = {new_rate:.3f}\nmde = {new_rate:.3f} - {current_rate:.3f} = {mde:.4f}"
                    
                    st.code(f"""
from statsmodels.stats.power import NormalIndPower
import numpy as np

# Parameters
current_rate = {current_rate:.3f}
{mde_display}
power = {power}
alpha = {alpha}
num_treatments = {num_treatments}
treatment_allocation = {treatment_allocation:.2f}

# Bonferroni correction
alpha_adjusted = {alpha} / {num_treatments} = {alpha_adjusted:.4f}  # Bonferroni correction

# Allocation calculations
treatment_per_group = {treatment_allocation:.2f} / {num_treatments} = {treatment_per_group:.3f}
control_allocation = 1 - {treatment_allocation:.2f} = {control_allocation:.3f}
allocation_ratio = {treatment_per_group:.3f} / {control_allocation:.3f} = {allocation_ratio:.3f}

# Standardized effect size for proportions
p1 = {current_rate:.3f}
p2 = {current_rate:.3f} + {mde:.4f} = {current_rate + mde:.3f}
pooled_var = sqrt(p1 * (1 - p1) + p2 * (1 - p2)) = {pooled_var:.4f}
effect_size = {mde:.4f} / {pooled_var:.4f} = {effect_size:.4f}

# Sample size calculation (two-sided test with Bonferroni correction)
power_analysis = NormalIndPower()
sample_size_control = power_analysis.solve_power(
    effect_size={effect_size:.4f},
    power={power},
    alpha={alpha_adjusted:.4f},
    alternative='two-sided',
    ratio={allocation_ratio:.3f}
)

sample_size_control = {sample_size_control}
sample_size_per_treatment = {sample_size_per_treatment}
total_sample = {total_sample}
""", language="python")
                else:
                    st.markdown("**t-test for Multiple Treatments:**")
                    cohens_d = multi_params.get('cohens_d', 0.25)
                    current_mean = multi_params.get('current_mean', 100)
                    std_dev = multi_params.get('std_dev', 20)
                    effect_size_input = multi_params.get('effect_size_input', 5)
                    
                    st.code(f"""
from statsmodels.stats.power import TTestIndPower

# Parameters
current_mean = {current_mean}
std_dev = {std_dev}
effect_size = {effect_size_input}
power = {power}
alpha = {alpha}
num_treatments = {num_treatments}
treatment_allocation = {treatment_allocation:.2f}

# Bonferroni correction
alpha_adjusted = {alpha} / {num_treatments} = {alpha_adjusted:.4f}  # Bonferroni correction

# Allocation calculations
treatment_per_group = {treatment_allocation:.2f} / {num_treatments} = {treatment_per_group:.3f}
control_allocation = 1 - {treatment_allocation:.2f} = {control_allocation:.3f}
allocation_ratio = {treatment_per_group:.3f} / {control_allocation:.3f} = {allocation_ratio:.3f}

# Cohen's d calculation
cohens_d = effect_size / std_dev = {effect_size_input} / {std_dev} = {cohens_d:.3f}

# Sample size calculation (two-sided test with Bonferroni correction)
power_analysis = TTestIndPower()
sample_size_control = power_analysis.solve_power(
    effect_size={cohens_d:.3f},
    power={power},
    alpha={alpha_adjusted:.4f},
    alternative='two-sided',
    ratio={allocation_ratio:.3f}
)

sample_size_control = {sample_size_control}
sample_size_per_treatment = {sample_size_per_treatment}
total_sample = {total_sample}
""", language="python")
            
        except Exception as e:
            st.error(f"Error calculating multiple treatment sample size: {str(e)}")
