select * from {{ ref('fct_tickets') }} where dataset = 'public'
and (csat is not null or first_contact_resolution is not null or first_response_at is not null or sla_target_hours is not null)
