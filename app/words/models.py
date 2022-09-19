from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint
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
class CityModel:
    __tablename__ = "cities"
    __sa_dataclass_metadata_key__ = "sa"

    id_region: Optional[int] = field(metadata={"sa": Column(Integer)})
    id_country: Optional[int] = field(metadata={"sa": Column(Integer)})
    title: str = field(metadata={"sa": Column(String, nullable=False)})
    id: Optional[int] = field(default=None, metadata={"sa": Column(Integer, primary_key=True)})


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
    score: int = field(metadata={"sa": Column(Integer, default=0)})
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
    current_move: Optional[int] = field(
        metadata={
            "sa": Column(
                Integer,
                nullable=True,
            )
        }
    )
    event_timestamp: Optional[datetime] = field(
        metadata={
            "sa": Column(
                DateTime(timezone=True),
                nullable=True,
            )
        }
    )
    elapsed_time: Optional[int] = field(metadata={"sa": Column(Integer, default=0, nullable=False)})
    status: str = field(metadata={"sa": Column(String, default="init")})
    last_word: Optional[str] = field(
        metadata={
            "sa": Column(
                String,
                nullable=True,
            )
        }
    )
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
    vote_word: Optional[str] = field(
        metadata={
            "sa": Column(
                String,
                nullable=True,
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


@mapper_registry.mapped
@dataclass
class UsedWordModel:
    __tablename__ = "usedwords"
    __sa_dataclass_metadata_key__ = "sa"

    title: str = field(metadata={"sa": Column(String, nullable=False)})
    game_id: int = field(metadata={"sa": Column(ForeignKey("games.id", ondelete="CASCADE"))})
    id: Optional[int] = field(default=None, metadata={"sa": Column(Integer, primary_key=True)})


@mapper_registry.mapped
@dataclass
class VoteModel:
    __tablename__ = "votes"
    __sa_dataclass_metadata_key__ = "sa"

    title: str = field(metadata={"sa": Column(String, nullable=False)})
    player_id: int = field(metadata={"sa": Column(ForeignKey("players.id", ondelete="CASCADE"))})
    game_id: int = field(metadata={"sa": Column(ForeignKey("games.id", ondelete="CASCADE"))})
    is_correct: bool = field(default=True, metadata={"sa": Column(Boolean, nullable=False)})
    id: Optional[int] = field(default=None, metadata={"sa": Column(Integer, primary_key=True)})

    __table_args__ = (UniqueConstraint("player_id", "title", name="_vote_word_uc"),)
