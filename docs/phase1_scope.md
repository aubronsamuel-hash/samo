# Phase 1: Foundation - Scope MVP

**Authority**: README.md ("Roadmap strategique" + "Moteurs du systeme")

## Contexte
Ce document definit le perimetre du MVP Phase 1 afin d'eviter toute derive de scope. Toute demande hors perimetre doit etre escaladee via AGENT.md.

## Vertical ciblee (Spectacle/Evenementiel)
- **Vertical**: Spectacle Vivant & Prestation Evenementielle
- **Sous-secteur**: Gestion des equipes techniques (son, lumiere, video, scenographie)
- **Justification**:
  - **Besoins critiques**:
    - Coordination en temps reel des techniciens (ex: 50+ personnes sur un festival).
    - Gestion des conflits de materiel (ex: 2 consoles son demandees en meme temps).
    - Facturation complexe (forfaits jour/nuit, penalites retard, options materiel).
  - **Marche porteur**:
    - 15 000 evenements/an en France (source: France Evenements).
    - Taux de turnover eleve chez les prestataires (30% en moyenne).
  - **Reglementation**:
    - Convention collective "Spectacle Vivant" (accords sur les heures de nuit/week-end).
    - Normes securite (ERP, commission de securite).
- **Validation**:
  - Experts metier:
    - Jean-Michel Leroy (Regisseur General, Festival d'Avignon)
    - Claire Martin (Cheffe Technique, Zenith Paris)
    - Thomas Dubois (Gerant, Societe Sonorisation Pro)

---

## Capacites incluses (Must-Have)
Ces capacites sont strictement alignees sur la Phase 1 du README.md.

| Capacite | Reference README.md | Definition de succes | Responsable agent | Priorite |
| --- | --- | --- | --- | --- |
| IAM (SSO, OAuth2, RBAC, audit trail) | Identity and Access Management | 95% des users connectes en <1.5s (Auth0) | backend_agent.md | P0 |
| Creation de plannings techniques | Time and Reservation Engine | Planning cree avec validation conflits materiel/humain | backend_agent.md | P0 |
| Detection conflits materiel/humain | Conflict Detection and Resolution Engine | 100% des chevauchements detectes (tolerance: 15 min) | architecture_agent.md | P0 |
| Matching competences/equipements | Resource and Matching Intelligence Engine | 85% des besoins couverts automatiquement | architecture_agent.md | P1 |
| Mobile: fiche de poste digitale | Mobile first experience | Acces offline aux infos techniques (cablage, patchs) | frontend_agent.md | P0 |
| Tracking financier forfaits/options | Financial Intelligence Engine | Export PDF des devis valides par les producteurs | finance_agent.md | P1 |

---

## Non-goals (exclus pour Phase 1)
Base sur le README.md (Phases 2-4) :
- Gestion des artistes (Phase 2)
- Billetterie integree (Phase 3)
- Streaming live (Phase 4)
- Multi-evenements simultanes (Phase 2)
- IA predictive (Phase 3)

---

## Metriques de succes (Phase 1)
Les cibles doivent respecter les metriques globales du README.md.

| Metrique | Cible Phase 1 | Source de verite | Responsable |
| --- | --- | --- | --- |
| Taux de plannings sans conflit | >= 92% | Logs Conflict Engine | Backend |
| Temps de creation planning | < 5s | Latency metrics (FastAPI) | DevOps |
| Taux d'adoption mobile | >= 80% | Mixpanel (evenement `tech_sheet_viewed`) | UX |
| Precision matching equipement | >= 85% | % besoins couverts sans ajustement manuel | Data Science |
| Conformite conventions collectives | 100% | Audit Trail (table `labor_compliance_logs`) | Legal |

---

## Decisions techniques validees
Alignement sur README.md (stack a expliciter par la verticale).

1. **Stack technique**:
   - **Backend**: Python 3.10 + FastAPI + PostgreSQL 15 (avec extension PostGIS pour les plans de salle).
   - **Mobile**: React Native + SQLite (pour les donnees offline: plans de cablage, patchs audio).
   - **Auth**: Auth0 (avec MFA pour les admins).
   - **Cache**: Redis (pour les disponibilites des techniciens/materiel).
   - **Stockage fichiers**: AWS S3 (pour les riders techniques en PDF).

2. **Regles de conflit specifiques**:
   - **Priorites**:
     1. Urgences techniques (ex: panne son pendant un spectacle).
     2. Maintenance reglementaire (ex: controle securite des nacelles).
     3. Installations (montage/demontage).
     4. Repetitions.
   - **Resolution**:
     - Conflit CRITICAL (ex: 2 inges son sur la meme console) -> Escalade au regisseur.
     - Conflit HIGH (ex: chevauchement de 30 min) -> Proposition de swap automatique.

3. **Donnees offline**:
   - **Strategie**: Les fiches techniques (cablage, patchs) et les plannings sont disponibles offline.
   - **Conflits de sync**: "Last write wins" sauf pour les urgences techniques (manuel).

4. **Securite**:
   - Chiffrement: AES-256 pour les donnees sensibles (ex: `Technician.license_number`).
   - **Audit Trail**: Toute modification de `Shift.status` ou `Equipment.availability` est loguee.

---

## Regles metier specifiques (Spectacle)
1. **Conventions collectives**:
   - **Heures de nuit** (22h-6h): +50% (vs +30% dans la sante).
   - **Temps de repos**: 12h minimum entre 2 shifts (vs 11h dans la sante).
   - **Forfait repas**: 15 EUR/jour si shift > 6h.

2. **Equipements**:
   - **Categories**:
     - **Son**: Consoles (Yamaha CL5, DiGiCo SD10), microphones (Shure SM58), retours.
     - **Lumiere**: Projecteurs (Moving Heads, PAR LED), tables (MA2, Chamsys).
     - **Videos**: Serveurs (Resolume, Millumin), ecrans LED.
   - **Maintenance**: Tout equipement doit avoir un `last_maintenance_date` < 6 mois.

3. **Workflows**:
   - **Creation d'un planning**:
     1. Import du rider technique (PDF/Excel).
     2. Assignment automatique des techniciens (par competences).
     3. Validation par le regisseur.
     4. Envoi des fiches de poste aux techniciens (mobile).
   - **Jour J**:
     - Check-in/check-out via QR code (pour tracer les heures reelles).
     - Signalement des incidents (ex: materiel defectueux) via l'app mobile.

---

## Prochaines etapes
1. [x] Valider la verticale avec 3 experts (fait le 20/01).
2. [ ] Implementer le `ConflictEngine` avec regles spectacle.
3. [ ] Integrer un parseur de riders techniques (PDF -> donnees structurees).
4. [ ] Tester le workflow mobile avec 5 techniciens son/lumiere.
