select dataset, date_trunc('month', opened_at)::date as month, channel,
    hour(opened_at) as opened_hour, count(*) as ticket_volume
from {{ ref('fct_tickets') }} group by 1, 2, 3, 4
