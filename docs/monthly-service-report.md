# Monthly service report | December 2024

**Synthetic demonstration — fictional service desk.** Prepared for an IT operations manager. Reporting snapshot: 1 January 2025, 00:00. Outcome rates describe tickets opened in December and observed by the snapshot; they are not December closure throughput.

December intake was **1,708 tickets**, compared with **1,621** in November (**+5.4%**). Of this intake, **1,664** had resolved by the snapshot. SLA compliance was **90.0%** across **1,664 eligible tickets**. Mean resolution time was **7.2 hours**; the median was **2.8 hours** and the 90th percentile **18.7 hours**. The gap suggests a tail of slower tickets that merits review.

| Service measure | December result | Interpretation |
| --- | --- | --- |
| First contact resolution | 34.9% / 1,664 eligible | Resolved without escalation or reopening; explicit simulated flag |
| Reopen rate | 6.4% of 1,708 opened tickets | Repeat work observed by snapshot |
| CSAT | 4.15 / 5 from 609 responses | Response coverage 36.6% of resolved intake; possible selection bias |
| Total queue at snapshot | 529 tickets | All opening cohorts still unresolved |
| Queue aged at least 31 days | 485 tickets | Requires ownership and next-action review |

**Recommended actions**

1. **Service delivery lead:** inspect the December Network breach cases: **69 of 246 eligible tickets** missed the fictional target (**28.0%**). Identify delay reasons before trialling a routing or capacity change; track the same cohort measure next month.
2. **Team leads:** give each of the **485 tickets aged at least 31 days** a named owner and next action in the next queue review. Monitor the aged count and closures from that list weekly; validate records before assuming staffing is the cause.
3. **Knowledge manager:** review closure checks and support articles for Network, where **41 of 252 December tickets reopened (16.3%)**. Trial an improved resolution checklist and compare next month's reopen rate at the same observation age.

**Measurement limits:** calendar hours, no business-hour pauses; recent unresolved cases are excluded from outcome rates. Reopen exposure varies by ticket age. Final timestamps cannot reconstruct all reopen intervals. Results show how to use evidence, not the performance of a real employer. SQL evidence: `analysis/`; definitions: `docs/kpi-definitions.md`; source: `data/SOURCE.md`.
