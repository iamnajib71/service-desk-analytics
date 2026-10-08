select * from {{ ref('fct_tickets') }}
where first_response_at < opened_at or first_response_at > resolved_at
