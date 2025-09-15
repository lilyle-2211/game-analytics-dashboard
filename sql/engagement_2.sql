-- Daily Return Rate Query
-- This query calculates day-over-day user return rates
-- Used for: Engagement analytics dashboard - measuring short-term user retention

WITH all_users AS (
  SELECT
    COUNT(DISTINCT user_id) as unique_users_count
  FROM `tactile-471816.data_analyst_test_local.activity`
  WHERE date IS NOT NULL AND date >='2022-06-06' AND user_id IS NOT NULL
),
user_daily_activity AS (
  SELECT
    user_id,
    date,
    LAG(date) OVER (PARTITION BY user_id ORDER BY date) as prev_date,
  FROM `tactile-471816.data_analyst_test_local.activity`
  WHERE date IS NOT NULL AND date >='2022-06-06' AND user_id IS NOT NULL
),
daily_returns AS (
  SELECT
    date,
    COUNT(DISTINCT user_id) as total_active_users,
    COUNT(DISTINCT CASE WHEN DATE_DIFF(date, prev_date, DAY) = 1 THEN user_id END) as returned_next_day,
  FROM user_daily_activity
  GROUP BY date
),
return_rates AS (
  SELECT
    date,
    total_active_users,
    returned_next_day,
    ROUND(returned_next_day * 100.0 / NULLIF(total_active_users, 0), 2) as daily_return_rate_pct,
    (SELECT unique_users_count FROM all_users) as total_unique_users
  FROM daily_returns
)
SELECT * FROM return_rates
ORDER BY date
