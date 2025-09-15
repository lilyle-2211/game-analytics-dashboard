"""Data processing utilities for LTV analytics."""
import pandas as pd


def create_revenue_segmentation(df):
    """Create revenue segmentation table."""

    # Find revenue columns
    revenue_cols = [col for col in df.columns if col.startswith("revenue_day_")]
    revenue_cols = sorted(revenue_cols, key=lambda x: int(x.split("_")[-1]))

    # Use Day 20 cumulative revenue
    df_analysis = df.copy()
    df_analysis["total_revenue_day_20"] = df_analysis["revenue_day_20"]

    # Create segments based on revenue quantiles
    paying_users = df_analysis[df_analysis["total_revenue_day_20"] > 0]

    if len(paying_users) == 0:
        return pd.DataFrame()

    # Define quantiles and labels
    quantiles = [0, 0.25, 0.5, 0.75, 0.90, 0.95, 1.0]
    revenue_thresholds = paying_users["total_revenue_day_20"].quantile(quantiles).values

    segment_labels = [
        "Non-Payer",
        "Low Spender",
        "Medium Spender",
        "High Spender",
        "Premium",
        "VIP",
        "Whale",
    ]

    # Assign segments
    def assign_segment(revenue):
        if revenue == 0:
            return "Non-Payer"
        for i in range(1, len(revenue_thresholds)):
            if revenue <= revenue_thresholds[i]:
                return segment_labels[i]
        return segment_labels[-1]

    df_analysis["segment"] = df_analysis["total_revenue_day_20"].apply(assign_segment)

    # Create table
    results = []
    total_users = len(df_analysis)
    total_revenue = df_analysis["total_revenue_day_20"].sum()

    for segment in segment_labels:
        segment_data = df_analysis[df_analysis["segment"] == segment]

        if len(segment_data) == 0:
            continue

        row = {"segment": segment, "num_user": len(segment_data)}

        # LTV 20 day total for this segment
        row["ltv_20_day"] = segment_data["total_revenue_day_20"].sum()

        # Average LTV per user for each day (day 20 to day 1)
        for i in range(20, 0, -1):
            col_name = f"revenue_day_{i}"
            if col_name in revenue_cols:
                row[f"avg_ltv_{i}_day_per_user"] = segment_data[col_name].mean()

        # Percentages
        row["pct_user"] = (len(segment_data) / total_users) * 100
        row["pct_ltv_20_day_per_segment"] = (
            (row["ltv_20_day"] / total_revenue) * 100 if total_revenue > 0 else 0
        )

        results.append(row)

    return pd.DataFrame(results)


def create_segment_plot_data(df):
    """Prepare data for segment visualization plots."""

    # Find revenue columns for plotting
    revenue_cols = [col for col in df.columns if col.startswith("revenue_day_")]
    revenue_cols = sorted(revenue_cols, key=lambda x: int(x.split("_")[-1]))

    if len(revenue_cols) == 0:
        return pd.DataFrame()

    # Create segments first
    df_analysis = df.copy()
    df_analysis["total_revenue_day_20"] = df_analysis.get("revenue_day_20", 0)

    # Create segments based on revenue quantiles
    paying_users = df_analysis[df_analysis["total_revenue_day_20"] > 0]

    if len(paying_users) == 0:
        return pd.DataFrame()

    # Define quantiles and labels
    quantiles = [0, 0.25, 0.5, 0.75, 0.90, 0.95, 1.0]
    revenue_thresholds = paying_users["total_revenue_day_20"].quantile(quantiles).values

    segment_labels = [
        "Non-Payer",
        "Low Spender",
        "Medium Spender",
        "High Spender",
        "Premium",
        "VIP",
        "Whale",
    ]

    # Assign segments
    def assign_segment(revenue):
        if revenue == 0:
            return "Non-Payer"
        for i in range(1, len(revenue_thresholds)):
            if revenue <= revenue_thresholds[i]:
                return segment_labels[i]
        return segment_labels[-1]

    df_analysis["segment"] = df_analysis["total_revenue_day_20"].apply(assign_segment)

    # Create plot data - average revenue per user by day for each segment
    plot_data = []

    for segment in segment_labels:
        segment_data = df_analysis[df_analysis["segment"] == segment]

        if len(segment_data) == 0:
            continue

        for col in revenue_cols:
            day = int(col.split("_")[-1])
            avg_revenue = segment_data[col].mean()

            plot_data.append(
                {"segment": segment, "day": day, "avg_revenue_per_user": avg_revenue}
            )

    return pd.DataFrame(plot_data)


