-- Which teams own the oldest queue at the latest observed month end?
select g.assignment_group, sum(backlog_tickets) as backlog,
    sum(case when age_bucket = '31+ days' then backlog_tickets else 0 end) as aged_31_plus,
    round(max(oldest_days), 1) as oldest_days
from marts.kpi_backlog b join marts.dim_group g using(group_key)
where dataset = $dataset and month = (select max(month) from marts.kpi_backlog where dataset = $dataset)
group by 1 order by aged_31_plus desc, backlog desc, assignment_group limit 10
