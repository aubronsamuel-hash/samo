# organisation_industrielle_coder.md

Authority: README.md is the single product truth.

## Objectif
Mettre en place une organisation lourde, durable et auditable pour travailler avec Codex/OpenAI, sans inventer de scope produit au-dela de README.md.

## Philosophie non negociable
- Codex est un executant supervise, jamais un decideur produit.
- Une seule autorite finale: README.md.
- Traçabilite stricte entre intention produit, decision et execution.
- Une iteration = une intention claire, un livrable, une validation.

## Ordre d autorite
1. README.md (verite produit)
2. AGENT.md (gouvernance du depot)
3. docs/agents/*.md (gouvernance par domaine)
4. docs/audits/** (constats et readiness)
5. code/ (implementation)

Si un niveau contredit un niveau superieur: stop et escalation.

## Roles industriels (poles)
### Pole pilotage produit
**Responsabilite:** verifier la coherence produit avec README.md.  
**Interdit:** coder, redefinir la roadmap.

### Pole documentation et coherence
**Responsabilite:** verifier les liens README.md -> specs -> execution.  
**Livrable:** docs/audits/implementation_readiness.md.

### Pole architecture
**Responsabilite:** invariants techniques, decoupages, dette.  
**Interdit:** inventer des exigences fonctionnelles.

### Pole backend
**Responsabilite:** implémenter les services et flux autorises par README.md.  
**Interdit:** deduire des regles non documentees.

### Pole frontend
**Responsabilite:** UI/UX conforme aux docs UX.  
**Interdit:** logique metier implicite.

### Pole securite
**Responsabilite:** IAM, permissions, audit trail, risques.  
**Interdit:** redefinir la politique produit.

### Pole qualite
**Responsabilite:** scenarios de test, non regression, seuils.  
**Interdit:** modifier la spec.

### Pole devops
**Responsabilite:** CI/CD, reproductibilite, guardrails.  
**Interdit:** changer la gouvernance.

## Workflow industriel (iteration controlee)
1. Audit readiness (docs/audits/implementation_readiness.md)
2. Proposition d une iteration unique
3. Validation humaine explicite
4. Execution par l agent mandate
5. Rapport et controle
6. Validation humaine
7. Commit

## Format de sortie standard (pour toute iteration)
1. Intention de l iteration
2. Contexte d autorite (fichiers references)
3. Travail effectue
4. Fichiers modifies
5. Commandes a executer localement
6. Resultat attendu
7. Risques / limites
8. Validation requise ? (oui/non)

## Limites et escalations
- Ambiguite ou conflit -> consigner dans docs/agents/agents_audit.md et escalader.
- Aucun ajout de fonctionnalite sans trace explicite dans README.md.
- Aucun code si les prerequis documentaires ne sont pas valides.
