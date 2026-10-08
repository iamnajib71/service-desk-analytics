"""Generate every quoted figure and the recruiter-facing evidence from the warehouse."""
import json
from pathlib import Path
import duckdb
import pandas as pd

SUMMARY_SQL = '''select count(*) as opened_tickets, count(resolved_at) as resolved_tickets,
count(sla_met) as sla_eligible, 100.0 * avg(sla_met::integer) as sla_pct,
avg(resolution_hours) as mttr_hours, median(resolution_hours) as median_resolution_hours,
quantile_cont(resolution_hours, 0.9) as p90_resolution_hours,
count(first_contact_resolution) as fcr_eligible, 100.0 * avg(first_contact_resolution::integer) as fcr_pct,
100.0 * avg(reopened::integer) as reopen_pct, avg(csat) as csat_mean,
count(csat) as csat_responses, sum(invalid_resolution::integer) as invalid_resolutions,
sum(unparsed_resolution::integer) as unparsed_resolutions,
min(opened_at) as first_opened, max(opened_at) as last_opened, max(as_of) as as_of
from marts.fct_tickets where dataset = ?'''


def records(frame):
    return json.loads(frame.to_json(orient='records', date_format='iso'))


def table(frame):
    def display(value):
        if pd.isna(value): return 'Unavailable'
        if isinstance(value, float): return f'{value:,.2f}'
        return str(value).split(' 00:00:00')[0]
    lines = ['| '+' | '.join(frame.columns)+' |', '| '+' | '.join(['---']*len(frame.columns))+' |']
    lines += ['| '+' | '.join(display(v) for v in row)+' |' for row in frame.itertuples(index=False, name=None)]
    return '\n'.join(lines)


