from fastapi.testclient import TestClient

from app.models import Equipment, EquipmentStatus, Event, User


def test_conflict_engine_double_booking(
    client: TestClient, test_event: Event, test_technician: User
):
    base_payload = {
        "title": "Shift A",
        "event_id": str(test_event.id),
        "call_time": "2024-02-15T09:00:00Z",
        "start_time": "2024-02-15T10:00:00Z",
        "end_time": "2024-02-15T14:00:00Z",
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

    overlap_payload = {
        **base_payload,
        "title": "Shift B",
        "start_time": "2024-02-15T12:00:00Z",
        "end_time": "2024-02-15T18:00:00Z",
    }

    response = client.post("/shifts/", json=overlap_payload)
    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "RESOURCE_CONFLICT"
    assert any(conflict["resource_type"] == "technician" for conflict in detail["conflicts"])


def test_conflict_engine_equipment_maintenance(
    client: TestClient,
    db_session,
    test_event: Event,
    test_manager: User,
):
    equipment = Equipment(
        name="Console en Maintenance",
        category="audio",
        subcategory="mixing_console",
        status=EquipmentStatus.MAINTENANCE,
        quantity=1,
        organization_id=test_manager.organization_id,
    )
    db_session.add(equipment)
    db_session.commit()
    db_session.refresh(equipment)

    payload = {
        "title": "Shift Maintenance",
        "event_id": str(test_event.id),
        "call_time": "2024-02-15T16:00:00Z",
        "start_time": "2024-02-15T18:00:00Z",
        "end_time": "2024-02-15T23:00:00Z",
        "resources": [
            {"id": str(equipment.id), "type": "equipment", "role": "mixing_console"}
        ],
        "economic_value": {
            "base_rate": 45,
            "total_amount": 800,
            "budget_line": "sound",
        },
        "priority": "high",
    }

    response = client.post("/shifts/", json=payload)
    assert response.status_code in {409, 422}
