# API Specifications - Phase 1

**Authority**: README.md (IAM, Time Engine, Conflict Engine, Financial Engine, Integration and Ecosystem)

## Objectif
Lister les endpoints minimaux pour le MVP Phase 1. Les details d'implementation (framework, auth provider, format exact) doivent etre valides par les owners.

---

## Authentification
Reference: IAM

- **Auth**: OAuth2 / SSO (provider a valider)
- **Tokens**: JWT (a valider)

Endpoints MVP:
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`

---

## Users
Reference: IAM

- `GET /users/me`
- `PATCH /users/me/availability`
- `PATCH /users/me/skills`

---

## Shifts (Time Engine)
Reference: Time and Reservation Engine

- `POST /shifts`
- `GET /shifts`
- `GET /shifts/{shift_id}`
- `PATCH /shifts/{shift_id}`

Validation minimale:
- `start_time < end_time`
- `timezone` explicite ou derivee de l'organisation
- `economic_value.amount >= 0`

---

## Conflict Engine
Reference: Conflict Detection and Resolution Engine

- `GET /shifts/{shift_id}/conflicts`
- `POST /shifts/{shift_id}/resolve`

Regles (Phase 1):
- CRITICAL et HIGH uniquement (cf. README.md)

---

## Financial Records
Reference: Financial Intelligence Engine

- `GET /financial-records`
- `GET /financial-records/export` (CSV)

Donnees minimales:
- `type`: estimated / actual
- `amount`, `currency`

---

## Integrations (Phase 1)
Reference: Integration and Ecosystem

- Calendrier (Google/Outlook/iCal) - selection exacte a valider
- Endpoint generique:
  - `POST /integrations/calendar/sync`

---

## Webhooks
Reference: API ecosystem (webhooks: real time events)

- `shift.conflict.detected`
- `shift.status.changed`

---

## Regles d'API
- Rate limiting a definir (cibles SLA dans README.md)
- Erreurs standard: `400`, `401`, `403`, `404`, `409`, `422`
- Toutes les dates en UTC

---

## Prochaines etapes
1. Valider le fournisseur IAM et les formats de token.
2. Completer les schemas exacts de requete/response avec `docs/data_models.md`.
3. Generer la spec OpenAPI.
