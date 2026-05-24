import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class ApiKeyBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    rate_limit: int = Field(default=100, ge=1, description="Requests per minute")


class ApiKeyCreate(ApiKeyBase):
    pass


class ApiKeyPublic(ApiKeyBase):
    id: uuid.UUID
    key_prefix: str
    is_active: bool
    created_at: datetime | None
    last_used_at: datetime | None


class ApiKeyCreated(ApiKeyPublic):
    raw_key: str


class ApiKeysPublic(SQLModel):
    data: list[ApiKeyPublic]
    count: int


class ApiKey(ApiKeyBase, table=True):
    __tablename__ = "api_key"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    key_hash: str = Field(unique=True, index=True)
    key_prefix: str = Field(max_length=8)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    is_active: bool = Field(default=True)
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
    last_used_at: datetime | None = Field(default=None)
