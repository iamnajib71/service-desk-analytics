select dataset, date_trunc('month', opened_at)::date as month,
    count(*) as opened_tickets, count(resolved_at) as resolved_tickets,
    count(sla_met) as sla_eligible, 100.0 * avg(sla_met::integer) as sla_pct,
    avg(resolution_hours) as mttr_hours, median(resolution_hours) as median_resolution_hours,
    quantile_cont(resolution_hours, 0.9) as p90_resolution_hours,
    count(first_contact_resolution) as fcr_eligible,
    100.0 * avg(first_contact_resolution::integer) as fcr_pct,
    100.0 * avg(reopened::integer) as reopen_pct,
    avg(csat) as csat_mean, count(csat) as csat_responses,
    100.0 * count(csat) / nullif(count(resolved_at), 0) as csat_response_pct,
    avg(response_minutes) as first_response_minutes
from {{ ref('fct_tickets') }} group by 1, 2
