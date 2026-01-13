# Prompt Codex - Documentation backend PlanningHub

Authority: README.md est la source de verite pour le produit PlanningHub.

Utilisez ce prompt pour demander a Codex de produire une documentation backend conforme au scope du README.md et aux regles d AGENT.md.

---

## Prompt

```
En tant qu agent de documentation backend, je dois creer un guide complet pour le backend du projet PlanningHub. Ce guide doit inclure les instructions pour lancer le backend, le tester, et fournir des informations essentielles pour les developpeurs.

### Instructions generales

- Respecter le scope et les priorites du README.md (source de verite).
- Ne pas inventer de fonctionnalites ou de workflows absents du README.md.
- S appuyer sur les documents existants :
  - docs/api_specs.md
  - docs/data_models.md
  - docs/agents/backend_agent.md
- Referencer les fichiers backend reelles pour les commandes et les variables d environnement.
- Indiquer les differences entre environnement local et execution en conteneur si applicable.

### Structure du guide

1. Introduction
   - Description brieve du role du backend PlanningHub.
   - Mentionner l alignement avec les moteurs du README.md.

2. Prerequis
   - Python 3.10+ (aligner avec le Dockerfile si utilise).
   - FastAPI, SQLAlchemy, Redis, et autres dependances listées dans planninghub/backend/requirements.txt.
   - Docker (optionnel pour execution en conteneur).

3. Installation
   - Cloner le depot.
   - Installer les dependances : `pip install -r planninghub/backend/requirements.txt`.

4. Configuration
   - Creer un fichier `.env` a la racine de `planninghub/backend`.
   - Exemple de variables (aligner avec planninghub/backend/app/config.py) :
     - `DATABASE_URL`
     - `REDIS_URL`
     - `AUTH0_DOMAIN`
     - `AUTH0_API_AUDIENCE`
     - `AUTH0_ALGORITHMS`
     - `SECRET_KEY`

5. Lancement
   - Mode developpement : `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.
   - Mode conteneur : `docker build -t planninghub-backend planninghub/backend` puis `docker run -p 8000:8000 planninghub-backend`.

6. Tests
   - Executer la suite : `pytest` depuis `planninghub/backend`.
   - Mentionner les tests existants et leur role (auth, conflits, shifts, equipment, etc.).

7. API Documentation
   - Swagger UI disponible sur `http://localhost:8000/docs`.
   - Lister les endpoints majeurs avec exemples issus de docs/api_specs.md.

8. Depannage
   - Erreurs de configuration `.env`.
   - Dependances manquantes.
   - Redis ou base de donnees indisponible.

9. Contribution
   - Suivre les regles AGENT.md.
   - Valider les changements avec tests avant PR.

### Exemples a inclure

- Exemple de fichier `.env` minimal.
- Exemple de requete API et reponse issue de docs/api_specs.md.
- Exemple de commande de test et sortie attendue.

### References

- README.md (source de verite)
- docs/api_specs.md
- docs/data_models.md
- docs/agents/backend_agent.md
```
