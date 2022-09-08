from typing import Optional

from sqlalchemy import insert, select

from app.base.base_accessor import BaseAccessor
from app.quiz.models import (
    ThemeModel,
    QuestionModel,
    AnswerModel,
)


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> ThemeModel:
        query_insert = insert(ThemeModel).values(title=title)
        new_theme = ThemeModel(title=title)
        async with self.app.database.session() as session:
            #     await session.add(new_theme)
            #     await session.flush()
            #     await session.commit()
            # return Theme(id=new_theme.id, title=new_theme.title)
            new_theme = await session.execute(query_insert)
            id = new_theme.inserted_primary_key[0]
            query_select = select(ThemeModel).where(ThemeModel.id == id)
            response = await session.execute(query_select)
            await session.commit()
        res = response.scalar()
        if res:
            return ThemeModel(id=res.id, title=res.title)
        return None

    async def get_theme_by_title(self, title: str) -> Optional[ThemeModel]:
        query = select(ThemeModel).where(ThemeModel.title == title)
        async with self.app.database.session() as session:
            response = await session.execute(query)
        res = response.scalar()
        if res:
            return ThemeModel(id=res.id, title=res.title)
        return None

    async def get_theme_by_id(self, id_: int) -> Optional[ThemeModel]:
        query = select(ThemeModel).where(ThemeModel.id == id_)
        async with self.app.database.session() as session:
            response = await session.execute(query)
        res = response.scalar()
        if res:
            return ThemeModel(id=res.id, title=res.title)
        return None

    async def list_themes(self) -> list[ThemeModel]:
        query = select(ThemeModel)
        async with self.app.database.session() as session:
            response = await session.execute(query)
            return [
                ThemeModel(id=theme.id, title=theme.title)
                for theme in response.scalars().unique()
            ]

    async def create_answers(
        self, question_id: int, answers: list[AnswerModel]
    ) -> list[AnswerModel]:
        response_lst = []
        queries = [
            insert(AnswerModel).values(
                question_id=question_id,
                title=answer.title,
                is_correct=answer.is_correct,
            )
            for answer in answers
        ]

        async with self.app.database.session() as session:
            for query in queries:
                response = await session.execute(query)
                response_lst.append(response.scalar())
            await session.commit()
        return [
            AnswerModel(is_correct=answer.is_correct, title=answer.title)
            for answer in answers
        ]

    async def create_question(
        self, title: str, theme_id: int, answers: list[AnswerModel]
    ) -> QuestionModel:
        query_insert = insert(QuestionModel).values(title=title, theme_id=theme_id)
        async with self.app.database.session() as session:
            new_question = await session.execute(query_insert)
            id = new_question.inserted_primary_key[0]
            await session.commit()
        async with self.app.database.session() as session:
            await self.create_answers(id, answers)
            query_select = select(QuestionModel).where(QuestionModel.id == id)
            response = await session.execute(query_select)

        res = response.scalar()
        if res:
            return QuestionModel(
                id=res.id, title=res.title, theme_id=res.theme_id, answers=res.answers
            )
        return None

    async def get_question_by_title(self, title: str) -> Optional[QuestionModel]:
        query = select(QuestionModel).where(QuestionModel.title == title)
        async with self.app.database.session() as session:
            response = await session.execute(query)
        res = response.scalar()
        if res:
            return QuestionModel(
                id=res.id,
                title=res.title,
                theme_id=res.theme_id,
                answers=[
                    AnswerModel(title=answer.title, is_correct=answer.is_correct)
                    for answer in res.answers
                ],
            )
        return None

    async def list_questions(
        self, theme_id: Optional[int] = None
    ) -> list[QuestionModel]:
        query = select(QuestionModel)
        if theme_id is not None:
            query = query.where(QuestionModel.theme_id == theme_id)
        async with self.app.database.session() as session:
            response = await session.execute(query)
        return [
            QuestionModel(
                id=question.id,
                title=question.title,
                theme_id=question.theme_id,
                answers=[
                    AnswerModel(title=answer.title, is_correct=answer.is_correct)
                    for answer in question.answers
                ],
            )
            for question in response.scalars().unique()
        ]
