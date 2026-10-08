-- Which categories have the highest reopen rate with a meaningful sample?
select c.category, count(*) as tickets, sum(reopened::integer) as reopened_tickets,
    round(100.0 * avg(reopened::integer), 2) as reopen_pct,
    round(avg(csat), 2) as csat_mean, count(csat) as csat_responses
from marts.fct_tickets f join marts.dim_category c using(category_key)
where dataset = $dataset group by 1 having count(*) >= 100
order by reopen_pct desc, tickets desc, category limit 10
