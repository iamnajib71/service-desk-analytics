from pathlib import Path
import json
import sys
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dashboard.charts import figures, metrics

st.set_page_config(page_title='Service Operations | Nazmul Hassan', page_icon='◉', layout='wide')
st.markdown('''<style>
.stApp { background:#0a131b; } .block-container { padding-top:4rem; max-width:1450px; }
h1 { letter-spacing:-1.5px; } [data-testid="stMetric"] { background:#111c24; border:1px solid #25343c; padding:18px; border-radius:10px; }
[data-testid="stMetricValue"] {color:#73e2ae;} .stPlotlyChart {border:1px solid #25343c;border-radius:10px;}
</style>''', unsafe_allow_html=True)
st.caption('NAZMUL HASSAN  /  ANALYTICS PORTFOLIO')
st.title('Service operations')
st.markdown('Turn ticket activity into decisions about service quality, queue health and support capacity.')
with st.sidebar:
    st.header('Explore the evidence')
    source = st.selectbox('Dataset', ['Synthetic demo', 'Public UCI research data'])
    dataset = 'synthetic' if source == 'Synthetic demo' else 'public'
    path = ROOT / f'dashboard/data/{dataset}.json'
    if not path.exists():
        st.error('Run the rebuild command first.'); st.stop()
    data = json.loads(path.read_text())
    month = st.selectbox('Opening cohort', ['All months']+[row['month'] for row in data['kpi_monthly']])
    st.markdown('**Definitions**')
    st.caption('Trend charts retain full history; the dotted line marks the selected cohort. Queue age is a point-in-time snapshot. SLA, duration and CSAT use eligible resolved tickets from the opening cohort.')
    st.caption('Public: source SLA flag; FCR, first response and CSAT unavailable. Synthetic: fictional calendar-hour targets, no real users.')
    st.link_button('SQL and evidence on GitHub', 'https://github.com/iamnajib71/service-desk-analytics')
st.info('SYNTHETIC DATA · fictional tickets for demonstration · seed 71' if dataset == 'synthetic' else 'PUBLIC RESEARCH DATA · UCI / CC BY 4.0 · anonymised category labels · historical snapshot')
row = metrics(data, month)
cols = st.columns(4)
cols[0].metric('Tickets opened', f"{row['opened_tickets']:,}")
cols[1].metric('SLA compliance', 'Unavailable' if row['sla_pct'] is None else f"{row['sla_pct']:.1f}%")
cols[2].metric('Mean time to resolve', f"{row['mttr_hours']:.1f} h")
cols[3].metric('Reopen rate', f"{row['reopen_pct']:.1f}%")
st.caption(f"SLA denominator: {row['sla_eligible']:,} · FCR: " + ('unavailable' if row['fcr_pct'] is None else f"{row['fcr_pct']:.1f}%") + f" · CSAT respondents: {row['csat_responses']:,} · report basis: opening cohort / calendar elapsed time")
charts = figures(data, month)
for start in range(0, len(charts), 2):
    columns = st.columns(2)
    for col, (title, subtitle, fig) in zip(columns, charts[start:start+2]):
        with col:
            st.subheader(title); st.caption(subtitle)
            st.plotly_chart(fig, width='stretch', config={'displayModeBar':False})
with st.expander('Monthly KPI table and export'):
    st.dataframe(data['kpi_monthly'], width='stretch')
    st.download_button('Download monthly evidence JSON', json.dumps(data['kpi_monthly'], indent=2), f'{dataset}_monthly.json')
st.caption('Built by Nazmul Hassan · source details and measurement limits in data/SOURCE.md and docs/kpi-definitions.md')
