"""SQL queries for LTV (Lifetime Value) analytics."""

REVENUE_SEGMENTATION_QUERY = """
SELECT * FROM `game-analytics.data_analyst_test_local.revenue_day1_20`
"""

RETENTION_RATE_QUERY = """
SELECT * FROM `game-analytics.data_analyst_test_local.retention_rate_day1_20`
"""

# Additional queries can be added here as needed
LTV_COHORT_QUERY = """
-- Placeholder for cohort analysis query
SELECT 'No data available' as message
"""

LTV_ROI_QUERY = """
-- Placeholder for ROI analysis query
SELECT 'No data available' as message
"""
