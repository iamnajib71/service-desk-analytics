"""Shared Plotly charts for Streamlit and the synthetic Pages demo."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

GREEN = '#73e2ae'
PALETTE = [GREEN, '#8cb8ff', '#ffc876', '#dd9ce9']


def figures(data, month='All months'):
    def frame(name):
        df = pd.DataFrame(data[name])
        return df if month == 'All months' or 'month' not in df else df[df.month == month]
    monthly = pd.DataFrame(data['kpi_monthly'])
    sla = frame('kpi_sla').groupby('priority', as_index=False)[['eligible_tickets', 'compliant_tickets']].sum()
    sla['sla_pct'] = 100 * sla.compliant_tickets / sla.eligible_tickets
    cat = frame('kpi_category').groupby('category', as_index=False).agg(ticket_volume=('ticket_volume', 'sum'), breaches=('breaches', 'sum'), eligible_tickets=('eligible_tickets', 'sum'))
    cat['breach_pct'] = 100 * cat.breaches / cat.eligible_tickets.replace(0, float('nan'))
    cat = cat.sort_values('breaches', ascending=False).head(8).sort_values('breaches')
    backlog = frame('kpi_backlog')
    if month == 'All months':
        backlog = backlog[backlog.month == backlog.month.max()]
    backlog = backlog.groupby('age_bucket', as_index=False).backlog_tickets.sum()
    demand = frame('kpi_demand')
    channel = demand.groupby('channel', as_index=False).ticket_volume.sum()
    heat = demand.pivot_table(index='channel', columns='opened_hour', values='ticket_volume', aggfunc='sum', fill_value=0)
    selected_monthly = monthly if month == 'All months' else monthly[monthly.month == month]
    figs = [
        ('Ticket intake', 'Opening cohort · monthly volume', px.area(monthly, x='month', y='opened_tickets')),
        ('SLA by priority', 'Eligible resolved tickets · percentage', px.bar(sla, x='priority', y='sla_pct', text_auto='.1f')),
        ('Where breaches concentrate', 'Top categories · breach count', px.bar(cat, x='breaches', y='category', orientation='h', hover_data=['breach_pct', 'eligible_tickets'])),
        ('Queue age at month end', 'Unresolved at snapshot · calendar days', px.bar(backlog, x='age_bucket', y='backlog_tickets', category_orders={'age_bucket':['0-1 days','2-7 days','8-30 days','31+ days']})),
        ('How users contact IT', 'Opening cohort · channel share', px.pie(channel, names='channel', values='ticket_volume', hole=0.68)),
        ('When demand arrives', 'Source local clock · channel / hour', px.imshow(heat, aspect='auto', color_continuous_scale=['#172923', GREEN])),
        ('Repeat work', 'Opening cohort · reopened percentage', px.line(monthly, x='month', y='reopen_pct', markers=True)),
        ('Voice of the user', 'Opening cohort · mean CSAT among respondents', px.line(monthly, x='month', y='csat_mean', markers=True)),
    ]
    for i, (title, subtitle, fig) in enumerate(figs):
        fig.update_layout(template='plotly_dark', paper_bgcolor='#111c24', plot_bgcolor='#111c24',
            font={'family':'Arial', 'color':'#bacbd4', 'size':12}, colorway=PALETTE,
            margin={'l':45,'r':20,'t':20,'b':40}, height=285, showlegend=i == 4)
        if i in [0, 6, 7]:
            fig.update_traces(line_color=GREEN)
        if i in [1, 2, 3]:
            fig.update_traces(marker_color=GREEN)
        fig.update_xaxes(showgrid=False, title=None)
        fig.update_yaxes(gridcolor='#25343c', title=None)
        if i == 1:
            fig.update_yaxes(range=[0,100])
            fig.update_xaxes(tickmode='array', tickvals=[1,2,3,4], ticktext=['P1','P2','P3','P4'])
        if i == 7:
            fig.update_yaxes(range=[1,5])
            if all(row['csat_mean'] is None for row in data['kpi_monthly']):
                fig.add_annotation(text='CSAT unavailable in public source', x=0.5, y=0.5, xref='paper', yref='paper', showarrow=False)
        if month != 'All months' and i in [0,6,7]:
            fig.add_vline(x=month, line_dash='dot', line_color='#ffc876')
    return figs


def metrics(data, month):
    if month == 'All months':
        return data['summary']
    return next(row for row in data['kpi_monthly'] if row['month'] == month)
