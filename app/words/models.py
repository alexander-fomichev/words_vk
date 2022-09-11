from dataclasses import dataclass, field
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Boolean

from app.store.database.sqlalchemy_base import db, mapper_registry


@mapper_registry.mapped
@dataclass
class WordModel:
    __tablename__ = "words"
    __sa_dataclass_metadata_key__ = "sa"

    title: str = field(
        metadata={"sa": Column(String, nullable=False, unique=True)}
    )
    is_correct: bool = field(default=True, metadata={"sa": Column(Boolean, nullable=False)})
    id: Optional[int] = field(
        default=None, metadata={"sa": Column(Integer, primary_key=True)}
    )


@mapper_registry.mapped
@dataclass
class SettingModel:
    __tablename__ = "settings"
    __sa_dataclass_metadata_key__ = "sa"

    title: str = field(
        metadata={"sa": Column(String, nullable=False, unique=True)}
    )
    timeout: int = field(
        metadata={
            "sa": Column(
                Integer,
                nullable=False,
            )
        }
    )
    id: Optional[int] = field(
        default=None, metadata={"sa": Column(Integer, primary_key=True)}
    )
