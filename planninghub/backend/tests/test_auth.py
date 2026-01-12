import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.auth import dependencies


def test_get_current_user_valid_token(mocker):
    mocker.patch(
        "app.auth.dependencies.decode_token",
        return_value={"sub": "user-123", "role": "planner"},
    )
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
    payload = dependencies.get_current_user(credentials)
    assert payload["user_id"] == "user-123"
    assert payload["role"] == "planner"


def test_get_current_user_invalid_token(mocker):
    mocker.patch(
        "app.auth.dependencies.decode_token",
        side_effect=ValueError("Invalid token"),
    )
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
    with pytest.raises(HTTPException) as excinfo:
        dependencies.get_current_user(credentials)
    assert excinfo.value.status_code == 401


def test_require_role_allows_access():
    checker = dependencies.require_role("planner")
    payload = {"role": ["planner"]}
    assert checker(current_user=payload) == payload


def test_require_role_denies_access():
    checker = dependencies.require_role("planner")
    payload = {"role": "viewer"}
    with pytest.raises(HTTPException) as excinfo:
        checker(current_user=payload)
    assert excinfo.value.status_code == 403
