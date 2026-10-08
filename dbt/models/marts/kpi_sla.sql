select dataset, date_trunc('month', opened_at)::date as month, priority,
    count(*) as opened_tickets, count(sla_met) as eligible_tickets,
    count(*) filter (where sla_met) as compliant_tickets,
    100.0 * count(*) filter (where sla_met) / nullif(count(sla_met), 0) as sla_pct
from {{ ref('fct_tickets') }} group by 1, 2, 3
