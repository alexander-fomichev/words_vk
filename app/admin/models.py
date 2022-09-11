import uuid
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Optional

from aiohttp_session import Session
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.store.database.sqlalchemy_base import mapper_registry


@mapper_registry.mapped
@dataclass
class AdminModel:
    __tablename__ = "admins"
    __sa_dataclass_metadata_key__ = "sa"


    email: str = field(
        metadata={"sa": Column(String, nullable=False, unique=True)}
    )
    id: Optional[uuid.UUID] = field(
        default=None, metadata={"sa": Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)}
    )
    password: str = field(
        default=None, metadata={"sa": Column(String, nullable=False)}
    )

    def is_password_valid(self, password: str):
        return self.password == str(sha256(password.encode()).hexdigest())

    @classmethod
    def from_session(cls, session: Optional[Session]) -> Optional["AdminModel"]:
        return cls(id=session["admin"]["id"], email=session["admin"]["email"])
