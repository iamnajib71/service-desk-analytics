-- Latest audit row is deterministic even when update timestamps tie.
with typed as (
    select *,
        try_strptime(opened_at, '%d/%m/%Y %H:%M') as opened_ts,
        try_strptime(resolved_at, '%d/%m/%Y %H:%M') as resolved_ts,
        try_strptime(sys_updated_at, '%d/%m/%Y %H:%M') as updated_ts
    from {{ source('raw', 'uci_events') }}
), latest as (
    select * from typed
    qualify row_number() over (partition by number order by updated_ts desc nulls last, try_cast(sys_mod_count as integer) desc nulls last, source_row desc) = 1
)
select 'public' as dataset, number as ticket_id,
    coalesce(nullif(category, '?'), 'Unknown') as category,
    coalesce(nullif(assignment_group, '?'), 'Unknown') as assignment_group,
    try_cast(left(priority, 1) as integer) as priority,
    coalesce(nullif(contact_type, '?'), 'Unknown') as channel,
    opened_ts as opened_at, null::timestamp as first_response_at,
    case when resolved_ts >= opened_ts then resolved_ts end as resolved_at,
    coalesce(try_cast(reopen_count as integer), 0) as reopen_count,
    null::boolean as first_contact_resolution, null::integer as csat,
    try_cast(made_sla as boolean) as source_sla_met,
    null::integer as sla_target_hours,
    resolved_ts < opened_ts as invalid_resolution,
    resolved_at <> '?' and resolved_ts is null as unparsed_resolution,
    greatest(opened_ts, updated_ts, resolved_ts) as last_observed_at
from latest
