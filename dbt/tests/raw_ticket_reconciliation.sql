with expected as (
select 'public' as dataset, count(distinct number) as n from {{ source('raw', 'uci_events') }}
union all select 'synthetic', count(*) from {{ source('raw', 'synthetic_tickets') }}
), actual as (select dataset, count(*) as n from {{ ref('fct_tickets') }} group by 1)
select * from expected e full join actual a using(dataset) where e.n is distinct from a.n
