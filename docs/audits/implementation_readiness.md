# Implementation Readiness Audit

Authority: README.md is the single product truth.

## Scope
This audit maps README.md concepts to the documented roadmap and the current repo layout. It records gaps and decisions required before implementation work can proceed.

## Repo state summary
- Governance and documentation: Phase 1 complete.
- Application code: Initialization authorized. `app/` folder creation in progress.
- Status: **BUILD PHASE ACTIVE**.

## Mapping: README concepts -> roadmap/specs -> code folders
- Backend Core: `app/main.py`, `app/models.py` (Authorized)
- API Routes: `app/routers/` (Authorized)
- Domain Logic: `app/services/` (Authorized)

## Execution Plan (Code Implementation)
1. **Iteration 4 (Current)**: Initialize FastAPI skeleton, Database models (User/Shift/Equipment), and Core Shift API based on `api_specs.md`.
2. Iteration 5: Implement Auth0 integration, User profiles endpoint, and Equipment availability logic.
3. Iteration 6: Implement Conflict Detection Engine v1 and basic caching (Redis).

## Gaps
- No implementation specs, data models, or API definitions are present.
- No documentation maps roadmap phases to required data schemas, workflows, or compliance rules.
- No codebase exists to verify folder ownership or module boundaries.
- Mobile offline-first sync rules and conflict handling are not specified.
- Marketplace reputation, dispute handling, and pricing rules are not documented.
- Financial accounting assumptions (taxes, overtime, cost attribution) are undefined.

## Decisions required
- Confirm the target vertical for Phase 1 MVP.
- Define authoritative data schemas for users, memberships, shifts, and financial records.
- Specify API boundaries and integration protocols for named systems.
- Define UX flows for workflow states and conflict resolution paths.
- Confirm compliance scope by region and industry standards.
- Define mobile offline-first sync rules and conflict resolution approach.
- Define marketplace reputation inputs, dispute rules, and pricing model details.
- Define financial accounting assumptions tied to the Financial Intelligence Engine.

## Ordered plan for the next 3 iterations (docs only)
1. Iteration 10: Frontend Initialization (CORS, Types, Axios Client).
2. Iteration 11: Auth Pages (Login with JWT).
3. Iteration 12: Event & Shift Dashboard.
