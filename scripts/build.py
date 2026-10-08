"""One command: raw ingestion -> dbt build -> evidence -> tests."""
import os
from pathlib import Path
import subprocess
import sys
import sysconfig

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.ingest import ingest


def main():
    os.chdir(ROOT)
    database = ROOT / 'artifacts/service_desk.duckdb'
    ingest(ROOT, database)
    environment = {**os.environ, 'WAREHOUSE_PATH': database.as_posix(), 'DBT_SEND_ANONYMOUS_USAGE_STATS': 'false'}
    dbt = Path(sysconfig.get_path('scripts')) / ('dbt.exe' if os.name == 'nt' else 'dbt')
    subprocess.run([str(dbt), 'build', '--project-dir', 'dbt', '--profiles-dir', 'dbt'], env=environment, check=True)
    from scripts.evidence import export_evidence
    export_evidence(ROOT, database)
    subprocess.run([sys.executable, '-m', 'pytest', '-q', 'tests'], check=True)
    print('BUILD COMPLETE | warehouse, dbt tests, SQL results, report and dashboard data ready', flush=True)


if __name__ == '__main__':
    main()
