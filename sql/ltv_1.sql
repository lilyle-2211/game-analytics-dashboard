-- Revenue Segmentation Query
-- This query retrieves day 1-20 revenue segmentation data
-- Used for: LTV analytics dashboard - analyzing user revenue segments and spending patterns over 20-day window

WITH user_installs AS (
  SELECT
    user_id,
    DATE(install_date) AS install_date
  FROM `tactile-471816.data_analyst_test_local.users_view`
  WHERE DATE(install_date) >= '2022-06-06'
    AND install_date IS NOT NULL
),

revenue_20 AS (
  SELECT
    ui.user_id,
    r.transaction_value,
    DATE_DIFF(DATE(r.date), ui.install_date, DAY) AS day_offset
  FROM user_installs ui
  LEFT JOIN `tactile-471816.data_analyst_test_local.revenue_view` r
    ON ui.user_id = r.user_id
   AND DATE_DIFF(DATE(r.date), ui.install_date, DAY) BETWEEN 0 AND 19
)

SELECT
  user_id,
  -- Cumulative revenue from day 1 through each day
  SUM(IF(day_offset = 0, transaction_value, 0)) AS revenue_day_1,
  SUM(IF(day_offset <= 1, transaction_value, 0)) AS revenue_day_2,
  SUM(IF(day_offset <= 2, transaction_value, 0)) AS revenue_day_3,
  SUM(IF(day_offset <= 3, transaction_value, 0)) AS revenue_day_4,
  SUM(IF(day_offset <= 4, transaction_value, 0)) AS revenue_day_5,
  SUM(IF(day_offset <= 5, transaction_value, 0)) AS revenue_day_6,
  SUM(IF(day_offset <= 6, transaction_value, 0)) AS revenue_day_7,
  SUM(IF(day_offset <= 7, transaction_value, 0)) AS revenue_day_8,
  SUM(IF(day_offset <= 8, transaction_value, 0)) AS revenue_day_9,
  SUM(IF(day_offset <= 9, transaction_value, 0)) AS revenue_day_10,
  SUM(IF(day_offset <= 10, transaction_value, 0)) AS revenue_day_11,
  SUM(IF(day_offset <= 11, transaction_value, 0)) AS revenue_day_12,
  SUM(IF(day_offset <= 12, transaction_value, 0)) AS revenue_day_13,
  SUM(IF(day_offset <= 13, transaction_value, 0)) AS revenue_day_14,
  SUM(IF(day_offset <= 14, transaction_value, 0)) AS revenue_day_15,
  SUM(IF(day_offset <= 15, transaction_value, 0)) AS revenue_day_16,
  SUM(IF(day_offset <= 16, transaction_value, 0)) AS revenue_day_17,
  SUM(IF(day_offset <= 17, transaction_value, 0)) AS revenue_day_18,
  SUM(IF(day_offset <= 18, transaction_value, 0)) AS revenue_day_19,
  SUM(IF(day_offset <= 19, transaction_value, 0)) AS revenue_day_20
FROM revenue_20
GROUP BY user_id
ORDER BY user_id;
