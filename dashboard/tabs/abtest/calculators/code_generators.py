"""Python code generators for A/B test calculations."""
import streamlit as st


def render_ab_test_python_code(
    ab_params, sample_size_control, sample_size_treatment, total_sample, duration
):
    """Render Python code for A/B test calculations."""
    test_metric = ab_params.get("test_metric", "Z-test (proportion)")
    alpha = ab_params.get("alpha", 0.05)
    power = ab_params.get("power", 0.80)
    treatment_size = ab_params.get("treatment_size", 0.5)
    daily_users = ab_params.get("daily_users", 1000)

    if "Z-test" in test_metric:
        current_rate = ab_params.get("current_rate", 0.15)
        mde = ab_params.get("mde", 0.02)
        new_rate = current_rate + mde
        st.code(
            f"""
# A/B Test Sample Size Calculation (Z-test for proportions)
import numpy as np
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

# Parameters
current_rate = {current_rate:.3f}  # {current_rate * 100:.1f}%
new_rate = {new_rate:.3f}  # {new_rate * 100:.1f}%
mde = {mde:.3f}  # {mde * 100:.1f} percentage points
power = {power:.2f}
alpha = {alpha:.3f}
treatment_allocation = {treatment_size:.1f}  # {treatment_size * 100:.0f}% treatment, {(1 - treatment_size) * 100:.0f}% control
daily_users = {daily_users}

# Calculate effect size (Cohen's h for proportions)
effect_size = proportion_effectsize(new_rate, current_rate)
print(f"Effect size (Cohen's h): {{effect_size:.4f}}")

# Calculate allocation ratio
allocation_ratio = treatment_allocation / (1 - treatment_allocation)
print(f"Allocation ratio: {{allocation_ratio:.3f}}")

# Sample size calculation
power_analysis = NormalIndPower()
sample_size_control = power_analysis.solve_power(
    effect_size=effect_size,
    power=power,
    alpha=alpha,
    alternative='two-sided',
    ratio=allocation_ratio
)

sample_size_control = int(np.ceil(sample_size_control))
sample_size_treatment = int(np.ceil(sample_size_control * allocation_ratio))
total_sample = sample_size_control + sample_size_treatment

print(f"Control group size: {{sample_size_control:,}}")
print(f"Treatment group size: {{sample_size_treatment:,}}")
print(f"Total sample size: {{total_sample:,}}")

# Duration calculation
control_users_per_day = daily_users * (1 - treatment_allocation)
treatment_users_per_day = daily_users * treatment_allocation
days_for_control = np.ceil(sample_size_control / control_users_per_day)
days_for_treatment = np.ceil(sample_size_treatment / treatment_users_per_day)
duration = max(days_for_control, days_for_treatment)

print(f"Test duration: {{int(duration)}} days ({{duration/7:.1f}} weeks)")
""",
            language="python",
        )
    else:  # t-test
        current_mean = ab_params.get("current_mean", 100.0)
        std_dev = ab_params.get("std_dev", 20.0)
        effect_size_input = ab_params.get("effect_size_input", 5.0)
        st.code(
            f"""
# A/B Test Sample Size Calculation (t-test for continuous metrics)
import numpy as np
from statsmodels.stats.power import TTestIndPower

# Parameters
current_mean = {current_mean:.1f}
std_dev = {std_dev:.1f}
effect_size = {effect_size_input:.1f}  # minimum detectable difference
power = {power:.2f}
alpha = {alpha:.3f}
treatment_allocation = {treatment_size:.1f}  # {treatment_size*100:.0f}% treatment, {(1-treatment_size)*100:.0f}% control
daily_users = {daily_users}

# Calculate Cohen's d
cohens_d = effect_size / std_dev
print(f"Cohen's d: {{cohens_d:.4f}}")

# Calculate allocation ratio
allocation_ratio = treatment_allocation / (1 - treatment_allocation)
print(f"Allocation ratio: {{allocation_ratio:.3f}}")

# Sample size calculation
power_analysis = TTestIndPower()
sample_size_control = power_analysis.solve_power(
    effect_size=cohens_d,
    power=power,
    alpha=alpha,
    alternative='two-sided',
    ratio=allocation_ratio
)

sample_size_control = int(np.ceil(sample_size_control))
sample_size_treatment = int(np.ceil(sample_size_control * allocation_ratio))
total_sample = sample_size_control + sample_size_treatment

print(f"Control group size: {{sample_size_control:,}}")
print(f"Treatment group size: {{sample_size_treatment:,}}")
print(f"Total sample size: {{total_sample:,}}")

# Duration calculation
control_users_per_day = daily_users * (1 - treatment_allocation)
treatment_users_per_day = daily_users * treatment_allocation
days_for_control = np.ceil(sample_size_control / control_users_per_day)
days_for_treatment = np.ceil(sample_size_treatment / treatment_users_per_day)
duration = max(days_for_control, days_for_treatment)

print(f"Test duration: {{int(duration)}} days ({{duration/7:.1f}} weeks)")
""",
            language="python",
        )


