# TECM

Transformer and Equipment Condition Monitoring System — foundation release 0.1.

This is the Python implementation of the approved TECM architecture, using Streamlit, SQLite and SQLAlchemy. It carries forward the existing GridWatch dashboard's asset, operations, maintenance and supervisor workflows. The application is an incremental implementation, not a claim that all planned engineering modules are complete.

## What works

- All 33 approved relational models and a frozen Alembic initial migration.
- UUID keys, UTC timestamps, indexes, unique/check constraints and tenant-qualified foreign keys.
- Argon2id login, failed-login lockout, session expiry, logout, account/organisation deactivation and server-side permission checks.
- Platform provisioning of organisations and their initial administrator; tenant administrators create users in their own organisation.
- Substation registration, equipment registration, oil/dry transformer nameplate details.
- Validated manual measurements, duplicate protection, provenance, persisted history and Plotly trends.
- Four dashboard task views. Changing a view never changes account permissions.
- Evidence display for oil/DGA samples, inspections, relay events and maintenance logs.
- Alert acknowledgement, verification, handoff, findings, resolution, reopening and clarity feedback with actor/time audit records.
- Tenant-scoped measurement CSV downloads for authorised users.
- Optional, explicitly synthetic seed dataset: two transformers, 150 readings, gas sample, inspection, relay event, maintenance log and alert.
- Consistent SQLite backup and integrity verification.

## Planned next milestones

CSV/XLSX bulk import, manual DGA/test entry, editable work orders, automated engineering limits and alert generation, validated DGA/thermal/insulation methods, health-index calculation, predictive analytics, PDF/XLSX reports, email delivery and external hosting are not implemented in this release. Their schema is present. No algorithm claims a confirmed fault or a validated failure probability. Health stays “Not assessed” rather than inventing a score.

No records from the live GridWatch database have been migrated. The old website remains unchanged. New example evidence is synthetic.

## Windows quick start

Extract this ZIP to a new folder, for example `Documents\TECM_Python`, and open the extracted `TECM` folder in VS Code. Preserve any version you are developing separately.

Run these commands in PowerShell from the folder containing `app.py`:

```powershell
py -3.15 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m scripts.manage init
.\.venv\Scripts\python.exe -m scripts.manage bootstrap
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The bootstrap command prompts for your platform administrator email, name and password. Password entry is hidden. There are no default credentials. Use at least 12 characters. Bootstrap only works before the first user is created.

Open the Local URL printed by Streamlit, normally `http://localhost:8501`. This is local access, not the future hosted URL.

1. Sign in with your platform administrator account.
2. Create an organisation and its administrator account in Organisation administration.
3. Sign out; sign in with the organisation administrator account.
4. Open Sample data and deliberately load the labelled synthetic examples, or create a substation and transformer yourself.
5. Open Measurements to record observations and Overview to inspect trends.
6. Use Users to create engineer, technician or viewer accounts. Supervisor access can use the viewer role and Supervisor task view.

You do not need to activate the environment when using its full Python path as above. In VS Code select `.venv\Scripts\python.exe` through Python: Select Interpreter.

## Permissions

| Role | Initial capabilities |
|---|---|
| Platform administrator | Organisation provisioning and activation; no tenant impersonation |
| Organisation administrator | Inventory, readings, alerts, users, CSV export and sample-data loading |
| Electrical engineer | Inventory, readings, alerts including resolution, feedback and CSV export |
| Maintenance engineer | Read inventory, readings, alerts including resolution, feedback and CSV export |
| Technician | Read inventory, readings, alert acknowledgement/findings and feedback |
| Viewer | Read inventory/evidence, evaluate alert clarity and export measurement CSV |

Maintenance permissions are seeded for the upcoming work-order milestone. No public registration or invitation emails are sent. Password reset and MFA are not yet implemented; internet deployment requires their operational/security review and additional rate limiting at the edge.

## Configuration and database

The default database is `data/tecm.db`, created only by `scripts.manage init`. Copy `.env.example` to `.env` if changing its location. `TECM_DATA_DIR` changes the default database folder, while `TECM_DATABASE_URL` explicitly selects the connection string. Do not commit `.env`, live database files, uploads or secrets.

All observation timestamps must carry a timezone. Entry forms use Africa/Nairobi (EAT); storage uses UTC. Numeric validation rejects non-finite values. This milestone accepts the parameter's canonical unit only; unit conversion is deliberately not implicit.

The included `data/sample_data/tecm_reference.sqlite` contains schema and reference catalogues only, with no users, passwords or operational records. It can be inspected with DB Browser. It is not automatically used by the application.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Tests create isolated temporary databases, including temporary test accounts. Test passwords exist only in fixtures and are never seeded into the application database. Test outcomes and coverage limits are in `docs/Validation.md`.

## Backup and restore

```powershell
.\.venv\Scripts\python.exe -m scripts.manage backup --destination backups\tecm_backup_001.sqlite
```

This uses SQLite's backup API and checks the result. The destination must not already exist. Keep backups on independent protected storage. To restore: stop all app processes, retain the current database and sidecars as a rollback copy, restore the verified backup to the configured database path, ensure no old WAL/SHM sidecars remain at that path, and restart. Test this procedure on a disposable copy before production use. Do not copy a live database file alone while WAL is active.

Alembic migrations run through `python -m scripts.manage init`; it also seeds reference data idempotently. Destructive downgrade is disabled. Back up before future migrations.

## Future hosting outside chatgpt.site

Target: one Python service with a persistent local disk, such as a paid Render service. Suggested start command after provisioning a disk and securely bootstrapping accounts:

```sh
python -m scripts.manage init && python -m streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT --server.headless=true
```

Set `TECM_DATA_DIR` to a directory on the persistent mount, such as `/var/data/tecm`. The SQLite database must not live on an ephemeral filesystem. Use one service instance. Do not launch multiple replicas against one SQLite file or put the file on a network share.

The hosted address will be provider-issued (for example an available onrender.com hostname) or an owner-controlled domain, not chatgpt.site. No hostname has been reserved, no hosting resources created, and no working hosted URL exists for this release.

Before deployment: connect the hosting account, approve the actual paid plan, secure administrator provisioning, perform browser/security acceptance tests, configure backups and verify restart persistence. Login-required application data is distinct from a network-private service; decide whether a gateway/VPN is required. The existing site remains untouched.

## Structure

- `database/models/`: five domain model modules plus shared identity/time helpers.
- `database/migrations/`: frozen initial migration and Alembic environment.
- `modules/`: authentication, inventory, acquisition, monitoring and alert services.
- `dashboard/pages.py`: Streamlit presentation only.
- `scripts/manage.py`: database migration, initial administrator and backup commands.
- `tests/`: service, constraint and Streamlit AppTest coverage.
- `docs/`: approved architecture baseline, decisions, schema SQL and validation report.

Reference: SQLAlchemy composite foreign keys https://docs.sqlalchemy.org/en/20/core/constraints.html; SQLite enforcement https://docs.sqlalchemy.org/en/20/dialects/sqlite.html; Streamlit testing https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest.
