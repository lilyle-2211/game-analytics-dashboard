-- Anomaly Transactions Query
-- This query identifies statistical outliers in transaction data (transactions >100x average)
-- Used for: Monetization analytics dashboard - detecting unusual transaction patterns and potential data issues

WITH transaction_stats AS (
  SELECT
    revenue_type,
    AVG(transaction_value) AS avg_transaction,
    AVG(transaction_value) * 100 AS threshold_100x -- 100x average threshold
  FROM `tactile-471816.data_analyst_test_local.revenues`
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
FROM `tactile-471816.data_analyst_test_local.revenues` t
JOIN transaction_stats s ON t.revenue_type = s.revenue_type
WHERE
  (t.transaction_value > s.threshold_100x) AND eventDate >= '2022-06-06'
ORDER BY t.transaction_value DESC, t.eventDate
