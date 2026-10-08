"""Semantic checks with independent fixtures plus end-to-end dashboard smoke tests."""
import json
from pathlib import Path
import sys
import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.generate_tickets import generate


def sql(name, table):
    return (ROOT / f'dbt/models/marts/{name}.sql').read_text().replace("{{ ref('fct_tickets') }}", table)


def test_generator_is_reproducible(tmp_path):
    first, second, changed = [tmp_path / x for x in ['first.csv', 'second.csv', 'changed.csv']]
    generate(first, count=200); generate(second, count=200); generate(changed, count=200, seed=72)
    assert first.read_bytes() == second.read_bytes()
    assert first.read_bytes() != changed.read_bytes()


def test_month_end_boundaries_and_ageing():
    con = duckdb.connect()
    con.execute('''create table fixture(dataset varchar, opened_at timestamp, resolved_at timestamp,
    as_of timestamp, ticket_key varchar, group_key varchar)''')
    con.execute('''insert into fixture values
    ('x','2024-12-01','2025-01-01','2025-01-01','a','g'),
    ('x','2024-12-31 23:59',null,'2025-01-01','b','g'),
    ('x','2024-12-15','2024-12-31 23:59','2025-01-01','c','g'),
    ('x','2025-01-01',null,'2025-01-01','d','g')''')
    result = con.execute(sql('kpi_backlog','fixture')).df()
    december = result[result.month.astype(str) == '2024-12-01']
    assert december.backlog_tickets.sum() == 2
    assert dict(zip(december.age_bucket,december.backlog_tickets)) == {'31+ days':1, '0-1 days':1}


def test_sla_unknown_outcomes_are_not_failures():
    con = duckdb.connect()
    con.execute('''create table fixture(dataset varchar, opened_at timestamp, priority integer, sla_met boolean)''')
    con.execute("insert into fixture values ('x','2024-12-01',1,true),('x','2024-12-01',1,false),('x','2024-12-01',1,null)")
    row = con.execute(sql('kpi_sla','fixture')).df().iloc[0]
    assert row.opened_tickets == 3 and row.eligible_tickets == 2 and row.sla_pct == 50


def test_uci_reduction_tie_and_invalid_interval():
    con = duckdb.connect()
    con.execute('''create table fixture(number varchar, opened_at varchar, resolved_at varchar, sys_updated_at varchar,
    sys_mod_count varchar, source_row integer, category varchar, assignment_group varchar, priority varchar,
    contact_type varchar, reopen_count varchar, made_sla varchar)''')
    con.execute("""insert into fixture values
    ('A','1/1/2016 09:00','1/1/2016 08:00','2/1/2016 10:00','2',1,'Old','G','3 - Moderate','Phone','0','true'),
    ('A','1/1/2016 09:00','1/1/2016 08:00','2/1/2016 10:00','2',2,'?','?','3 - Moderate','Phone','1','false')""")
    query = (ROOT / 'dbt/models/staging/stg_uci_tickets.sql').read_text().replace("{{ source('raw', 'uci_events') }}",'fixture')
    row = con.execute(query).df().iloc[0]
    assert row.category == 'Unknown' and row.assignment_group == 'Unknown'
    assert row.invalid_resolution and str(row.resolved_at) == 'NaT'
    assert row.reopen_count == 1 and not row.source_sla_met


def test_exported_evidence_matches_warehouse():
    with duckdb.connect(str(ROOT / 'artifacts/service_desk.duckdb'), read_only=True) as con:
        for dataset in ['public','synthetic']:
            data = json.loads((ROOT / f'dashboard/data/{dataset}.json').read_text())
            assert data['summary']['opened_tickets'] == con.execute('select count(*) from marts.fct_tickets where dataset=?',[dataset]).fetchone()[0]
            assert sum(r['ticket_volume'] for r in data['kpi_demand']) == data['summary']['opened_tickets']
            assert sum(r['opened_tickets'] for r in data['kpi_monthly']) == data['summary']['opened_tickets']


def test_public_missing_metrics_and_synthetic_site():
    public = json.loads((ROOT / 'dashboard/data/public.json').read_text())
    assert public['summary']['csat_mean'] is None and public['summary']['fcr_pct'] is None
    site = json.loads((ROOT / 'site/charts.json').read_text())
    assert len(site) == 13 and len(site['All months']['charts']) == 8
    assert site['All months']['metrics']['opened_tickets'] == 20_000
    assert all('Category ' not in json.dumps(bundle) for bundle in site.values())


@pytest.mark.parametrize('source', ['Synthetic demo','Public UCI research data'])
def test_streamlit_source_and_cohort(source):
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(ROOT / 'dashboard/app.py'), default_timeout=30).run()
    app.selectbox[0].select(source).run()
    assert not app.exception
    app.selectbox[1].select(app.selectbox[1].options[-1]).run()
    assert not app.exception
    assert len(app.metric) == 4
