"""Export synthetic-only Plotly dashboard for free, serverless GitHub Pages hosting."""
import json
from pathlib import Path
from plotly.offline import get_plotlyjs
from dashboard.charts import figures, metrics


def export_site(root: Path):
    site = root / 'site'; site.mkdir(exist_ok=True)
    data = json.loads((root / 'dashboard/data/synthetic.json').read_text())
    bundles = {}
    for month in ['All months']+[row['month'] for row in data['kpi_monthly']]:
        bundles[month] = {'metrics':metrics(data,month), 'charts':[{'title':t,'subtitle':s,'figure':json.loads(f.to_json())} for t,s,f in figures(data,month)]}
    (site / 'charts.json').write_text(json.dumps(bundles, allow_nan=False), encoding='utf-8')
    (site / 'plotly.min.js').write_text(get_plotlyjs(), encoding='utf-8')
    (site / 'index.html').write_text((root / 'dashboard/site.html').read_text(encoding='utf-8'), encoding='utf-8')
    (site / '.nojekyll').touch()
