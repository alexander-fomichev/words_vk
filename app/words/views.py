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
    PlayerSchema, PatchPlayerSchema, PlayerListSchema, GameIdSchema, GameSchema, GamePatchSchema, GameListSchema,
    PeerIdSchema, GameSettingSchema, PlayerIdSchema,
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


class PlayerGetView(AuthRequiredMixin, View):
    @docs(
        tags=["players"],
        summary="get player",
        description="return player",
    )
    @querystring_schema(PlayerIdSchema)
    @response_schema(PlayerSchema)
    async def get(self):
        player_id = self.request["querystring"]["id"]
        player = await self.store.words.get_player(player_id=player_id)
        if player is None:
            raise HTTPNotFound
        return json_response(data=PlayerSchema().dump(player))


class PlayerAddView(AuthRequiredMixin, View):
    @docs(tags=["players"], summary="add player", description="Add new player")
    @request_schema(PlayerSchema)
    @response_schema(PlayerSchema)
    async def post(self):
        game_id = self.data["game_id"]
        user_id = self.data["user_id"]
        user_name = self.data["name"]
        try:
            player = await self.store.words.create_player(game_id, user_id, user_name)
        except IntegrityError as e:
            if e.orig.pgcode == "23505":
                raise HTTPConflict
            if e.orig.pgcode == "23503":
                raise HTTPNotFound
        player_out = PlayerSchema().dump(player)
        return json_response(data=player_out)


class PlayerPatchView(AuthRequiredMixin, View):
    @docs(
        tags=["players"],
        summary="patch setting",
        description="partial update player",
    )
    @request_schema(PatchPlayerSchema)
    @response_schema(PlayerSchema)
    async def post(self):
        player_id = self.data["id"]
        status = self.data.get("status", None)
        online = self.data.get("online", None)
        player = await self.store.words.patch_player(
            player_id=player_id, status=status, online=online
        )
        if player is None:
            raise HTTPNotFound
        player_out = PlayerSchema().dump(player)
        return json_response(data=player_out)


class PlayerDeleteView(AuthRequiredMixin, View):
    @docs(
        tags=["players"],
        summary="delete player",
        description="Delete existed player",
    )
    @request_schema(PlayerIdSchema)
    @response_schema(PlayerSchema)
    async def post(self):
        player_id = self.data["id"]
        player = await self.store.words.get_player(player_id)
        if player is None:
            raise HTTPNotFound
        await self.store.words.delete_player(player_id)
        player_out = PlayerSchema().dump(player)
        return json_response(data=player_out)


class PlayerListView(AuthRequiredMixin, View):
    @docs(
        tags=["players"],
        summary="get players",
        description="return list of players",
    )
    @querystring_schema(GameIdSchema)
    @response_schema(PlayerListSchema)
    async def get(self):
        game_id = self.request["querystring"]["id"]
        game = await self.store.words.get_game_by_id(id=game_id)
        if not game:
            raise HTTPNotFound
        players = await self.store.words.list_player(game_id)
        return json_response(
            data=PlayerListSchema().dump({"players": players})
        )


class GameGetView(AuthRequiredMixin, View):
    @docs(
        tags=["games"],
        summary="get game",
        description="return game",
    )
    @querystring_schema(GameIdSchema)
    @response_schema(GameSettingSchema)
    async def get(self):
        game_id = self.request["querystring"]["id"]
        game = await self.store.words.get_game_by_id(id=game_id)
        if game is None:
            raise HTTPNotFound
        return json_response(data=GameSettingSchema().dump(game))


class GameAddView(AuthRequiredMixin, View):
    @docs(
        tags=["games"], summary="add game", description="Add new game"
    )
    @request_schema(GameSchema)
    @response_schema(GameSettingSchema)
    async def post(self):
        setting_id = self.data["setting_id"]
        peer_id = self.data["peer_id"]
        # players = self.data["players"]
        try:
            new_game = await self.store.words.create_game(setting_id=setting_id, peer_id=peer_id)
        except IntegrityError as e:
            if e.orig.pgcode == "23503":
                raise HTTPNotFound
        game = await self.store.words.get_game_by_id(new_game.id)
        game_out = GameSettingSchema().dump(game)
        return json_response(data=game_out)


class GamePatchView(AuthRequiredMixin, View):
    @docs(
        tags=["games"],
        summary="patch game",
        description="partial update game",
    )
    @request_schema(GamePatchSchema)
    @response_schema(GameSettingSchema)
    async def post(self):
        game_id = self.data["id"]
        status = self.data.get("status", None)
        players = self.data.get("players", None)
        game = await self.store.words.patch_game(
            id=game_id, players=players, status=status
        )
        if game is None:
            raise HTTPNotFound
        game_out = GameSettingSchema().dump(game)
        return json_response(data=game_out)


class GameDeleteView(AuthRequiredMixin, View):
    @docs(
        tags=["games"],
        summary="delete game",
        description="Delete existed game",
    )
    @request_schema(GameIdSchema)
    @response_schema(GameSettingSchema)
    async def post(self):
        game_id = self.data["id"]
        game = await self.store.words.get_game_by_id(game_id)
        if game is None:
            raise HTTPNotFound
        await self.store.words.delete_game(game_id)
        game_out = GameSettingSchema().dump(game)
        return json_response(data=game_out)


class GameListView(AuthRequiredMixin, View):
    @docs(
        tags=["games"],
        summary="get games",
        description="return list of games",
    )
    @querystring_schema(PeerIdSchema)
    @response_schema(GameListSchema)
    async def get(self):
        peer_id = self.request["querystring"].get("peer_id", None)
        games = await self.store.words.list_games(peer_id)
        return json_response(
            data=GameListSchema().dump({"games": games})
        )
