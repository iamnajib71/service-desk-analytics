"""Load immutable CSVs into raw; record download provenance and hashes."""
import hashlib
import json
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
import duckdb
from scripts.generate_tickets import generate

URL = 'https://archive.ics.uci.edu/static/public/498/incident+management+process+enriched+event+log.zip'


def ingest(root: Path, database: Path):
    raw = root / 'data/raw'
    raw.mkdir(parents=True, exist_ok=True)
    csv = raw / 'incident_event_log.csv'
    archive = raw / 'uci.zip'
    if not archive.exists():
        with urllib.request.urlopen(URL, timeout=120) as response:
            archive.write_bytes(response.read())
    metadata_path = raw.parent / 'download.json'
    existing = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
    archive_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
    if existing.get('sha256') and existing['sha256'] != archive_hash:
        raise ValueError('UCI archive checksum changed. Review provenance before accepting new data.')
    with zipfile.ZipFile(archive) as zipped:
        csv.write_bytes(zipped.read('incident_event_log.csv'))
    generate(raw / 'synthetic_tickets.csv')
    database.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(database)) as con:
        con.execute('create schema if not exists raw')
        con.execute("create or replace table raw.uci_events as select row_number() over () as source_row, * from read_csv(?, all_varchar=true)", [str(csv)])
        con.execute("create or replace table raw.synthetic_tickets as select * from read_csv(?, all_varchar=true)", [str(raw / 'synthetic_tickets.csv')])
    metadata = {'url': URL, 'downloaded_at': existing.get('downloaded_at', datetime.now(timezone.utc).isoformat()),
        'sha256': archive_hash, 'csv_sha256': hashlib.sha256(csv.read_bytes()).hexdigest()}
    metadata_path.write_text(json.dumps(metadata, indent=2)+'\n', encoding='utf-8')
