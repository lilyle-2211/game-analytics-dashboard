-- Two Week Retention Query
-- This query calculates 2-week retention rates by launch phase
-- Used for: Engagement analytics dashboard - measuring medium-term user retention

WITH user_installs AS (
  SELECT
    u.user_id,
    REGEXP_EXTRACT(u.user_id, r'_(\d+)') as numeric_user_id,
    DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', u.install_date)) as install_date
  FROM `game-analytics.data_analyst_test_local.users` u
  WHERE u.install_date IS NOT NULL
    AND DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', u.install_date)) >= '2020-01-01'
    AND DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', u.install_date)) <= CURRENT_DATE()
),
user_activity AS (
  SELECT
    CAST(a.user_id AS STRING) as numeric_user_id,
    a.date as activity_date
  FROM `game-analytics.data_analyst_test_local.activity` a
  WHERE a.date IS NOT NULL AND a.user_id IS NOT NULL
),
two_week_retention AS (
  SELECT
    ui.user_id,
    ui.install_date,
    CASE
      WHEN ui.install_date < '2022-06-06' THEN 'Soft Launch'
      ELSE 'Official Launch'
    END as launch_phase,
    CASE
      WHEN MAX(CASE
        WHEN DATE_DIFF(ua.activity_date, ui.install_date, DAY) BETWEEN 14 AND 20
        THEN 1 ELSE 0
      END) = 1 THEN 1
      ELSE 0
    END as active_week_2
  FROM user_installs ui
  LEFT JOIN user_activity ua ON ui.numeric_user_id = ua.numeric_user_id
  WHERE ui.install_date <= DATE_SUB(CURRENT_DATE(), INTERVAL 21 DAY)
  GROUP BY ui.user_id, ui.install_date, launch_phase
)
SELECT
  launch_phase,
  COUNT(*) as total_installed_users,
  SUM(active_week_2) as users_active_week_2,
  ROUND(SUM(active_week_2) * 100.0 / COUNT(*), 2) as two_week_retention_pct
FROM two_week_retention
GROUP BY launch_phase
ORDER BY launch_phase
