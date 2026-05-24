import secrets
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.core.security import get_password_hash
from app.models.api_key import (
    ApiKey,
    ApiKeyCreate,
    ApiKeyCreated,
    ApiKeyPublic,
    ApiKeysPublic,
)
from app.models import Message

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


def _generate_api_key() -> tuple[str, str, str]:
    raw = f"ak_{secrets.token_urlsafe(32)}"
    hashed = get_password_hash(raw)
    prefix = raw[:10]
    return raw, hashed, prefix


@router.post("/", response_model=ApiKeyCreated)
def create_api_key(
    *, session: SessionDep, current_user: CurrentUser, body: ApiKeyCreate
) -> Any:
    raw, hashed, prefix = _generate_api_key()
    api_key = ApiKey(
        name=body.name,
        key_hash=hashed,
        key_prefix=prefix,
        rate_limit=body.rate_limit,
        user_id=current_user.id,
    )
    session.add(api_key)
    session.commit()
    session.refresh(api_key)

    result = ApiKeyCreated.model_validate(api_key)
    result.raw_key = raw
    return result


@router.get("/", response_model=ApiKeysPublic)
def list_api_keys(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 20
) -> Any:
    keys = session.query(ApiKey).where(ApiKey.user_id == current_user.id)
    count = keys.count()
    items = keys.offset(skip).limit(limit).all()
    return ApiKeysPublic(data=items, count=count)


@router.delete("/{key_id}", response_model=Message)
def revoke_api_key(
    key_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    api_key = session.get(ApiKey, key_id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    if api_key.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    api_key.is_active = False
    session.add(api_key)
    session.commit()
    return Message(message="API key revoked")
