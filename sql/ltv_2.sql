-- Retention Rate Query
-- This query retrieves day 1-20 retention rate data
-- Used for: LTV analytics dashboard - analyzing user retention patterns over 20-day window

WITH user_installs AS (
  SELECT

    u.user_id,
    DATE(u.install_date) as install_date,
  FROM `game-analytics.data_analyst_test_local.users_view` u
  WHERE u.install_date IS NOT NULL
    AND DATE(u.install_date) >= '2022-06-06'
    AND DATE(u.install_date) <= DATE_SUB(CURRENT_DATE(), INTERVAL 21 DAY)  -- Ensure 20+ days of data
),

user_activity AS (
  SELECT
    user_id,
    a.date as activity_date
  FROM `game-analytics.data_analyst_test_local.activity_view` a
  WHERE a.date IS NOT NULL
    AND a.user_id IS NOT NULL
),

daily_retention_calculation AS (
  SELECT
    ui.user_id,
    ui.install_date,
    -- Check activity for each day (1-20) since install
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 1 THEN 1 ELSE 0 END) as active_day_1,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 2 THEN 1 ELSE 0 END) as active_day_2,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 3 THEN 1 ELSE 0 END) as active_day_3,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 4 THEN 1 ELSE 0 END) as active_day_4,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 5 THEN 1 ELSE 0 END) as active_day_5,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 6 THEN 1 ELSE 0 END) as active_day_6,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 7 THEN 1 ELSE 0 END) as active_day_7,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 8 THEN 1 ELSE 0 END) as active_day_8,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 9 THEN 1 ELSE 0 END) as active_day_9,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 10 THEN 1 ELSE 0 END) as active_day_10,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 11 THEN 1 ELSE 0 END) as active_day_11,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 12 THEN 1 ELSE 0 END) as active_day_12,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 13 THEN 1 ELSE 0 END) as active_day_13,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 14 THEN 1 ELSE 0 END) as active_day_14,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 15 THEN 1 ELSE 0 END) as active_day_15,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 16 THEN 1 ELSE 0 END) as active_day_16,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 17 THEN 1 ELSE 0 END) as active_day_17,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 18 THEN 1 ELSE 0 END) as active_day_18,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 19 THEN 1 ELSE 0 END) as active_day_19,
    MAX(CASE WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) = 20 THEN 1 ELSE 0 END) as active_day_20
  FROM user_installs ui
  LEFT JOIN user_activity ua ON ui.user_id = ua.user_id
  GROUP BY ui.user_id, ui.install_date
)

-- Calculate retention rates for each day
SELECT
  COUNT(*) as total_installed_users,

  -- Day 1-20 retention rates
  ROUND(SUM(active_day_1) * 100.0 / COUNT(*), 2) as day_1_retention_pct,
  ROUND(SUM(active_day_2) * 100.0 / COUNT(*), 2) as day_2_retention_pct,
  ROUND(SUM(active_day_3) * 100.0 / COUNT(*), 2) as day_3_retention_pct,
  ROUND(SUM(active_day_4) * 100.0 / COUNT(*), 2) as day_4_retention_pct,
  ROUND(SUM(active_day_5) * 100.0 / COUNT(*), 2) as day_5_retention_pct,
  ROUND(SUM(active_day_6) * 100.0 / COUNT(*), 2) as day_6_retention_pct,
  ROUND(SUM(active_day_7) * 100.0 / COUNT(*), 2) as day_7_retention_pct,
  ROUND(SUM(active_day_8) * 100.0 / COUNT(*), 2) as day_8_retention_pct,
  ROUND(SUM(active_day_9) * 100.0 / COUNT(*), 2) as day_9_retention_pct,
  ROUND(SUM(active_day_10) * 100.0 / COUNT(*), 2) as day_10_retention_pct,
  ROUND(SUM(active_day_11) * 100.0 / COUNT(*), 2) as day_11_retention_pct,
  ROUND(SUM(active_day_12) * 100.0 / COUNT(*), 2) as day_12_retention_pct,
  ROUND(SUM(active_day_13) * 100.0 / COUNT(*), 2) as day_13_retention_pct,
  ROUND(SUM(active_day_14) * 100.0 / COUNT(*), 2) as day_14_retention_pct,
  ROUND(SUM(active_day_15) * 100.0 / COUNT(*), 2) as day_15_retention_pct,
  ROUND(SUM(active_day_16) * 100.0 / COUNT(*), 2) as day_16_retention_pct,
  ROUND(SUM(active_day_17) * 100.0 / COUNT(*), 2) as day_17_retention_pct,
  ROUND(SUM(active_day_18) * 100.0 / COUNT(*), 2) as day_18_retention_pct,
  ROUND(SUM(active_day_19) * 100.0 / COUNT(*), 2) as day_19_retention_pct,
  ROUND(SUM(active_day_20) * 100.0 / COUNT(*), 2) as day_20_retention_pct,

  -- Raw counts for reference
  SUM(active_day_1) as day_1_active_users,
  SUM(active_day_7) as day_7_active_users,
  SUM(active_day_14) as day_14_active_users,
  SUM(active_day_20) as day_20_active_users

FROM daily_retention_calculation;
