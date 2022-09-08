from aiohttp.web_exceptions import HTTPConflict, HTTPNotFound
from aiohttp_apispec import querystring_schema, request_schema, response_schema, docs

from app.quiz.models import AnswerModel
from app.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    ThemeIdSchema,
    ThemeListSchema,
    ThemeSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="add theme", description="Add new theme")
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema)
    async def post(self):
        title = self.data["title"]
        if await self.store.quizzes.get_theme_by_title(title):
            raise HTTPConflict
        theme = await self.store.quizzes.create_theme(title=title)
        user_out = ThemeSchema().dump(theme)
        return json_response(data=user_out)


class ThemeListView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="get themes", description="return list of themes")
    @response_schema(ThemeListSchema)
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        return json_response(data=ThemeListSchema().dump({"themes": themes}))


class QuestionAddView(AuthRequiredMixin, View):
    @docs(tags=["quiz"], summary="add question", description="Add new question")
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        title = self.data["title"]
        theme_id = self.data["theme_id"]
        answers = [
            AnswerModel(title=answer["title"], is_correct=answer["is_correct"])
            for answer in self.data["answers"]
        ]
        if await self.store.quizzes.get_question_by_title(title):
            raise HTTPConflict
        if not await self.store.quizzes.get_theme_by_id(theme_id):
            raise HTTPNotFound
        question = await self.store.quizzes.create_question(
            title=title, theme_id=theme_id, answers=answers
        )
        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @docs(
        tags=["quiz"], summary="get questions", description="return list of questions"
    )
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        theme_id = self.request.query.get("theme_id", None)
        questions = await self.store.quizzes.list_questions(theme_id)
        return json_response(data=ListQuestionSchema().dump({"questions": questions}))
