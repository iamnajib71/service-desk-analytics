select * from {{ ref('fct_tickets') }}
where csat is not null and (csat not between 1 and 5 or resolved_at is null)
