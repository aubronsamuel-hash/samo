from functools import lru_cache
from typing import Any, Dict

import httpx
from jose import jwt
from jose.exceptions import JWTError

from ..config import settings


@lru_cache(maxsize=1)
def fetch_jwks() -> Dict[str, Any]:
    if not settings.auth0_domain:
        raise ValueError("AUTH0_DOMAIN non configure")
    url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
    response = httpx.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def decode_token(token: str) -> Dict[str, Any]:
    if not settings.auth0_domain or not settings.auth0_api_audience:
        raise ValueError("Auth0 configuration incomplete")
    jwks = fetch_jwks()
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")
    key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if not key:
        raise ValueError("Signing key not found")
    try:
        return jwt.decode(
            token,
            key,
            algorithms=[settings.auth0_algorithms],
            audience=settings.auth0_api_audience,
            issuer=f"https://{settings.auth0_domain}/",
        )
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
