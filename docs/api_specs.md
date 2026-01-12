# API Specifications - Phase 1 (Spectacle Vivant)

**Authority**: README.md (IAM, Time Engine, Conflict Engine, Financial Engine, Integration and Ecosystem)
**Base URL**: `https://api.planninghub-spectacle.fr/v1`
**Auth**: Auth0 JWT (alg: RS256, audience: `https://planninghub-spectacle.fr/api`)
**Rate Limiting**:
- 100 req/min pour les endpoints standards.
- 20 req/min pour les endpoints critiques (`/shifts`, `/equipment/availability`).

---
## Authentication (Auth0)
### 1. Login (avec metadonnees evenementielles)
```
POST /auth/login
```
**Request**:
```json
{
  "email": "jmichel@sonopro.fr",
  "password": "securePassword123!",
  "organization_id": "org_123",
  "event_id": "event_456"
}
```
**Response (200)**:
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": "user_456",
    "email": "jmichel@sonopro.fr",
    "roles": ["sound_engineer", "stage_manager"],
    "specializations": ["foh_engineer", "system_tech"],
    "current_event": {
      "id": "event_456",
      "name": "Festival Jazz a Juan 2024",
      "role": "head_sound_engineer"
    }
  }
}
```

---
## Users (Techniciens)
### 1. Get Current User (avec specialisations)
```
GET /users/me
Headers: Authorization: Bearer <token>
```
**Response (200)**:
```json
{
  "id": "user_456",
  "first_name": "Jean-Michel",
  "last_name": "Leroy",
  "email": "jmichel@sonopro.fr",
  "phone": "+336XXXXXXXX",
  "roles": ["sound_engineer", "stage_manager"],
  "specializations": [
    {
      "category": "sound",
      "skills": [
        {"name": "foh_engineer", "level": 5, "certifications": [{"name": "DiGiCo Certified", "expiry_date": "2025-12-31"}]},
        {"name": "system_tech", "level": 4}
      ]
    }
  ],
  "availability": {
    "2024-02-15": ["08:00-18:00", "20:00-02:00"],
    "2024-02-16": ["14:00-23:00"]
  },
  "employment_contract": {
    "type": "freelance",
    "hourly_rate": 45,
    "overtime_rules": {
      "night_shift_bonus": 1.5,
      "weekend_shift_bonus": 1.3,
      "emergency_call_bonus": 2.5
    },
    "meal_allowance": true
  },
  "current_events": [
    {
      "id": "event_456",
      "name": "Festival Jazz a Juan 2024",
      "role": "head_sound_engineer",
      "shifts": ["shift_789", "shift_101"]
    }
  ]
}
```

### 2. Update Availability (avec validation conflits)
```
PATCH /users/me/availability
Headers: Authorization: Bearer <token>
```
**Request**:
```json
{
  "2024-02-20": ["10:00-20:00"],
  "2024-02-21": ["14:00-03:00"],
  "2024-02-22": null
}
```
**Response (200)**:
```json
{
  "status": "success",
  "availability": {
    "2024-02-20": ["10:00-20:00"],
    "2024-02-21": ["14:00-03:00"],
    "2024-02-22": []
  },
  "warnings": [
    {
      "date": "2024-02-21",
      "message": "Ce creneau chevauche un shift existant (shift_101). Le conflit sera resolu par le regisseur.",
      "severity": "medium"
    }
  ]
}
```

---
## Equipment (Materiel Technique)
### 1. List Available Equipment (avec filtres)
```
GET /equipment?category=sound&subcategory=mixing_console&start_time=2024-02-15T00:00:00&end_time=2024-02-16T00:00:00
Headers: Authorization: Bearer <token>
```
**Response (200)**:
```json
{
  "count": 3,
  "results": [
    {
      "id": "eq_101",
      "name": "DiGiCo SD5",
      "category": "sound",
      "subcategory": "mixing_console",
      "availability": [
        {
          "start_time": "2024-02-15T08:00:00+01:00",
          "end_time": "2024-02-15T18:00:00+01:00",
          "status": "available"
        },
        {
          "start_time": "2024-02-15T20:00:00+01:00",
          "end_time": "2024-02-16T02:00:00+01:00",
          "status": "booked",
          "event_id": "event_456"
        }
      ],
      "specifications": {
        "inputs": 128,
        "outputs": 64,
        "compatibility": ["Dante", "MADI"]
      },
      "maintenance": {
        "last_maintenance_date": "2024-01-10",
        "next_maintenance_date": "2024-04-10"
      }
    }
  ]
}
```

### 2. Book Equipment (avec validation)
```
POST /equipment/book
Headers: Authorization: Bearer <token>
```
**Request**:
```json
{
  "equipment_id": "eq_101",
  "event_id": "event_456",
  "shift_id": "shift_789",
  "start_time": "2024-02-15T20:00:00+01:00",
  "end_time": "2024-02-16T02:00:00+01:00",
  "technician_id": "user_456"
}
```
**Response (201)**:
```json
{
  "booking_id": "booking_202",
  "equipment_id": "eq_101",
  "status": "confirmed",
  "conflicts": [],
  "warnings": [
    {
      "code": "MAINTENANCE_DUE",
      "message": "Cet equipement necessite une maintenance dans 45 jours (next_maintenance_date: 2024-04-10).",
      "severity": "low"
    }
  ]
}
```
**Erreurs**:
- `409 Conflict`: Equipement deja reserve.
- `422 Unprocessable Entity`:
  - `last_maintenance_date` > 3 mois.
  - Technicien non certifie pour cet equipement.

---
## Shifts (Plannings Techniques)
### 1. Create Shift (avec riders techniques)
```
POST /shifts
Headers: Authorization: Bearer <token>
```
**Request**:
```json
{
  "title": "Sonorisation - Scene Principale - Jazz a Juan",
  "event_id": "event_456",
  "start_time": "2024-02-15T20:00:00+01:00",
  "end_time": "2024-02-16T02:00:00+01:00",
  "call_time": "2024-02-15T18:00:00+01:00",
  "break_times": [
    {"start": "2024-02-15T22:30:00+01:00", "end": "2024-02-15T23:00:00+01:00", "mandatory": true}
  ],
  "resources": [
    {
      "id": "user_456",
      "type": "technician",
      "role": "foh_engineer",
      "required_skills": ["foh_engineer", "system_tech"]
    },
    {
      "id": "eq_101",
      "type": "equipment",
      "role": "mixing_console",
      "quantity": 1
    },
    {
      "id": "eq_102",
      "type": "equipment",
      "role": "stage_box",
      "quantity": 2
    }
  ],
  "economic_value": {
    "base_rate": 45,
    "equipment_rate": 500,
    "total_amount": 1200,
    "budget_line": "sound",
    "breakdown": {
      "labor_cost": 405,
      "equipment_cost": 500,
      "meal_allowance": 20,
      "transport_cost": 50,
      "overtime_cost": 225
    }
  },
  "priority": "high",
  "metadata": {
    "technical_rider": "https://s3.planninghub-spectacle.fr/riders/jazz-juan-2024-sound.pdf",
    "stage_plot": "https://s3.planninghub-spectacle.fr/plans/jazz-juan-2024-stage.svg",
    "cable_plan": "https://s3.planninghub-spectacle.fr/plans/jazz-juan-2024-cable.pdf"
  }
}
```
**Response (201)**:
```json
{
  "id": "shift_789",
  "status": "confirmed",
  "conflicts": [],
  "warnings": [
    {
      "code": "OVERLAP_WARNING",
      "message": "Le technicien user_456 a un autre shift a 16h-18h le meme jour (temps de repos respecte: 12h).",
      "severity": "low"
    }
  ],
  "economic_value": {
    "total_amount": 1200,
    "budget_line": "sound"
  },
  "created_at": "2024-01-20T10:00:00Z",
  "version": 1
}
```

### 2. Get Shift Details (avec fiches techniques)
```
GET /shifts/{shift_id}
Headers: Authorization: Bearer <token>
```
**Response (200)**:
```json
{
  "id": "shift_789",
  "title": "Sonorisation - Scene Principale - Jazz a Juan",
  "status": "confirmed",
  "start_time": "2024-02-15T20:00:00+01:00",
  "end_time": "2024-02-16T02:00:00+01:00",
  "resources": [
    {
      "id": "user_456",
      "type": "technician",
      "name": "Jean-Michel Leroy",
      "role": "foh_engineer",
      "skills": ["foh_engineer", "system_tech"],
      "status": "confirmed"
    },
    {
      "id": "eq_101",
      "type": "equipment",
      "name": "DiGiCo SD5",
      "category": "sound",
      "subcategory": "mixing_console",
      "status": "booked"
    }
  ],
  "economic_value": {
    "total_amount": 1200,
    "breakdown": {
      "labor_cost": 405,
      "equipment_cost": 500,
      "meal_allowance": 20,
      "transport_cost": 50,
      "overtime_cost": 225
    }
  },
  "metadata": {
    "technical_rider": "https://s3.../jazz-juan-2024-sound.pdf",
    "stage_plot": "https://s3.../jazz-juan-2024-stage.svg",
    "cable_plan": "https://s3.../jazz-juan-2024-cable.pdf",
    "checklist": [
      "Verifier les niveaux des retours avant le soundcheck",
      "Tester les backup lines pour la console",
      "Prevoir 2 cables XLR de rechange"
    ]
  },
  "conflicts": [],
  "qrcode": {
    "checkin_url": "https://app.planninghub-spectacle.fr/checkin?shift_id=shift_789&token=abc123",
    "checkout_url": "https://app.planninghub-spectacle.fr/checkout?shift_id=shift_789&token=abc123"
  }
}
```

---
## Events (Gestion des Evenements)
### 1. Create Event (avec riders techniques)
```
POST /events
Headers: Authorization: Bearer <token>
```
**Request**:
```json
{
  "name": "Festival Jazz a Juan 2024",
  "description": "25eme edition du festival de jazz en plein air.",
  "start_date": "2024-07-15",
  "end_date": "2024-07-22",
  "venue": {
    "name": "Pinede Gould",
    "address": "62 Bd de la Croisette, 06160 Antibes",
    "capacity": 3500,
    "technical_contact": {
      "name": "Pierre Durand",
      "email": "p.durand@jazzajuan.com",
      "phone": "+33493958585"
    }
  },
  "technical_requirements": {
    "sound": {
      "main_system": "L-Acoustics K2",
      "monitors": 8,
      "mixing_consoles": ["DiGiCo SD5 (FOH)", "DiGiCo SD10 (Monitors)"]
    },
    "lighting": {
      "moving_lights": 24,
      "led_pars": 48,
      "lighting_desks": ["MA3 Light"]
    },
    "power": {
      "total_power_needed": 200,
      "distros_required": 4
    }
  },
  "budget": {
    "total": 150000,
    "breakdown": {
      "sound": 50000,
      "lighting": 40000,
      "video": 20000,
      "labor": 30000,
      "transport": 10000
    }
  }
}
```
**Response (201)**:
```json
{
  "id": "event_456",
  "status": "planning",
  "technical_requirements": {
    "sound": {},
    "lighting": {}
  },
  "next_steps": [
    "Assigner un regisseur general",
    "Importer les riders techniques des artistes",
    "Planifier les repetitions techniques"
  ]
}
```

---
## Webhooks (Notifications en Temps Reel)
### 1. Shift Conflict Detected
```
POST [your-webhook-url]/shift-conflict
```
**Payload**:
```json
{
  "event": "shift.conflict.detected",
  "data": {
    "shift_id": "shift_789",
    "conflict_with": [
      {
        "shift_id": "shift_101",
        "resource_id": "user_456",
        "resource_type": "technician",
        "severity": "high",
        "overlap": "2024-02-15T22:00:00+01:00 - 2024-02-15T23:00:00+01:00"
      }
    ],
    "suggested_actions": [
      {
        "action": "reschedule_shift_789",
        "new_start_time": "2024-02-15T23:00:00+01:00"
      },
      {
        "action": "assign_alternative_technician",
        "technician_id": "user_789",
        "skills_match": 0.95
      }
    ]
  },
  "timestamp": "2024-01-20T10:00:00Z"
}
```

### 2. Equipment Maintenance Due
```
POST [your-webhook-url]/equipment-maintenance
```
**Payload**:
```json
{
  "event": "equipment.maintenance.due",
  "data": {
    "equipment_id": "eq_101",
    "name": "DiGiCo SD5",
    "last_maintenance_date": "2024-01-10",
    "next_maintenance_date": "2024-04-10",
    "days_until_due": 45,
    "booked_shifts": [
      {
        "shift_id": "shift_789",
        "event_id": "event_456",
        "start_time": "2024-02-15T20:00:00+01:00"
      }
    ]
  },
  "timestamp": "2024-01-20T10:00:00Z"
}
```

---
## Regles d'API specifiques
1. **Rate Limiting**:
   - **Endpoints critiques** (`/shifts`, `/equipment/book`): 20 req/min.
   - **Webhooks**: 1000 req/jour.

2. **Validation**:
   - Toutes les dates doivent etre en UTC (affichage Europe/Paris cote client).
   - Les `time-range` doivent etre au format `HH:MM-HH:MM`.

3. **Erreurs specifiques**:
   | Code | Erreur | Description |
   | --- | --- | --- |
   | 400 | `INVALID_TIME_RANGE` | `end_time` <= `start_time` ou format invalide. |
   | 409 | `RESOURCE_CONFLICT` | Conflit de ressource (technicien ou equipement). |
   | 422 | `LABOR_LAW_VIOLATION` | Violation des conventions collectives (ex: temps de repos insuffisant). |
   | 422 | `MAINTENANCE_OVERDUE` | Equipement necessite une maintenance. |
   | 422 | `SKILL_MISMATCH` | Technicien non qualifie pour l'equipement ou le role. |
   | 429 | `RATE_LIMIT_EXCEEDED` | Trop de requetes. |

4. **Headers obligatoires**:
   - `X-Organization-ID`: ID de l'organisation (multi-tenancy).
   - `X-Event-ID`: ID de l'evenement (si contexte evenementiel).

---
## Prochaines etapes pour Codex
1. **Backend**:
   - [ ] Implementer les modeles `User`, `Equipment`, `Shift`, `Event` (SQLAlchemy).
   - [ ] Coder les endpoints `/shifts` et `/equipment` (FastAPI).
   - [ ] Integrer Auth0 pour l'authentification.
   - [ ] Configurer les webhooks (via AWS SNS ou directement en FastAPI).

2. **Mobile (React Native)**:
   - [ ] Ecran de liste des shifts avec filtres (par evenement, date, role).
   - [ ] Affichage des fiches techniques (PDF/SVG) en offline.
   - [ ] Module de check-in/check-out via QR code.

3. **Tests**:
   - [ ] Ecrire des tests pour les regles de conflit (ex: chevauchement de shifts).
   - [ ] Valider les calculs de couts (bonus nuit, repas, transport).

4. **Deploiement**:
   - [ ] Configurer un environnement de staging sur AWS (ECS + RDS).
   - [ ] Mettre en place le monitoring (Prometheus + Grafana).

---
### Exemple de code pour demarrer (FastAPI)
```python
# models.py
from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List, Literal

