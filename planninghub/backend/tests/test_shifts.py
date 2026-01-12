from uuid import uuid4

from fastapi.testclient import TestClient


def test_create_shift_success(client: TestClient):
    tech_id = str(uuid4())
    equip_id = str(uuid4())
    shift_data = {
        "title": "Concert - Regie Son",
        "event_id": str(uuid4()),
        "call_time": "2024-02-15T16:00:00Z",
        "start_time": "2024-02-15T18:00:00Z",
        "end_time": "2024-02-15T23:00:00Z",
        "break_times": [
            {
                "start": "2024-02-15T20:30:00Z",
                "end": "2024-02-15T20:50:00Z",
                "mandatory": True,
            }
        ],
        "resources": [
            {
                "id": tech_id,
                "type": "technician",
                "role": "foh_engineer",
                "required_skills": ["foh_engineer"],
            },
            {"id": equip_id, "type": "equipment", "role": "mixing_console"},
        ],
        "economic_value": {
            "base_rate": 45,
            "total_amount": 1200,
            "budget_line": "sound",
            "breakdown": {"labor_cost": 405, "equipment_cost": 500},
        },
        "priority": "high",
        "metadata": {
            "technical_rider": "https://s3.example.com/rider.pdf",
            "stage_plot": "https://s3.example.com/plot.svg",
        },
    }

    response = client.post("/shifts/", json=shift_data)
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "planned"
    assert payload["version"] == 1


def test_create_shift_double_booking(client: TestClient):
    tech_id = str(uuid4())
    event_id = str(uuid4())
    base_payload = {
        "title": "Shift 1",
        "event_id": event_id,
        "call_time": "2024-02-15T16:00:00Z",
        "start_time": "2024-02-15T18:00:00Z",
        "end_time": "2024-02-15T23:00:00Z",
        "resources": [
            {"id": tech_id, "type": "technician", "role": "foh_engineer"}
        ],
        "economic_value": {
            "base_rate": 45,
            "total_amount": 800,
            "budget_line": "sound",
        },
        "priority": "high",
    }

    client.post("/shifts/", json=base_payload)

    conflicting = {
        **base_payload,
        "title": "Shift 2",
        "start_time": "2024-02-15T20:00:00Z",
        "end_time": "2024-02-16T01:00:00Z",
    }

    response = client.post("/shifts/", json=conflicting)
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "RESOURCE_CONFLICT"
