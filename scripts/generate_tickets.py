"""Seeded fictional service desk data; never blended with public observations."""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

SEED = 71
COUNT = 20_000
AS_OF = datetime(2025, 1, 1)


def generate(path: Path, count: int = COUNT, seed: int = SEED):
    rng = random.Random(seed)
    categories = ['Access', 'Hardware', 'Network', 'Software', 'Email', 'Business apps']
    groups = ['Service desk', 'Desktop support', 'Infrastructure', 'Applications', 'Service desk', 'Applications']
    targets = {1: 4, 2: 8, 3: 24, 4: 72}
    rows = []
    for i in range(count):
        category = rng.choices(categories, [25, 17, 14, 20, 12, 12])[0]
        opened = datetime(2024, 1, 1) + timedelta(days=rng.randrange(366), hours=rng.choices(range(24), [1]*8+[5]*10+[2]*6)[0], minutes=rng.randrange(60))
        priority = rng.choices([1, 2, 3, 4], [4, 16, 56, 24])[0]
        reopened = rng.random() < (0.16 if category == 'Network' else 0.06)
        fcr = category in ['Access', 'Email', 'Software'] and rng.random() < 0.62 and not reopened
        duration = rng.lognormvariate(1.5, 1.05) * (2.2 if category in ['Network', 'Business apps'] else 1)
        if fcr:
            duration = rng.uniform(0.15, 1.2)
        response = min(duration, rng.uniform(0.05, 1.8))
        resolved = opened + timedelta(hours=duration)
        if resolved >= AS_OF or rng.random() < 0.025:
            resolved = None
        csat = rng.choices([1, 2, 3, 4, 5], [3, 5, 12, 30, 50])[0] if resolved and rng.random() < 0.35 else None
        first_response = opened + timedelta(hours=response)
        rows.append(dict(ticket_id=f'SYN{i+1:06d}', category=category, assignment_group=groups[categories.index(category)],
            priority=priority, channel=rng.choices(['Phone', 'Portal', 'Email', 'Chat'], [42, 30, 20, 8])[0],
            opened_at=opened.isoformat(), first_response_at=first_response.isoformat() if first_response < AS_OF else '',
            resolved_at=resolved.isoformat() if resolved else '', reopen_count=int(reopened),
            first_contact_resolution=fcr if resolved else '', csat=csat or '',
            source_sla_met='', sla_target_hours=targets[priority]))
    rows.sort(key=lambda row: row['ticket_id'])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == '__main__':
    generate(Path('data/raw/synthetic_tickets.csv'))
