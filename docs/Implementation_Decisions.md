# Implementation decisions

Schema approved by the project owner on 12 November 2026. Python/Streamlit/SQLite/SQLAlchemy and a future non-chatgpt.site address are retained. The architecture review is the design baseline; its original proposed-status wording is retained for traceability.

The first implementation advances foundation, inventory and selected monitoring workflows. All 33 entities exist; presence of a table does not imply its full business module is implemented.

- SQLAlchemy models are split into identity, inventory, acquisition, engineering and operations modules. Shared UTC/UUID helpers are separate. Model count excludes Alembic's version table.
- Timestamps reject naive values. Database storage is UTC; UI uses EAT.
- Cross-organisation links are constrained by composite foreign keys. Additional sensor/asset/parameter and sample/assessment/asset constraints protect several same-organisation relationships.
- Platform administrators provision tenants but do not impersonate organisation actors. Platform audit records have a null organisation and identify the target tenant in details. Tenant operations require a tenant user.
- All models carry created/updated timestamps for consistent administration. History append behavior is enforced through the exposed services; someone with direct filesystem/database access can bypass application policies. Database triggers for immutable history are not claimed.
- Primary/FK/unique/check constraints are implemented, but engineering-specific cross-field applicability and method lifecycle validation will be completed with their modules. Direct ORM access is internal and must not be exposed as an unrestricted endpoint.
- The synthetic seed operation uses a shared transaction context so its nested service writes commit or roll back together.
- DGA gas codes are constrained in the gas measurement table. No extra gas-code table is introduced.
- Health-index, threshold evaluation, predictions and diagnosis are deliberately inactive until validated engineering criteria are supplied. Sample alerts identify scenarios, not algorithmic findings.
- Dashboard views affect layout, not permissions. Account role is re-read server-side on every service call.
- Idle session limit is 30 minutes and absolute lifetime is 8 hours, checked on interactions/reruns. Failed sign-ins lock an account for 15 minutes after five attempts. Distributed/IP throttling, password recovery and MFA remain deployment-readiness work.
- Unit conversion and measurement corrections are not exposed yet. Conflicting values at an existing observation identity are rejected rather than overwritten.
- Measurement list/export is bounded at 100,000 rows in this release; the UI discloses this cap. Pagination and asynchronous large exports are future work.
- No existing live workflow events are imported. Legacy roles do not establish actor identity.
- Render is not connected or provisioned by this package; external deployment remains pending connection, paid-plan approval and acceptance testing.
