from fastapi.testclient import TestClient

from app.models import Equipment, Event, User


def test_create_shift_success(
    client: TestClient, test_event: Event, test_technician: User, test_equipment: Equipment
):
    shift_data = {
        "title": "Concert - Regie Son",
        "event_id": str(test_event.id),
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
                "id": str(test_technician.id),
                "type": "technician",
                "role": "foh_engineer",
                "required_skills": ["foh_engineer"],
            },
            {"id": str(test_equipment.id), "type": "equipment", "role": "mixing_console"},
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
    assert payload["status"] == "confirmed"
    assert payload["version"] == 1


def test_create_shift_double_booking(
    client: TestClient, test_event: Event, test_technician: User
):
    base_payload = {
        "title": "Shift 1",
        "event_id": str(test_event.id),
        "call_time": "2024-02-15T16:00:00Z",
        "start_time": "2024-02-15T18:00:00Z",
        "end_time": "2024-02-15T23:00:00Z",
        "resources": [
            {"id": str(test_technician.id), "type": "technician", "role": "foh_engineer"}
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


def test_create_shift_date_bounds_error(
    client: TestClient, test_event: Event, test_technician: User
):
    shift_data = {
        "title": "Shift Hors Event",
        "event_id": str(test_event.id),
        "call_time": "2024-02-14T16:00:00Z",
        "start_time": "2024-02-14T18:00:00Z",
        "end_time": "2024-02-14T23:00:00Z",
        "resources": [
            {"id": str(test_technician.id), "type": "technician", "role": "foh_engineer"}
        ],
        "economic_value": {
            "base_rate": 45,
            "total_amount": 800,
            "budget_line": "sound",
        },
        "priority": "high",
    }

    response = client.post("/shifts/", json=shift_data)
    assert response.status_code == 422
    assert response.json()["detail"] == "Shift dates must be within event dates"


def test_create_shift_conflict_soft(
    client: TestClient, test_event: Event, test_technician: User
):
    base_payload = {
        "title": "Shift Matin",
        "event_id": str(test_event.id),
        "call_time": "2024-02-15T06:00:00Z",
        "start_time": "2024-02-15T08:00:00Z",
        "end_time": "2024-02-15T12:00:00Z",
        "resources": [
            {"id": str(test_technician.id), "type": "technician", "role": "foh_engineer"}
        ],
        "economic_value": {
            "base_rate": 45,
            "total_amount": 800,
            "budget_line": "sound",
        },
        "priority": "high",
    }

    response = client.post("/shifts/", json=base_payload)
    assert response.status_code == 201

    second_payload = {
        **base_payload,
        "title": "Shift Soir",
        "call_time": "2024-02-15T16:00:00Z",
        "start_time": "2024-02-15T18:00:00Z",
        "end_time": "2024-02-15T22:00:00Z",
    }

    response = client.post("/shifts/", json=second_payload)
    assert response.status_code == 201
    warnings = response.json()["warnings"]
    assert any(warning["code"] == "REST_TIME_WARNING" for warning in warnings)
