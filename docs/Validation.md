# Validation record

Date: 12 November 2026.

## Executed checks

The complete 26-test suite passed on Python 3.13 in the Linux validation environment. It includes Streamlit AppTest interaction tests and temporary SQLite databases. The same 26-test suite passed on Python 3.12. Final runs: Python 3.13 — 26 passed in 12.81 seconds; Python 3.12 — 26 passed in 12.68 seconds. Alembic check reported no new upgrade operations after correcting constraint-name collisions. A local Streamlit process served HTTP 200 at its health endpoint and root page.

| Area | Verified |
|---|---|
| Schema | 33 application tables plus Alembic version table, FK enforcement, no FK integrity violations, migration/seed repeatability |
| Authentication | Argon2id hash storage, correct/incorrect login, persisted account lockout, one-time bootstrap |
| Organisation isolation | Read/write rejection for other-tenant IDs, database rejection of cross-tenant substation/actor links, scoped exports |
| Roles | Viewer cannot write or create users; organisation admin cannot assign platform role; platform cannot impersonate tenant inventory access |
| Account lifecycle | User and organisation deactivation blocks subsequent service calls |
| Inventory | Duplicate asset rejected with transaction rollback |
| Measurements | NaN/infinity/boolean rejection, timezone enforcement/UTC round trip, dry-type rejection of oil data, duplicate idempotency and conflicting-value rejection |
| Same-tenant integrity | Sensor belonging to another asset rejected by database composite FK |
| Synthetic fixtures | 150 readings, labelled gas evidence, below-detection value retained, one-time seed, atomic rollback under injected failure |
| Alerts | Tenant checks, acknowledgement idempotency, findings required before resolution, evaluation, reopen and fresh-finding requirement |
| Backups | Database-consistent backup, integrity check, preserved observations and refusal to overwrite backup |
| UI | Login/logout, measurement save, all available tenant pages, four task views, viewer restrictions, platform page |

## Limits of this validation

No real Windows desktop/browser session, mobile visual review, load test, penetration test, live hosting test or real equipment integration has been performed. Streamlit AppTest validates widget interaction and rendering logic; it is not a screenshot-based browser accessibility review. The tests do not certify production security.

Engineering diagnostic methods, health scoring, predictive models, bulk upload processing, work-order editing, PDF/XLSX report generation and email delivery are not implemented and have no passing functionality claims. The schema anticipates those milestones.

There are no invented engineering reference results or model performance statistics. Before enabling an engineering method, supply the applicable standard edition/criteria and validate independent examples.

The initial dataset and example alert are synthetic. Alert timing summaries can include those records and are labelled accordingly.
