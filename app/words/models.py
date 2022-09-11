from dataclasses import dataclass, field
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import db, mapper_registry


@mapper_registry.mapped
@dataclass
class WordModel:
    __tablename__ = "words"
    __sa_dataclass_metadata_key__ = "sa"

    title: str = field(
        metadata={"sa": Column(String, nullable=False, unique=True)}
    )
    is_correct: bool = field(
        default=True, metadata={"sa": Column(Boolean, nullable=False)}
    )
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


# @mapper_registry.mapped
# @dataclass
# class PlayerGameModel:
#     __tablename__ = "players_games"
#     __sa_dataclass_metadata_key__ = "sa"
#
#     player_id: int = field(
#         init=False, metadata={"sa": Column(ForeignKey("players.id"), primary_key=True)}
#     )
#     game_id: int = field(
#         init=False, metadata={"sa": Column(ForeignKey("games.id"), primary_key=True)}
#     )


@mapper_registry.mapped
@dataclass
class PlayerModel:
    __tablename__ = "players"
    __sa_dataclass_metadata_key__ = "sa"

    status: str = field(
        metadata={"sa": Column(String, nullable=False)}
    )
    online: bool = field(
        metadata={"sa": Column(Boolean, nullable=False)}
    )
    user_id: int = field(
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


@mapper_registry.mapped
@dataclass
class GameModel:
    __tablename__ = "games"
    __sa_dataclass_metadata_key__ = "sa"

    status: str = field(
        metadata={"sa": Column(String, nullable=False)}
    )
    timeout: int = field(
        metadata={
            "sa": Column(
                Integer,
                nullable=False,
            )
        }
    )
    setting_id: int = field(
        init=False, metadata={"sa": Column(ForeignKey("settings.id"))}
    )
    players: List[PlayerModel] = field(
        default_factory=list, metadata={"sa": relationship("PlayerModel")}
    )
    id: Optional[int] = field(
        default=None, metadata={"sa": Column(Integer, primary_key=True)}
    )
