-- Daily Engagement Query
-- This query calculates daily active users and their level activity
-- Used for: Engagement analytics dashboard - tracking daily user engagement metrics

SELECT
  date,
  COUNT(DISTINCT user_id) as daily_active_users,
  SUM(levels_played) as total_levels_played,
  SUM(levels_completed) as total_levels_completed
FROM `game-analytics.data_analyst_test_local.activity`
WHERE date IS NOT NULL and date >='2022-06-06'
GROUP BY date
ORDER BY date
