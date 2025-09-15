-- Revenue by Source Query
-- This query analyzes daily revenue metrics by source (IAP vs Ad) with anomaly filtering
-- Used for: Monetization analytics dashboard - tracking revenue performance, ARPDAU, and user spending patterns

WITH filtered_revenue AS (
  SELECT
    eventDate AS revenue_date,
    revenue_type,
    user_id,
    transaction_value
  FROM `tactile-471816.data_analyst_test_local.revenues`
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
  FROM `tactile-471816.data_analyst_test_local.activity`
  WHERE date >= '2022-06-06'
  GROUP BY date
),

overall_totals AS (
  SELECT
    COUNT(DISTINCT CASE WHEN a.date IS NOT NULL THEN a.user_id END) AS total_unique_active_users,
    COUNT(DISTINCT CASE WHEN r.revenue_type = 'iap' THEN r.user_id END) AS total_unique_paying_users_iap,
    COUNT(DISTINCT CASE WHEN r.user_id IS NOT NULL THEN r.user_id END) AS total_unique_paying_users_all
  FROM `tactile-471816.data_analyst_test_local.activity` a
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
