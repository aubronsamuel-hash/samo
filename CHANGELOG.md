# Changelog

## 0.2.0 - Start of Implementation
- **Transition**: Passage officiel de la phase de conception à l'implémentation (Phase 1).
- **Scope**: Autorisation de création du dossier `app/` pour le backend FastAPI.
- **Docs**: Validation des itérations documentation 1, 2 et 3 (Scope, Models, Specs).

## 0.1.0
- Mise en place de la structure backend Phase 1 selon README.md et docs/phase1_scope.md.
- Ajout de l'endpoint POST /shifts avec detection de conflits (double booking technicien, equipement indisponible) conforme a docs/api_specs.md et docs/data_models.md.
- Ajout des modeles SQLAlchemy et schemas Pydantic pour Shift/User/Equipment selon docs/data_models.md.
- Ajout des tests backend pour la creation de shifts et la detection de conflits selon docs/api_specs.md.
