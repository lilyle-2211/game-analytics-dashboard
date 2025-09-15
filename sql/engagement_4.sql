-- Progression Milestone Query
-- This query tracks user progression through major level milestones (100, 200, 300, etc.)
-- Used for: Engagement analytics dashboard - analyzing player progression and milestone completion times

WITH user_level_progression AS (
  SELECT
    user_id,
    date,
    max_level_completed,
    ROW_NUMBER() OVER (PARTITION BY user_id, max_level_completed ORDER BY date) as rn
  FROM `tactile-471816.data_analyst_test_local.activity`
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
  FROM `tactile-471816.data_analyst_test_local.activity`
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
  FROM `tactile-471816.data_analyst_test_local.activity`
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
