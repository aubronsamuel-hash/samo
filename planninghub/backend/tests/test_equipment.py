from fastapi.testclient import TestClient


def test_list_equipment_empty(client: TestClient):
    response = client.get("/equipment/")
    assert response.status_code == 200
    assert response.json()["count"] == 0
