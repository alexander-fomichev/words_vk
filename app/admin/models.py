from dataclasses import dataclass, field
from hashlib import sha256
from typing import Optional, List

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import db, mapper_registry


# @dataclass
# class Admin:
#     id: int
#     email: str
#     password: Optional[str] = None
#
#     def is_password_valid(self, password: str):
#         return self.password == sha256(password.encode()).hexdigest()
#
#     @classmethod
#     def from_session(cls, session: Optional[dict]) -> Optional["Admin"]:
#         return cls(id=session["admin"]["id"], email=session["admin"]["email"])
#
#
# @dataclass
# class AdminModel(db):
#     __tablename__ = "admins"
#     id = Column(Integer, primary_key=True)
#     email = Column(String, nullable=False, unique=True)
#     password = Column(String, nullable=False)


@mapper_registry.mapped
@dataclass
class AdminModel:
    __tablename__ = "admins"
    __sa_dataclass_metadata_key__ = "sa"

    email: str = field(metadata={"sa": Column(String, nullable=False, unique=True)})
    id: Optional[int] = field(
        default=None, metadata={"sa": Column(Integer, primary_key=True)}
    )
    password: str = field(default=None, metadata={"sa": Column(String, nullable=False)})

    def is_password_valid(self, password: str):
        return self.password == sha256(password.encode()).hexdigest()

    @classmethod
    def from_session(cls, session: Optional[dict]) -> Optional["AdminModel"]:
        return cls(id=session["admin"]["id"], email=session["admin"]["email"])
