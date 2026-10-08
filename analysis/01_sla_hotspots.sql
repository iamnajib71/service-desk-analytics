-- Which high-volume categories have the greatest breach rate, and in which month?
select c.category, k.month, k.eligible_tickets, k.breaches,
    round(100.0 * k.breaches / k.eligible_tickets, 2) as breach_pct
from marts.kpi_category k join marts.dim_category c using(category_key)
where k.dataset = $dataset and k.eligible_tickets >= 100
order by breach_pct desc, breaches desc, category, month limit 10
