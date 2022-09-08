from dataclasses import dataclass, field
from typing import Optional, List

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import db, mapper_registry


@mapper_registry.mapped
@dataclass
class AnswerModel:
    __tablename__ = "answers"
    __sa_dataclass_metadata_key__ = "sa"

    title: str = field(metadata={"sa": Column(String, nullable=False, unique=True)})
    is_correct: bool = field(metadata={"sa": Column(Boolean, nullable=False)})
    question_id: Optional[int] = field(
        default=None,
        metadata={
            "sa": Column(
                Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
            )
        },
    )
    id: Optional[int] = field(
        default=None, metadata={"sa": Column(Integer, primary_key=True)}
    )


@mapper_registry.mapped
@dataclass
class QuestionModel:
    __tablename__ = "questions"
    __sa_dataclass_metadata_key__ = "sa"

    title: str = field(metadata={"sa": Column(String, nullable=False, unique=True)})
    theme_id: int = field(
        metadata={
            "sa": Column(
                Integer, ForeignKey("themes.id", ondelete="CASCADE"), nullable=False
            )
        }
    )
    id: Optional[int] = field(
        default=None, metadata={"sa": Column(Integer, primary_key=True)}
    )
    answers: List[AnswerModel] = field(
        default_factory=list,
        metadata={
            "sa": relationship(
                "AnswerModel",
                cascade="all, delete-orphan",
                passive_deletes=True,
                lazy="subquery",
            )
        },
    )


@mapper_registry.mapped
@dataclass
class ThemeModel:
    __tablename__ = "themes"
    __sa_dataclass_metadata_key__ = "sa"

    # id = Column(Integer, primary_key=True)
    # title = Column(String, nullable=False, unique=True)

    title: str = field(metadata={"sa": Column(String, nullable=False, unique=True)})
    id: Optional[int] = field(
        default=None, metadata={"sa": Column(Integer, primary_key=True)}
    )
    questions: Optional[List[QuestionModel]] = field(
        default_factory=list,
        metadata={
            "sa": relationship(
                "QuestionModel",
                cascade="all, delete-orphan",
                passive_deletes=True,
                lazy="subquery",
            )
        },
    )
