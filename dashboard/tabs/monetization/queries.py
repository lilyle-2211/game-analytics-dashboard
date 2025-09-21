"""SQL queries for monetization analytics."""

ANOMALY_TRANSACTIONS_QUERY = """
-- SQL Query to identify statistical outliers in transaction data
WITH transaction_stats AS (
  SELECT
    revenue_type,
    AVG(transaction_value) AS avg_transaction,
    AVG(transaction_value) * 100 AS threshold_100x -- 100x average threshold
  FROM `game-analytics.data_analyst_test_local.revenues`
  WHERE transaction_value > 0 AND eventDate >= '2022-06-06'
  GROUP BY revenue_type
)

SELECT
  t.eventDate,
  t.user_id,
  t.revenue_type,
  t.transaction_value,
  s.avg_transaction,
  ROUND(t.transaction_value / s.avg_transaction, 1) AS times_avg
FROM `game-analytics.data_analyst_test_local.revenues` t
JOIN transaction_stats s ON t.revenue_type = s.revenue_type
WHERE
  (t.transaction_value > s.threshold_100x) AND eventDate >= '2022-06-06'
ORDER BY t.transaction_value DESC, t.eventDate
"""


REVENUE_BY_SOURCE_QUERY = """
-- US Official Launch data with clean anomaly filtering
WITH filtered_revenue AS (
  SELECT
    eventDate AS revenue_date,
    revenue_type,
    user_id,
    transaction_value
  FROM `game-analytics.data_analyst_test_local.revenues`
  WHERE
    eventDate >= '2022-06-06'
    AND eventDate IS NOT NULL
    AND transaction_value IS NOT NULL
    -- Exclude the specific anomaly transaction
    AND NOT (user_id = 21634 AND eventDate = '2022-06-24' AND transaction_value = 10000.0)
),

activity_data AS (
  SELECT
    date,
    COUNT(DISTINCT user_id) AS DAU
  FROM `game-analytics.data_analyst_test_local.activity`
  WHERE date >= '2022-06-06'
  GROUP BY date
),

overall_totals AS (
  SELECT
    COUNT(DISTINCT CASE WHEN a.date IS NOT NULL THEN a.user_id END) AS total_unique_active_users,
    COUNT(DISTINCT CASE WHEN r.revenue_type = 'iap' THEN r.user_id END) AS total_unique_paying_users_iap,
    COUNT(DISTINCT CASE WHEN r.user_id IS NOT NULL THEN r.user_id END) AS total_unique_paying_users_all
  FROM `game-analytics.data_analyst_test_local.activity` a
  FULL OUTER JOIN filtered_revenue r ON a.user_id = r.user_id
  WHERE (a.date >= '2022-06-06' OR a.date IS NULL)
),

daily_metrics AS (
  SELECT
    revenue_date,
    SUM(CASE WHEN revenue_type = 'iap' THEN transaction_value ELSE 0 END) AS iap_revenue,
    SUM(CASE WHEN revenue_type = 'ad' THEN transaction_value ELSE 0 END) AS ad_revenue,
    SUM(transaction_value) AS total_revenue,
    COUNT(DISTINCT CASE WHEN revenue_type = 'iap' THEN user_id END) AS total_spender,
    SAFE_DIVIDE(
      SUM(CASE WHEN revenue_type = 'iap' THEN transaction_value ELSE 0 END),
      COUNT(DISTINCT CASE WHEN revenue_type = 'iap' THEN user_id END)
    ) AS iap_per_spender,
    SAFE_DIVIDE(
      SUM(CASE WHEN revenue_type = 'ad' THEN transaction_value ELSE 0 END),
      COUNT(DISTINCT CASE WHEN revenue_type = 'iap' THEN user_id END)
    ) AS ad_per_spender,
    SAFE_DIVIDE(
      SUM(CASE WHEN revenue_type = 'iap' THEN transaction_value ELSE 0 END),
      COUNT(DISTINCT CASE WHEN revenue_type = 'iap' THEN user_id END)
    ) AS total_per_spender
  FROM filtered_revenue
  GROUP BY revenue_date
)

SELECT
  d.revenue_date,
  'US - Official Launch' AS launch_phase,
  d.iap_revenue,
  d.ad_revenue,
  d.total_revenue,
  d.total_spender,
  d.iap_per_spender,
  d.ad_per_spender,
  d.total_per_spender,
  a.DAU,
  SAFE_DIVIDE(d.iap_revenue, a.DAU) AS iap_arpdau,
  SAFE_DIVIDE(d.ad_revenue, a.DAU) AS ad_arpdau,
  SAFE_DIVIDE(d.total_revenue, a.DAU) AS total_arpdau,
  t.total_unique_active_users,
  t.total_unique_paying_users_iap,
  t.total_unique_paying_users_all
FROM daily_metrics d
LEFT JOIN activity_data a ON d.revenue_date = a.date
CROSS JOIN overall_totals t
ORDER BY d.revenue_date
"""
