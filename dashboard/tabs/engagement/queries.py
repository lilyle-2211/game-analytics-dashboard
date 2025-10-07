"""SQL queries for engagement analytics."""

DAILY_ENGAGEMENT_QUERY = """
SELECT
  date,
  COUNT(DISTINCT user_id) as daily_active_users,
  SUM(levels_played) as total_levels_played,
  SUM(levels_completed) as total_levels_completed
FROM `game-analytics.data.activity`
WHERE date IS NOT NULL and date >='2022-06-06'
GROUP BY date
ORDER BY date
"""

DAILY_RETURN_RATE_QUERY = """
WITH all_users AS (
  SELECT
    COUNT(DISTINCT user_id) as unique_users_count
  FROM `game-analytics.data.activity`
  WHERE date IS NOT NULL AND date >='2022-06-06' AND user_id IS NOT NULL
),
user_daily_activity AS (
  SELECT
    user_id,
    date,
    LAG(date) OVER (PARTITION BY user_id ORDER BY date) as prev_date,
  FROM `game-analytics.data.activity`
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
"""

TWO_WEEK_RETENTION_QUERY = """
WITH user_installs AS (
  SELECT
    u.user_id,
    REGEXP_EXTRACT(u.user_id, r'_(\d+)') as numeric_user_id,
    DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', u.install_date)) as install_date
  FROM `game-analytics.data.users` u
  WHERE u.install_date IS NOT NULL
    AND DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', u.install_date)) >= '2020-01-01'
    AND DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', u.install_date)) <= CURRENT_DATE()
),
user_activity AS (
  SELECT
    CAST(a.user_id AS STRING) as numeric_user_id,
    a.date as activity_date
  FROM `game-analytics.data.activity` a
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
"""

PROGRESSION_MILESTONE_QUERY = """
WITH user_level_progression AS (
  SELECT
    user_id,
    date,
    max_level_completed,
    ROW_NUMBER() OVER (PARTITION BY user_id, max_level_completed ORDER BY date) as rn
  FROM `game-analytics.data.activity`
  WHERE date IS NOT NULL
    AND date >= '2022-06-06'
    AND user_id IS NOT NULL
    AND max_level_completed IS NOT NULL
),
user_first_level_completion AS (
  SELECT
    user_id,
    max_level_completed,
    date as completion_date
  FROM user_level_progression
  WHERE rn = 1
),
user_first_activity AS (
  SELECT
    user_id,
    MIN(date) as first_active_date
  FROM `game-analytics.data.activity`
  WHERE date IS NOT NULL
    AND date >= '2022-06-06'
    AND user_id IS NOT NULL
  GROUP BY user_id
),
user_max_levels AS (
  SELECT
    user_id,
    MIN(date) as first_active_date,
    MAX(max_level_completed) as highest_level_reached
  FROM `game-analytics.data.activity`
  WHERE date IS NOT NULL
    AND date >= '2022-06-06'
    AND user_id IS NOT NULL
    AND max_level_completed IS NOT NULL
  GROUP BY user_id
),
milestone_levels AS (
  -- Generate milestone levels from 100 to 5000 in increments of 100
  SELECT level
  FROM UNNEST(GENERATE_ARRAY(100, 5000, 100)) as level
),
user_milestone_achievements AS (
  SELECT
    uml.user_id,
    uml.first_active_date,
    uml.highest_level_reached,
    ml.level as milestone_level,
    CASE WHEN uml.highest_level_reached >= ml.level THEN TRUE ELSE FALSE END as milestone_achieved
  FROM user_max_levels uml
  CROSS JOIN milestone_levels ml
),
milestone_completion_times AS (
  SELECT
    uma.user_id,
    uma.milestone_level,
    uma.milestone_achieved,
    ufa.first_active_date,
    MIN(uflc.completion_date) as milestone_completion_date
  FROM user_milestone_achievements uma
  JOIN user_first_activity ufa ON uma.user_id = ufa.user_id
  LEFT JOIN user_first_level_completion uflc
    ON uma.user_id = uflc.user_id
    AND uflc.max_level_completed >= uma.milestone_level
  WHERE uma.milestone_achieved = TRUE
  GROUP BY uma.user_id, uma.milestone_level, uma.milestone_achieved, ufa.first_active_date
)
SELECT
  CONCAT(milestone_level, 'th') as milestone,
  COUNT(DISTINCT user_id) as num_users_who_played,
  ROUND(AVG(CASE WHEN milestone_achieved THEN DATE_DIFF(milestone_completion_date, first_active_date, DAY) END), 0) as cumulative_avg_days_to_complete
FROM milestone_completion_times
GROUP BY milestone_level
HAVING COUNT(DISTINCT CASE WHEN milestone_achieved THEN user_id END) > 1  -- Filter out milestones with only 1 user
ORDER BY milestone_level
"""