class Skill(BaseModel):
    name: Literal[
        "foh_engineer", "monitor_engineer", "system_tech", "moving_lights",
        "led_programmer", "video_mapping", "truss_rigger", "pyro_operator"
    ]
    level: int  # 1-5
    certifications: Optional[List[dict]] = None

class UserBase(BaseModel):
    email: str
    phone: str
    roles: List[Literal["technician", "sound_engineer", "lighting_engineer", "stage_manager"]]

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    specializations: List[Skill]
    availability: dict  # {"2024-02-15": ["20:00-02:00"]}

    @validator("availability")
    def validate_time_ranges(cls, v):
        for date, ranges in v.items():
            for time_range in ranges:
                if not re.match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]-([01]?[0-9]|2[0-3]):[0-5][0-9]$", time_range):
                    raise ValueError(f"Invalid time range: {time_range}")
        return v

# main.py (FastAPI)
from fastapi import FastAPI, Depends, HTTPException
from .models import UserCreate, User

app = FastAPI()

@app.post("/users", response_model=User)
def create_user(user: UserCreate):
    db_user = User(**user.dict())
    return db_user

@app.get("/users/me", response_model=User)
def get_current_user(current_user: User = Depends(get_current_user)):
    return current_user
```

---
## Resume des actions pour vous
1. **Valider les modeles** avec les experts spectacle (ex: Jean-Michel Leroy).
2. **Prioriser les endpoints** a implementer en premier:
   - `/shifts` (coeur du MVP).
   - `/equipment/availability` (pour eviter les conflits materiel).
   - `/users/me` (pour l'app mobile).
3. **Donner ces docs a Codex** avec la directive:
   > "Implemente le backend FastAPI en utilisant les modeles et endpoints definis dans `api_specs.md` et `data_models.md`. Commence par les endpoints `/shifts` et `/equipment`, puis ajoute l'auth Auth0. Escalade toute ambiguite via `AGENT.md`."

---
## Prochaines etapes cles
1. **Atelier UX** avec 3 techniciens son/lumiere pour valider:
   - L'affichage des fiches de poste sur mobile.
   - Le workflow de check-in/check-out.
2. **Integration avec un outil existant** (ex: Vectorworks pour les plans de scene).
3. **Test en conditions reelles** sur un petit evenement (ex: concert de 200 personnes).

---
## Annexes utiles
1. **Exemple de Rider Technique** (a parser):
   Lien vers un exemple reel: https://www.yamahaproaudio.com/global/en/support/downloads/
2. **Convention Collective Spectacle**:
   Texte officiel: https://www.legifrance.gouv.fr/
3. **Normes Securite ERP**:
   Guide pratique: https://www.service-public.fr/
