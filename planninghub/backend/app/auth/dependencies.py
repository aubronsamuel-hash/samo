from typing import Any, Dict, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .auth0 import decode_token

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from exc
    return _normalize_claims(payload)


def _normalize_claims(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id = payload.get("user_id") or payload.get("sub") or payload.get("id")
    organization_id = payload.get("organization_id") or payload.get("org_id")
    role = payload.get("role") or payload.get("roles") or payload.get("permissions")
    return {
        **payload,
        "user_id": user_id,
        "organization_id": organization_id,
        "role": role,
    }


def require_role(required_role: str):
    def _checker(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        roles: List[str] = []
        current_role = current_user.get("role")
        if isinstance(current_role, str):
            roles = [current_role]
        elif isinstance(current_role, list):
            roles = current_role
        if required_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )
        return current_user

    return _checker
