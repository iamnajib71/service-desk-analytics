# Measurement contract

The fact grain is **one incident per dataset**. Every mart retains `dataset`; public and synthetic records are never pooled. Months are opening cohorts, not closing throughput. Outcomes are observed at each dataset's extraction snapshot. Recent tickets have less opportunity to resolve or reopen.

| Measure | Calculation and denominator | Caveat |
| --- | --- | --- |
| Intake | Count of tickets opened in cohort | Deduplicated UCI events |
| SLA compliance | Met / known SLA outcomes on valid resolved tickets | Public uses final source `made_sla`; synthetic uses elapsed resolution duration against fictional priority target |
| First contact resolution | True explicit FCR flags / known FCR flags on resolved tickets | Public unavailable; synthetic flag means resolved without escalation/reopen |
| First response | Mean minutes from opening to explicit first response | Public unavailable; not inferred from system creation |
| MTTR | Mean elapsed calendar hours from opened to valid resolved timestamp | Excludes unresolved and invalid timestamps; median and p90 accompany mean; not repair labour time |
| Backlog | Opened before snapshot and unresolved or resolved at/after snapshot | Snapshot is exclusive next-month start, capped at extraction; across all opening cohorts |
| Queue age | Snapshot minus opened timestamp in calendar days | Mutually exclusive buckets: below 2, 2 to below 8, 8 to below 31, at least 31 days |
| Reopen rate | Tickets with final reopen count above zero / all opened tickets | At least one reopen, not total reopening events; observation age varies |
| Demand | Count by source-local opening hour and channel | Public timezone unknown; no assumed Melbourne conversion |
| CSAT trend | Mean observed score (1–5); count and coverage provided | Public unavailable; synthetic optional responses; respondents may not represent all users |

Synthetic priority targets: P1 4h; P2 8h; P3 24h; P4 72h. These are explicitly fictional. No business-hour calendar, pause clock, staffing cost, contractual compliance or causal attribution is claimed.

Public event reduction: greatest update timestamp, then system modification count, then original row position. The latest event's priority/category/group and outcome fields are retained. Missing category/group maps to an explicit `Unknown` member. Negative resolved intervals and malformed resolution dates stay flagged on the fact; the resolution timestamp is nullified. This retains the ticket in volume, excludes the invalid outcome from MTTR and SLA, and may overstate unresolved backlog.

Public historical backlog uses final outcomes and final assignment group, so it cannot reconstruct queue transfers or resolution/reopen intervals. Treat it as a retrospective approximation. Synthetic backlog uses the same algorithm to make the measurement contract observable.

Dashboard cohort selection filters SLA, category, demand and snapshot age. Volume/reopen/CSAT trend charts preserve the full history and mark the selected cohort. All-month backlog means the latest available snapshot, never the sum of snapshots.