def export_evidence(root: Path, database: Path):
    output = root / 'dashboard/data'; output.mkdir(parents=True, exist_ok=True)
    summaries = {}
    with duckdb.connect(str(database), read_only=True) as con:
        for dataset in ['public', 'synthetic']:
            data = {'dataset':dataset}
            for name in ['kpi_monthly', 'kpi_sla', 'kpi_backlog', 'kpi_demand', 'kpi_category']:
                query = f'select k.* from marts.{name} k where dataset = ? order by month'
                if name == 'kpi_category':
                    query = 'select k.*, c.category from marts.kpi_category k join marts.dim_category c using(category_key) where dataset = ? order by month, category'
                if name == 'kpi_backlog':
                    query = 'select k.*, g.assignment_group from marts.kpi_backlog k join marts.dim_group g using(group_key) where dataset = ? order by month, assignment_group, age_bucket'
                frame = con.execute(query, [dataset]).df()
                frame['month'] = frame.month.dt.strftime('%Y-%m-%d')
                data[name] = sorted(records(frame), key=lambda row: (row['month'], tuple(str(row[k]) for k in sorted(row))))
            data['summary'] = records(con.execute(SUMMARY_SQL, [dataset]).df())[0]
            summaries[dataset] = data['summary']
            (output / f'{dataset}.json').write_text(json.dumps(data, indent=2, allow_nan=False)+'\n', encoding='utf-8')
            for query_path in sorted((root / 'analysis').glob('*.sql')):
                frame = con.execute(query_path.read_text(), {'dataset':dataset}).df()
                frame.to_csv(root / 'analysis/results' / f'{query_path.stem}_{dataset}.csv', index=False, lineterminator='\n')
                row = frame.iloc[0]
                if query_path.stem.startswith('01'):
                    finding = f"{row.category} in {str(row.month)[:7]} leads the eligible high-volume category-months with a {row.breach_pct:.2f}% breach rate ({row.breaches:,.0f} breaches / {row.eligible_tickets:,.0f} eligible).\nPrioritise a case review of this cohort; volume thresholds reduce the risk of reacting to very small samples."
                elif query_path.stem.startswith('02'):
                    finding = f"{row.category} has the longest mean resolution time among qualifying categories: {row.mean_hours:.2f} hours, versus a {row.median_hours:.2f}-hour median and {row.p90_hours:.2f}-hour 90th percentile.\nUse the median and tail alongside the mean; this descriptive result does not identify a root cause."
                elif query_path.stem.startswith('03'):
                    finding = f"{row.assignment_group} owns {row.backlog:,.0f} tickets at the latest snapshot, including {row.aged_31_plus:,.0f} aged at least 31 days.\nValidate queue ownership before arranging an ageing review; the public snapshot is reconstructed from final outcomes, not an audit of historic queue moves."
                elif query_path.stem.startswith('04'):
                    finding = f"{row.channel} at hour {row.opened_hour:02.0f}:00 is the busiest channel-hour combination: {row.tickets:,.0f} tickets ({row.share_pct:.2f}% of demand).\nUse this as an input to rostering, then compare weekday demand and staffing capacity before making changes."
                else:
                    finding = f"{row.category} has the highest reopen rate among qualifying categories: {row.reopen_pct:.2f}% ({row.reopened_tickets:,.0f} / {row.tickets:,.0f} tickets).\nReview resolution notes and closure checks; missing public CSAT cannot be used to infer user satisfaction."
                (root / 'analysis/results' / f'{query_path.stem}_{dataset}.md').write_text(f'# {query_path.stem} — {dataset} data\n\n{finding}\n\n{table(frame)}\n', encoding='utf-8')
        report(root, con)
        raw_count = con.execute('select count(*) from raw.uci_events').fetchone()[0]
        metadata = json.loads((root / 'data/download.json').read_text())
        (root / 'data/SOURCE.md').write_text(f'''# Data provenance

## Public research data (primary analysis)

Amaral, C., Fantinato, M., & Peres, S. (2018). *Incident management process enriched event log*. UCI Machine Learning Repository. DOI: [10.24432/C57S4H](https://doi.org/10.24432/C57S4H).

- Source: https://archive.ics.uci.edu/dataset/498/incident+management+process+enriched+event+log
- Archive: {metadata['url']}
- Licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Data and derived public-data exports retain this licence; the MIT licence applies to project code.
- Initial download: {metadata['downloaded_at']}. Refreshes verify the pinned archive checksum; rebuilds do not rewrite the initial download date.
- Archive SHA-256: `{metadata['sha256']}`
- CSV SHA-256: `{metadata['csv_sha256']}`
- Loaded observations: {raw_count:,} audit rows, reduced to {summaries['public']['opened_tickets']:,} unique incidents.
- The source is anonymised; labels such as Category 46 are retained. No semantic category names are invented.
- Missing `?` values are unknown. Latest event chosen by update timestamp, then system modification count, then source row. SLA uses the final source `made_sla` flag, interpreted as true = met, with no invented contractual targets.
- Source timezone is unspecified. Timestamps remain source-local; they are not assumed to be Melbourne time.
- First-response time, verified first-contact resolution and CSAT are unavailable. They remain null.
- Negative resolution intervals: {summaries['public']['invalid_resolutions']:,}; unparseable nonmissing resolution timestamps: {summaries['public']['unparsed_resolutions']:,}. These are flagged, excluded from duration and SLA denominators, retained in volume, and treated as unresolved for backlog (possible overstatement).
- The source does not establish cancellation treatment or historic assignment ownership. Backlog is reconstructed from final timestamps and final group, with no inference about reopen intervals.

## Synthetic demonstration data (separate dataset)

Generated by `scripts/generate_tickets.py`, seed 71; {summaries['synthetic']['opened_tickets']:,} fictional tickets opened during calendar 2024, snapshot at 2025-01-01 00:00. Licence: MIT. No real users or copied incident records.

The synthetic dataset exercises all KPI fields and is the only dataset exposed by the GitHub Pages demo. Category, priority, channel, assignment group, timestamps, reopens, first-contact resolution and CSAT are simulated. Fictional resolution targets are P1: 4, P2: 8, P3: 24 and P4: 72 elapsed calendar hours. These are demonstration rules, not industry standards or an actual organisation's service agreement.
''', encoding='utf-8')
    results = json.loads((root / 'dbt/target/run_results.json').read_text())
    tests = [r for r in results['results'] if r['unique_id'].startswith('test.')]
    evidence = {'summaries':summaries, 'raw_event_rows':raw_count, 'dbt_models':len(results['results'])-len(tests), 'dbt_tests':len(tests), 'dbt_tests_passed':sum(r['status']=='pass' for r in tests)}
    (root / 'docs/evidence.json').write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8')
    readme(root, evidence)
    from scripts.export_site import export_site
    export_site(root)