def create_retention_curve_data(df):
    """Prepare retention rate data for curve plotting with 90-day projection."""

    if df.empty:
        return pd.DataFrame()

    # Import required libraries for modeling
    import numpy as np
    from scipy.optimize import curve_fit

    # Find retention columns
    retention_cols = [col for col in df.columns if col.endswith("_retention_pct")]
    retention_cols = sorted(retention_cols, key=lambda x: int(x.split("_")[1]))

    if len(retention_cols) == 0:
        return pd.DataFrame()

    # Extract actual retention data (days 1-20)
    actual_retention_values = df[retention_cols].iloc[0].values
    retention_fraction = actual_retention_values / 100.0  # convert to fraction
    days_1_20 = np.arange(1, 21)

    # Define Weibull model with conservative adjustment
    def weibull(t, lambda_, gamma):
        base_retention = np.exp(-((t / lambda_) ** gamma))
        # Apply conservative adjustment for projections beyond day 20
        if hasattr(t, "__iter__"):  # Handle array input
            adjustment = np.where(t > 20, 0.85 ** ((t - 20) / 10), 1.0)
            return base_retention * adjustment
        else:  # Handle scalar input
            if t > 20:
                adjustment = 0.85 ** ((t - 20) / 10)  # 15% additional decay per 10 days
                return base_retention * adjustment
            return base_retention

    try:
        # Fit Weibull model to actual data with conservative parameters
        p0 = [10, 1.2]  # More conservative: lower lambda, higher shape for faster decay
        bounds = ([1, 0.1], [50, 5.0])  # Realistic bounds: lambda 1-50, shape 0.1-5.0

        # Weight recent data more heavily (days 10-20 get more weight)
        weights = np.linspace(0.5, 2.0, len(days_1_20))

        params, _ = curve_fit(
            weibull,
            days_1_20,
            retention_fraction,
            p0=p0,
            bounds=bounds,
            sigma=1 / weights,
        )
        lambda_, gamma = params

        # Project retention for days 1-90
        all_days = np.arange(1, 91)
        projected_retention = weibull(all_days, lambda_, gamma)

        # Create plot data
        plot_data = []

        # Add actual data (days 1-20)
        for i, day in enumerate(days_1_20):
            plot_data.append(
                {
                    "day": day,
                    "retention_rate": actual_retention_values[i],
                    "type": "Actual",
                }
            )

        # Add projected data (days 1-90)
        for day in all_days:
            plot_data.append(
                {
                    "day": day,
                    "retention_rate": projected_retention[day - 1] * 100,
                    "type": "Projected",
                }
            )

        return pd.DataFrame(plot_data)

    except Exception as e:
        # If fitting fails, return only actual data
        plot_data = []
        for i, day in enumerate(days_1_20):
            plot_data.append(
                {
                    "day": day,
                    "retention_rate": actual_retention_values[i],
                    "type": "Actual",
                }
            )
        return pd.DataFrame(plot_data)


def project_90_day_ltv_simple(segmentation_df, retention_df=None, raw_revenue_df=None):
    """Project 90-day LTV using actual daily revenue data from SQL table"""

    import numpy as np
    from scipy.optimize import curve_fit

    results = []

    for _, row in segmentation_df.iterrows():
        segment = row["segment"]
        num_users = row["num_user"]
        ltv_20_day_total = row["ltv_20_day"]

        # Get avg LTV at day 20 (cumulative)
        avg_ltv_20_day_per_user = row.get(
            "avg_ltv_20_day_per_user",
            ltv_20_day_total / num_users if num_users > 0 else 0,
        )

        # Skip Non-Payers
        if segment == "Non-Payer":
            results.append(
                {
                    "segment": segment,
                    "num_user": num_users,
                    "ltv_20_day": ltv_20_day_total,
                    "avg_daily_revenue_per_user": 0.00,
                    "avg_ltv_20_day_per_user": avg_ltv_20_day_per_user,
                    "projected_avg_90_day_per_user": 0.00,
                }
            )
            continue

        projected_90 = None

        # Calculate correct average daily revenue per user
        # Formula: total_LTV_20_day / (num_users * 20_days)
        if num_users > 0:
            avg_daily_revenue = ltv_20_day_total / (num_users * 20)
        else:
            avg_daily_revenue = 0.00

        # Use retention data for 90-day projection if available
        if (
            retention_df is not None
            and not retention_df.empty
            and avg_daily_revenue > 0
        ):
            try:
                # Get retention rates for days 1-20
                retention_cols = [f"day_{i}_retention_pct" for i in range(1, 21)]
                retention_rates = []
                for col in retention_cols:
                    if col in retention_df.columns:
                        retention_rates.append(retention_df[col].iloc[0])

                if len(retention_rates) >= 15:  # Need sufficient data points
                    # Project using Weibull model
                    days = np.array(range(1, 21))
                    retention_vals = np.array(retention_rates[:20]) / 100.0

                    def weibull(t, lambda_, k):
                        base_retention = np.exp(-((t / lambda_) ** k))
                        # Apply conservative adjustment for projections beyond day 20
                        if hasattr(t, "__iter__"):  # Handle array input
                            adjustment = np.where(t > 20, 0.85 ** ((t - 20) / 10), 1.0)
                            return base_retention * adjustment
                        else:  # Handle scalar input
                            if t > 20:
                                adjustment = 0.85 ** (
                                    (t - 20) / 10
                                )  # 15% additional decay per 10 days
                                return base_retention * adjustment
                            return base_retention

                    if retention_vals[-1] > 0:
                        try:
                            # More conservative parameters and bounds
                            p0 = [10, 1.2]
                            bounds = ([1, 0.1], [50, 5.0])

                            # Weight recent data more heavily
                            weights = np.linspace(0.5, 2.0, len(days))

                            params, _ = curve_fit(
                                weibull,
                                days,
                                retention_vals,
                                p0=p0,
                                bounds=bounds,
                                sigma=1 / weights,
                            )
                            lambda_param, k = params

                            # Project to day 90 using the calculated daily revenue
                            projected_90 = (
                                avg_ltv_20_day_per_user  # Start with day 20 LTV
                            )

                            for day in range(21, 91):
                                day_retention = weibull(day, lambda_param, k)
                                projected_90 += avg_daily_revenue * day_retention

                        except (ValueError, RuntimeError):
                            projected_90 = None

            except Exception:
                projected_90 = None

        # If no projection possible, use current 20-day value
        if projected_90 is None:
            projected_90 = avg_ltv_20_day_per_user

        results.append(
            {
                "segment": segment,
                "num_user": num_users,
                "ltv_20_day": ltv_20_day_total,
                "avg_daily_revenue_per_user": avg_daily_revenue,
                "avg_ltv_20_day_per_user": avg_ltv_20_day_per_user,
                "projected_avg_90_day_per_user": projected_90,
            }
        )

    return pd.DataFrame(results)