def render_multiple_treatment_python_code(
    multi_params, sample_size_control, sample_size_per_treatment, total_sample, duration
):
    """Render Python code for multiple treatment test calculations."""
    test_metric = multi_params.get("test_metric", "Z-test (proportion)")
    alpha = multi_params.get("alpha", 0.05)
    power = multi_params.get("power", 0.80)
    num_treatments = multi_params.get("num_treatments", 3)
    correction_method = multi_params.get("correction_method", "Bonferroni Method")
    treatment_allocation = multi_params.get("treatment_allocation", 0.75)
    daily_users = multi_params.get("daily_users", 1000)

    if "Bonferroni" in correction_method:
        correction_code = (
            "alpha_adjusted = alpha / num_treatments  # Bonferroni correction"
        )
        alpha_label = "Bonferroni adjusted alpha"
    else:
        correction_code = (
            "# FDR (Benjamini-Hochberg): alpha_adjusted = alpha (applied post-hoc)"
        )
        alpha_label = "FDR (B-H) alpha"

    if "Z-test" in test_metric:
        current_rate = multi_params.get("current_rate", 0.15)
        mde = multi_params.get("mde", 0.02)
        new_rate = current_rate + mde
        st.code(
            f"""
# Multiple Treatment Test Sample Size Calculation (Z-test for proportions)
import numpy as np
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

# Parameters
current_rate = {current_rate:.3f}  # {current_rate * 100:.1f}%
new_rate = {new_rate:.3f}  # {new_rate * 100:.1f}%
mde = {mde:.3f}  # {mde * 100:.1f} percentage points
power = {power:.2f}
alpha = {alpha:.3f}
num_treatments = {num_treatments}
treatment_allocation = {treatment_allocation:.2f}  # Total for all treatments
daily_users = {daily_users}

# {correction_method} for multiple comparisons
{correction_code}

# Calculate effect size (Cohen's h for proportions)
effect_size = proportion_effectsize(new_rate, current_rate)
print(f"Effect size (Cohen's h): {{effect_size:.4f}}")

# Calculate allocation ratio per group
control_allocation = 1 - treatment_allocation
allocation_ratio = (treatment_allocation / num_treatments) / control_allocation
print(f"Allocation ratio per group: {{allocation_ratio:.3f}}")

# Sample size calculation
power_analysis = NormalIndPower()
sample_size_control = power_analysis.solve_power(
    effect_size=effect_size,
    power=power,
    alpha=alpha,  # Use alpha_adjusted for Bonferroni
    alternative='two-sided',
    ratio=allocation_ratio
)

sample_size_control = int(np.ceil(sample_size_control))
sample_size_per_treatment = int(np.ceil(sample_size_control * allocation_ratio))
total_sample = sample_size_control + (sample_size_per_treatment * num_treatments)

print(f"Control group size: {{sample_size_control:,}}")
print(f"Per treatment group size: {{sample_size_per_treatment:,}}")
print(f"Total sample size: {{total_sample:,}}")

# Duration calculation
control_users_per_day = daily_users * control_allocation
treatment_users_per_day_per_group = daily_users * (treatment_allocation / num_treatments)
days_for_control = np.ceil(sample_size_control / control_users_per_day)
days_for_treatment = np.ceil(sample_size_per_treatment / treatment_users_per_day_per_group)
duration = max(days_for_control, days_for_treatment)

print(f"Test duration: {{int(duration)}} days ({{duration/7:.1f}} weeks)")
""",
            language="python",
        )
    else:  # t-test
        current_mean = multi_params.get("current_mean", 100.0)
        std_dev = multi_params.get("std_dev", 20.0)
        effect_size_input = multi_params.get("effect_size_input", 5.0)
        st.code(
            f"""
# Multiple Treatment Test Sample Size Calculation (t-test for continuous metrics)
import numpy as np
from statsmodels.stats.power import TTestIndPower

# Parameters
current_mean = {current_mean:.1f}
std_dev = {std_dev:.1f}
effect_size = {effect_size_input:.1f}  # minimum detectable difference
power = {power:.2f}
alpha = {alpha:.3f}
num_treatments = {num_treatments}
treatment_allocation = {treatment_allocation:.2f}  # Total for all treatments
daily_users = {daily_users}

# {correction_method} for multiple comparisons
{correction_code}

# Calculate Cohen's d
cohens_d = effect_size / std_dev
print(f"Cohen's d: {{cohens_d:.4f}}")

# Calculate allocation ratio per group
control_allocation = 1 - treatment_allocation
allocation_ratio = (treatment_allocation / num_treatments) / control_allocation
print(f"Allocation ratio per group: {{allocation_ratio:.3f}}")

# Sample size calculation
power_analysis = TTestIndPower()
sample_size_control = power_analysis.solve_power(
    effect_size=cohens_d,
    power=power,
    alpha=alpha,  # Use alpha_adjusted for Bonferroni
    alternative='two-sided',
    ratio=allocation_ratio
)

sample_size_control = int(np.ceil(sample_size_control))
sample_size_per_treatment = int(np.ceil(sample_size_control * allocation_ratio))
total_sample = sample_size_control + (sample_size_per_treatment * num_treatments)

print(f"Control group size: {{sample_size_control:,}}")
print(f"Per treatment group size: {{sample_size_per_treatment:,}}")
print(f"Total sample size: {{total_sample:,}}")

# Duration calculation
control_users_per_day = daily_users * control_allocation
treatment_users_per_day_per_group = daily_users * (treatment_allocation / num_treatments)
days_for_control = np.ceil(sample_size_control / control_users_per_day)
days_for_treatment = np.ceil(sample_size_per_treatment / treatment_users_per_day_per_group)
duration = max(days_for_control, days_for_treatment)

print(f"Test duration: {{int(duration)}} days ({{duration/7:.1f}} weeks)")
""",
            language="python",
        )
