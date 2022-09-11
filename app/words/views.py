from aiohttp.web_exceptions import HTTPConflict, HTTPNotFound
from aiohttp_apispec import (
    querystring_schema,
    request_schema,
    response_schema,
    docs,
)
from sqlalchemy.exc import IntegrityError

from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response
from app.words.schemes import (
    WordSchema,
    WordListSchema,
    SettingSchema,
    WordIsCorrectSchema,
    SettingListSchema,
    SettingTitleSchema,
    PatchSettingSchema,
    PatchWordSchema,
    WordIdSchema,
    WordTitleSchema,
    SettingIdSchema,
)


class WordGetView(AuthRequiredMixin, View):
    @docs(
        tags=["words"], summary="get word", description="return word by title"
    )
    @querystring_schema(WordTitleSchema)
    @response_schema(WordSchema)
    async def get(self):
        title = self.request["querystring"]["title"].lower()
        word = await self.store.words.get_word_by_title(title)
        if word is None:
            raise HTTPNotFound
        return json_response(data=WordSchema().dump(word))


class WordAddView(AuthRequiredMixin, View):
    @docs(
        tags=["words"],
        summary="add word",
        description="Add new word to dictionary",
    )
    @request_schema(WordSchema)
    @response_schema(WordSchema)
    async def post(self):
        title = self.data["title"].lower()
        is_correct = self.data["is_correct"]
        try:
            word = await self.store.words.create_word(title, is_correct)
        except IntegrityError as e:
            if e.orig.pgcode == "23505":
                raise HTTPConflict
        word_out = WordSchema().dump(word)
        return json_response(data=word_out)


class WordPatchView(AuthRequiredMixin, View):
    @docs(
        tags=["words"], summary="patch word", description="Patch existed word"
    )
    @request_schema(PatchWordSchema)
    @response_schema(WordSchema)
    async def post(self):
        id = self.data["id"]
        title = self.data.get("title", None)
        if title:
            title = title.lower()
        is_correct = self.data.get("is_correct", None)
        word = await self.store.words.patch_word(
            id, title=title, is_correct=is_correct
        )
        if word is None:
            raise HTTPNotFound
        word_out = WordSchema().dump(word)
        return json_response(data=word_out)


class WordDeleteView(AuthRequiredMixin, View):
    @docs(
        tags=["words"], summary="delete word", description="Delete existed word"
    )
    @request_schema(WordIdSchema)
    @response_schema(WordSchema)
    async def post(self):
        id = self.data["id"]
        word = await self.store.words.get_word_by_id(id)
        if word is None:
            raise HTTPNotFound
        await self.store.words.delete_word(id)
        word_out = WordSchema().dump(word)
        return json_response(data=word_out)


class WordListView(AuthRequiredMixin, View):
    @docs(
        tags=["words"], summary="get words", description="return list of words"
    )
    @querystring_schema(WordIsCorrectSchema)
    @response_schema(WordListSchema)
    async def get(self):
        is_correct = self.request["querystring"].get("is_correct", None)
        words = await self.store.words.list_words(is_correct)
        return json_response(data=WordListSchema().dump({"words": words}))


class SettingGetView(AuthRequiredMixin, View):
    @docs(
        tags=["settings"],
        summary="get setting",
        description="return setting by title",
    )
    @querystring_schema(SettingTitleSchema)
    @response_schema(SettingSchema)
    async def get(self):
        title = self.request["querystring"]["title"].lower()
        setting = await self.store.words.get_setting_by_title(title)
        if setting is None:
            raise HTTPNotFound
        return json_response(data=SettingSchema().dump(setting))


class SettingAddView(AuthRequiredMixin, View):
    @docs(
        tags=["settings"], summary="add setting", description="Add new setting"
    )
    @request_schema(SettingSchema)
    @response_schema(SettingSchema)
    async def post(self):
        title = self.data["title"].lower()
        timeout = self.data["timeout"]
        try:
            setting = await self.store.words.create_setting(title, timeout)
        except IntegrityError as e:
            if e.orig.pgcode == "23505":
                raise HTTPConflict
        setting_out = SettingSchema().dump(setting)
        return json_response(data=setting_out)


class SettingPatchView(AuthRequiredMixin, View):
    @docs(
        tags=["settings"],
        summary="patch setting",
        description="partial update setting by title",
    )
    @request_schema(PatchSettingSchema)
    @response_schema(SettingSchema)
    async def post(self):
        id = self.data["id"]
        title = self.data.get("title", None)
        if title:
            title = title.lower()
        timeout = self.data.get("timeout", None)
        setting = await self.store.words.patch_setting(
            id, title=title, timeout=timeout
        )
        if setting is None:
            raise HTTPNotFound
        setting_out = SettingSchema().dump(setting)
        return json_response(data=setting_out)


class SettingDeleteView(AuthRequiredMixin, View):
    @docs(
        tags=["settings"],
        summary="delete word",
        description="Delete existed word",
    )
    @request_schema(SettingIdSchema)
    @response_schema(SettingSchema)
    async def post(self):
        id = self.data["id"]
        setting = await self.store.words.get_setting_by_id(id)
        if setting is None:
            raise HTTPNotFound
        await self.store.words.delete_setting(id)
        setting_out = SettingSchema().dump(setting)
        return json_response(data=setting_out)


class SettingListView(AuthRequiredMixin, View):
    @docs(
        tags=["settings"],
        summary="get settings",
        description="return list of settings",
    )
    @response_schema(SettingListSchema)
    async def get(self):
        settings = await self.store.words.list_settings()
        return json_response(
            data=SettingListSchema().dump({"settings": settings})
        )
