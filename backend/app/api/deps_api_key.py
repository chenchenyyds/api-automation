from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import ValidationError
from sqlmodel import Session

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import verify_password
from app.models import User
from app.models.api_key import ApiKey

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_db_session() -> Session:
    with next(get_db()) as session:
        return session


async def get_api_key_user(
    api_key: Annotated[str | None, Security(api_key_header)],
    session: Annotated[Session, Depends(get_db)],
) -> User:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header is required",
        )

    from sqlmodel import select

    statement = select(ApiKey).where(ApiKey.is_active == True)
    keys = session.exec(statement).all()

    for key in keys:
        verified, _ = verify_password(api_key, key.key_hash)
        if verified:
            from datetime import datetime, timezone

            key.last_used_at = datetime.now(timezone.utc)
            session.add(key)
            session.commit()

            user = session.get(User, key.user_id)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or inactive API key",
                )
            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
    )
