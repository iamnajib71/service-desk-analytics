-- Is the average hiding a long resolution tail?
select c.category, count(resolution_hours) as resolved_tickets,
    round(avg(resolution_hours), 2) as mean_hours,
    round(median(resolution_hours), 2) as median_hours,
    round(quantile_cont(resolution_hours, 0.9), 2) as p90_hours
from marts.fct_tickets f join marts.dim_category c using(category_key)
where dataset = $dataset and resolution_hours is not null
group by 1 having count(*) >= 100 order by mean_hours desc, category limit 10
