-- Which contact channel and hours contribute the most demand?
select channel, opened_hour, sum(ticket_volume) as tickets,
    round(100.0 * sum(ticket_volume) / (select sum(ticket_volume) from marts.kpi_demand where dataset = $dataset), 2) as share_pct
from marts.kpi_demand where dataset = $dataset
group by 1, 2 order by tickets desc, channel, opened_hour limit 10
