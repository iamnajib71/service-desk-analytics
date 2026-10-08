select * from {{ ref('fct_tickets') }} where resolved_at < opened_at
