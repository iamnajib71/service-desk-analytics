select * from {{ ref('stg_uci_tickets') }}
union all
select 'synthetic' as dataset, ticket_id, category, assignment_group,
    cast(priority as integer), channel,
    cast(opened_at as timestamp), try_cast(first_response_at as timestamp),
    try_cast(resolved_at as timestamp), cast(reopen_count as integer),
    try_cast(first_contact_resolution as boolean), try_cast(csat as integer),
    try_cast(source_sla_met as boolean), cast(sla_target_hours as integer),
    false as invalid_resolution, false as unparsed_resolution,
    timestamp '2025-01-01' as last_observed_at
from {{ source('raw', 'synthetic_tickets') }}
