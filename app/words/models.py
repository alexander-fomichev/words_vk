from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import mapper_registry, db


@mapper_registry.mapped
@dataclass
class WordModel:
    __tablename__ = "words"
    __sa_dataclass_metadata_key__ = "sa"

    title: str = field(metadata={"sa": Column(String, nullable=False, unique=True)})
    is_correct: bool = field(default=True, metadata={"sa": Column(Boolean, nullable=False)})
    id: Optional[int] = field(default=None, metadata={"sa": Column(Integer, primary_key=True)})

    # __table_args__ = (CheckConstraint("regexp_like(title, '^[а-яА-ЯёЁ]+$')", name='title_cyr'),)


@mapper_registry.mapped
@dataclass
class SettingModel:
    __tablename__ = "settings"
    __sa_dataclass_metadata_key__ = "sa"

    title: str = field(metadata={"sa": Column(String, nullable=False, unique=True)})
    timeout: int = field(
        metadata={
            "sa": Column(
                Integer,
                nullable=False,
            )
        }
    )
    id: Optional[int] = field(default=None, metadata={"sa": Column(Integer, primary_key=True)})


@mapper_registry.mapped
@dataclass
class PlayerModel:
    __tablename__ = "players"
    __sa_dataclass_metadata_key__ = "sa"

    name: str = field(metadata={"sa": Column(String, nullable=False)})
    status: str = field(metadata={"sa": Column(String, nullable=False)})
    online: bool = field(metadata={"sa": Column(Boolean, nullable=False)})
    user_id: int = field(
        metadata={
            "sa": Column(
                Integer,
                nullable=False,
            )
        }
    )
    game_id: int = field(metadata={"sa": Column(ForeignKey("games.id", ondelete="CASCADE"))})
    id: Optional[int] = field(default=None, metadata={"sa": Column(Integer, primary_key=True)})
    __table_args__ = (UniqueConstraint("user_id", "game_id", name="_user_game_uc"),)


@mapper_registry.mapped
@dataclass
class GameModel:
    __tablename__ = "games"
    __sa_dataclass_metadata_key__ = "sa"

    moves_order: Optional[str] = field(
        metadata={
            "sa": Column(
                String,
                nullable=True,
            )
        }
    )
    current_move: Optional[int] = field(metadata={"sa": Column(Integer, default=0)})
    event_timestamp: Optional[datetime] = field(
        metadata={
            "sa": Column(
                DateTime(timezone=True),
                nullable=True,
            )
        }
    )
    pause_timestamp: Optional[datetime] = field(
        metadata={
            "sa": Column(
                DateTime(timezone=True),
                nullable=True,
            )
        }
    )
    status: str = field(metadata={"sa": Column(String, default="Init")})
    setting_id: int = field(metadata={"sa": Column(ForeignKey("settings.id", ondelete="CASCADE"))})
    setting: Optional[SettingModel] = field(metadata={"sa": relationship("SettingModel")}, init=False)

    peer_id: int = field(
        metadata={
            "sa": Column(
                Integer,
                nullable=False,
            )
        }
    )
    players: List[PlayerModel] = field(
        default_factory=list,
        metadata={
            "sa": relationship(
                "PlayerModel",
                cascade="all, delete-orphan",
                passive_deletes=True,
            )
        },
    )
    id: Optional[int] = field(default=None, metadata={"sa": Column(Integer, primary_key=True)})
