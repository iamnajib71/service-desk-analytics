select dataset, date_trunc('month', opened_at)::date as month, category_key,
    count(*) as ticket_volume, count(sla_met) as eligible_tickets,
    count(*) filter (where sla_met = false) as breaches,
    100.0 * avg(sla_met::integer) as sla_pct,
    avg(resolution_hours) as mttr_hours, 100.0 * avg(reopened::integer) as reopen_pct
from {{ ref('fct_tickets') }} group by 1, 2, 3
