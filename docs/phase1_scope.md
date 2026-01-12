# Phase 1: Foundation - Scope MVP

**Authority**: README.md ("Roadmap strategique" + "Moteurs du systeme")

## Contexte
Ce document definit le perimetre du MVP Phase 1 afin d'eviter toute derive de scope. Toute demande hors perimetre doit etre escaladee via AGENT.md.

## Vertical ciblee (a valider)
- **Vertical**: [A completer]
- **Justification**: [A completer]
- **Validation**: 3 experts metier minimum

---

## Capacites incluses (Must-Have)
Ces capacites sont strictement alignees sur la Phase 1 du README.md.

| Capacite | Reference README.md | Definition de succes | Responsable agent |
| --- | --- | --- | --- |
| IAM (SSO, OAuth2, RBAC, audit trail) | Identity and Access Management | Auth functionnelle + roles + journalisation | backend_agent.md |
| Time Engine (creation de shifts) | Time and Reservation Engine | Shifts crees avec intervalle temporel + ressources + valeur economique | backend_agent.md |
| Conflits basiques | Conflict Detection and Resolution Engine | Detection des conflits CRITICAL et HIGH | architecture_agent.md |
| Matching simple | Resource and Matching Intelligence Engine | Matching de base selon competences et disponibilites | architecture_agent.md |
| Mobile planning | Mobile first experience | Consultation offline du planning + sync | frontend_agent.md |
| Finance tracking simple | Financial Intelligence Engine | Calculs "estimated" et budget tracking de base | finance_agent.md |

---

## Non-goals (exclus pour Phase 1)
Base sur le README.md (Phases 2-4) :
- Execution engine complet (timesheets, approvals, workflows avances)
- Marketplace et trust engine
- Notifications avancees et intelligence
- Multi-organization scale
- Integrations avancees (au-dela du calendrier)

---

## Metriques de succes (Phase 1)
Les cibles doivent respecter les metriques globales du README.md.

| Metrique | Cible Phase 1 | Source |
| --- | --- | --- |
| Time to value | < 3 minutes | Analytics produit |
| Feature adoption (core workflows) | > 80% | Analytics produit |
| Conflict resolution | < 2 heures en moyenne | Conflict Engine logs |
| Response time p95 | < 150 ms | Observabilite technique |

---

## Decisions techniques a valider
README.md ne fixe pas de stack; ces elements sont donc **a trancher** par les owners.

- **Backend**: [A completer]
- **Frontend / Mobile**: [A completer]
- **Auth provider**: [A completer]
- **Base de donnees**: [A completer]
- **Cache / sync offline**: [A completer]

---

## Regles de conflit (Phase 1)
Alignement sur la matrice de priorites du README.md :

- **CRITICAL**: legal_violation, double_booking_same_org, budget_hard_limit
- **HIGH**: double_booking_cross_org, missing_mandatory_skill, equipment_unavailable
- **MEDIUM**: budget_warning, certification_expiring, skill_mismatch
- **LOW**: preference_conflict, overtime_risk

---

## Prochaines etapes
1. Valider la verticale ciblee.
2. Completer les schemas de donnees dans `docs/data_models.md`.
3. Definir les endpoints MVP dans `docs/api_specs.md`.
4. Demarrer le prototype du Conflict Engine (Phase 1).
