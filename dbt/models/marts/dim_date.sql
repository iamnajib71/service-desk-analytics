with bounds as (
select date_trunc('month', min(opened_at)) as start_date,
    max(last_observed_at)::date as end_date from {{ ref('stg_tickets') }}
)
select d::date as date_key, year(d) as year, month(d) as month,
    date_trunc('month', d)::date as month_start, dayofweek(d) as day_of_week,
    dayofweek(d) in (0, 6) as is_weekend
from bounds, generate_series(start_date, end_date, interval 1 day) as dates(d)
