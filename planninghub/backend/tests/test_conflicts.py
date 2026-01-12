from uuid import uuid4

from fastapi.testclient import TestClient


def test_equipment_conflict_warning(client: TestClient):
    equip_id = str(uuid4())
    base_payload = {
        "title": "Shift 1",
        "event_id": str(uuid4()),
        "call_time": "2024-02-15T16:00:00Z",
        "start_time": "2024-02-15T18:00:00Z",
        "end_time": "2024-02-15T23:00:00Z",
        "resources": [
            {"id": equip_id, "type": "equipment", "role": "mixing_console"}
        ],
        "economic_value": {
            "base_rate": 45,
            "total_amount": 800,
            "budget_line": "sound",
        },
        "priority": "high",
    }

    client.post("/shifts/", json=base_payload)

    overlapping = {
        **base_payload,
        "title": "Shift 2",
        "start_time": "2024-02-15T20:00:00Z",
        "end_time": "2024-02-16T01:00:00Z",
    }

    response = client.post("/shifts/", json=overlapping)
    assert response.status_code == 201
    assert response.json()["warnings"][0]["code"] == "EQUIPMENT_UNAVAILABLE"
