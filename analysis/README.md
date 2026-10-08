# SQL questions and findings

Each `.sql` file is executable in DuckDB with the named parameter `dataset` set to `public` or `synthetic`. Rebuild regenerates CSV result tables and two-line findings under `results/`. They describe observations, not causal explanations. Public metrics are based on anonymised source categories; synthetic metrics are fictional.

| Question | Query | Public evidence | Synthetic evidence |
| --- | --- | --- | --- |
| Which high-volume category-months breach SLA most? | [01](01_sla_hotspots.sql) | [Result and finding](results/01_sla_hotspots_public.md) | [Result and finding](results/01_sla_hotspots_synthetic.md) |
| Does the mean hide a long resolution tail? | [02](02_resolution_tail.sql) | [Result and finding](results/02_resolution_tail_public.md) | [Result and finding](results/02_resolution_tail_synthetic.md) |
| Who owns the ageing queue at the latest snapshot? | [03](03_queue_risk.sql) | [Result and finding](results/03_queue_risk_public.md) | [Result and finding](results/03_queue_risk_synthetic.md) |
| Which channel and hour drive demand? | [04](04_channel_staffing.sql) | [Result and finding](results/04_channel_staffing_public.md) | [Result and finding](results/04_channel_staffing_synthetic.md) |
| Which categories generate repeat work? | [05](05_repeat_work.sql) | [Result and finding](results/05_repeat_work_public.md) | [Result and finding](results/05_repeat_work_synthetic.md) |

Run one directly after building:

```python
from pathlib import Path
import duckdb
with duckdb.connect('artifacts/service_desk.duckdb', read_only=True) as con:
    print(con.execute(Path('analysis/01_sla_hotspots.sql').read_text(), {'dataset': 'public'}).df().to_string(index=False))
```
