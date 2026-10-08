select dataset from {{ ref('fct_tickets') }} group by dataset
having count(*) <> (select sum(ticket_volume) from {{ ref('kpi_demand') }} d where d.dataset = fct_tickets.dataset)