def report(root, con):
    dataset = 'synthetic'; month = '2024-12-01'
    m = con.execute('select * from marts.kpi_monthly where dataset = ? and month = ?',[dataset,month]).df().iloc[0]
    prev = con.execute("select opened_tickets from marts.kpi_monthly where dataset='synthetic' and month='2024-11-01'").fetchone()[0]
    backlog, aged = con.execute("select sum(backlog_tickets), sum(case when age_bucket='31+ days' then backlog_tickets else 0 end) from marts.kpi_backlog where dataset=? and month=?", [dataset,month]).fetchone()
    cat = con.execute('''select c.category, k.breaches, k.eligible_tickets, k.sla_pct from marts.kpi_category k join marts.dim_category c using(category_key)
    where dataset=? and month=? order by breaches desc, category limit 1''', [dataset,month]).df().iloc[0]
    repeat = con.execute('''select c.category, count(*) as n, sum(reopened::integer) as reopens, 100*avg(reopened::integer) as rate from marts.fct_tickets f join marts.dim_category c using(category_key)
    where dataset=? and date_trunc('month',opened_at)=? group by 1 having count(*)>=100 order by rate desc, category limit 1''',[dataset,month]).df().iloc[0]
    (root / 'docs/monthly-service-report.md').write_text(f'''# Monthly service report | December 2024

**Synthetic demonstration — fictional service desk.** Prepared for an IT operations manager. Reporting snapshot: 1 January 2025, 00:00. Outcome rates describe tickets opened in December and observed by the snapshot; they are not December closure throughput.

December intake was **{m.opened_tickets:,} tickets**, compared with **{prev:,}** in November (**{100*(m.opened_tickets-prev)/prev:+.1f}%**). Of this intake, **{m.resolved_tickets:,}** had resolved by the snapshot. SLA compliance was **{m.sla_pct:.1f}%** across **{m.sla_eligible:,} eligible tickets**. Mean resolution time was **{m.mttr_hours:.1f} hours**; the median was **{m.median_resolution_hours:.1f} hours** and the 90th percentile **{m.p90_resolution_hours:.1f} hours**. The gap suggests a tail of slower tickets that merits review.

| Service measure | December result | Interpretation |
| --- | --- | --- |
| First contact resolution | {m.fcr_pct:.1f}% / {m.fcr_eligible:,} eligible | Resolved without escalation or reopening; explicit simulated flag |
| Reopen rate | {m.reopen_pct:.1f}% of {m.opened_tickets:,} opened tickets | Repeat work observed by snapshot |
| CSAT | {m.csat_mean:.2f} / 5 from {m.csat_responses:,} responses | Response coverage {m.csat_response_pct:.1f}% of resolved intake; possible selection bias |
| Total queue at snapshot | {backlog:,} tickets | All opening cohorts still unresolved |
| Queue aged at least 31 days | {aged:,} tickets | Requires ownership and next-action review |

**Recommended actions**

1. **Service delivery lead:** inspect the December {cat.category} breach cases: **{cat.breaches:,} of {cat.eligible_tickets:,} eligible tickets** missed the fictional target (**{100-cat.sla_pct:.1f}%**). Identify delay reasons before trialling a routing or capacity change; track the same cohort measure next month.
2. **Team leads:** give each of the **{aged:,} tickets aged at least 31 days** a named owner and next action in the next queue review. Monitor the aged count and closures from that list weekly; validate records before assuming staffing is the cause.
3. **Knowledge manager:** review closure checks and support articles for {repeat.category}, where **{repeat.reopens:,.0f} of {repeat.n:,.0f} December tickets reopened ({repeat.rate:.1f}%)**. Trial an improved resolution checklist and compare next month's reopen rate at the same observation age.

**Measurement limits:** calendar hours, no business-hour pauses; recent unresolved cases are excluded from outcome rates. Reopen exposure varies by ticket age. Final timestamps cannot reconstruct all reopen intervals. Results show how to use evidence, not the performance of a real employer. SQL evidence: `analysis/`; definitions: `docs/kpi-definitions.md`; source: `data/SOURCE.md`.
''', encoding='utf-8')


def readme(root, evidence):
    p = evidence['summaries']['public']; s = evidence['summaries']['synthetic']
    hotspot = pd.read_csv(root / 'analysis/results/01_sla_hotspots_public.csv').iloc[0]
    tail = pd.read_csv(root / 'analysis/results/02_resolution_tail_public.csv').iloc[0]
    template = (root / 'docs/README.template.md').read_text(encoding='utf-8')
    values = {'public_count':f"{p['opened_tickets']:,}", 'synthetic_count':f"{s['opened_tickets']:,}",
        'event_count':f"{evidence['raw_event_rows']:,}", 'model_count':str(evidence['dbt_models']), 'test_count':str(evidence['dbt_tests']),
        'public_sla':f"{p['sla_pct']:.2f}%", 'synthetic_sla':f"{s['sla_pct']:.2f}%", 'public_eligible':f"{p['sla_eligible']:,}", 'synthetic_eligible':f"{s['sla_eligible']:,}",
        'public_mttr':f"{p['mttr_hours']:.2f} h", 'synthetic_mttr':f"{s['mttr_hours']:.2f} h", 'public_reopen':f"{p['reopen_pct']:.2f}%", 'synthetic_reopen':f"{s['reopen_pct']:.2f}%",
        'synthetic_fcr':f"{s['fcr_pct']:.2f}%", 'synthetic_csat':f"{s['csat_mean']:.2f} / 5", 'synthetic_csat_n':f"{s['csat_responses']:,}",
        'hotspot_category':hotspot.category, 'hotspot_month':str(hotspot.month)[:7], 'hotspot_breaches':f'{hotspot.breaches:,}',
        'hotspot_eligible':f'{hotspot.eligible_tickets:,}', 'hotspot_rate':f'{hotspot.breach_pct:.2f}%',
        'tail_category':tail.category, 'tail_mean':f'{tail.mean_hours:,.2f}', 'tail_median':f'{tail.median_hours:,.2f}', 'tail_p90':f'{tail.p90_hours:,.2f}'}
    for key,value in values.items(): template = template.replace('{{'+key+'}}',value)
    (root / 'README.md').write_text(template, encoding='utf-8')
