with snapshots as (
select dataset, max(last_observed_at) as as_of from {{ ref('stg_tickets') }} group by dataset
)
select md5(t.dataset || ':' || ticket_id) as ticket_key, t.dataset, ticket_id,
    md5(category) as category_key, md5(assignment_group) as group_key,
    opened_at::date as opened_date_key, priority, channel, opened_at,
    first_response_at, resolved_at, reopen_count > 0 as reopened,
    first_contact_resolution, csat, sla_target_hours,
    case when resolved_at is not null then
        case when t.dataset = 'public' then source_sla_met
        else epoch(resolved_at - opened_at) / 3600.0 <= sla_target_hours end
    end as sla_met,
    case when resolved_at is not null then epoch(resolved_at - opened_at) / 3600.0 end as resolution_hours,
    epoch(first_response_at - opened_at) / 60.0 as response_minutes,
    coalesce(invalid_resolution, false) as invalid_resolution,
    coalesce(unparsed_resolution, false) as unparsed_resolution,
    s.as_of
from {{ ref('stg_tickets') }} t join snapshots s using (dataset)
