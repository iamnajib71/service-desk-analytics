-- Snapshot is the exclusive start of the next month, capped at extraction.
with months as (
    select distinct dataset, date_trunc('month', opened_at)::date as month,
        least(date_trunc('month', opened_at) + interval 1 month, as_of) as snapshot_at
    from {{ ref('fct_tickets') }}
), backlog as (
    select m.dataset, m.month, m.snapshot_at, f.ticket_key, f.group_key,
        epoch(m.snapshot_at - f.opened_at) / 86400.0 as age_days
    from months m join {{ ref('fct_tickets') }} f
        on m.dataset = f.dataset and f.opened_at < m.snapshot_at
        and (f.resolved_at is null or f.resolved_at >= m.snapshot_at)
)
select dataset, month, snapshot_at, group_key,
    case when age_days < 2 then '0-1 days' when age_days < 8 then '2-7 days'
         when age_days < 31 then '8-30 days' else '31+ days' end as age_bucket,
    count(*) as backlog_tickets, max(age_days) as oldest_days
from backlog group by 1, 2, 3, 4, 5
