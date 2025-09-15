-- Player Distribution Query
-- This query analyzes player acquisition data by install date, platform, country, channel type, and demographics
-- Used for: Player acquisition analytics dashboard - tracking user acquisition trends and distribution patterns

SELECT
  case when install_date is null then null ELSE DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', install_date)) end as install_date,
  CASE
    WHEN DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', install_date)) < '2022-04-01' THEN 'Soft Launch'
    WHEN DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', install_date)) >= '2022-06-01' THEN 'Official Launch'
    ELSE 'Unknown'
  END as launch_phase,
  case
    when lower(platform) = 'google_android' then 'android'
    when lower(platform) = 'apple_ios' then 'ios'
    else lower(platform)
  end as platform,
  LEFT(channel_country,2) AS country,
  SPLIT(channel_country, '-')[OFFSET(1)] AS channel_type,
  case when gender is null then "unknown" else gender end as gender,
  CASE
    WHEN age IS NULL OR age = '' OR age = 'unknown' THEN 'unknown'
    WHEN age = '60+' THEN '60+'
    WHEN SAFE_CAST(age AS INT64) IS NULL THEN 'unknown'
    WHEN SAFE_CAST(age AS INT64) <=30 THEN '<=30'
    WHEN SAFE_CAST(age AS INT64) BETWEEN 31 AND 40 THEN '31-40'
    WHEN SAFE_CAST(age AS INT64) BETWEEN 41 AND 50 THEN '41-50'
    WHEN SAFE_CAST(age AS INT64) BETWEEN 51 AND 60 THEN '51-60'
    ELSE 'unknown'
  END AS age_group,
  count(DISTINCT user_id) as num_player,
  count(*) as num_device
FROM `tactile-471816.data_analyst_test_local.users`
WHERE DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', install_date)) >= '2020-01-01'
  AND DATE(SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*SZ', install_date)) <= CURRENT_DATE()
GROUP BY 1, 2, 3, 4, 5, 6, 7
ORDER BY 1
