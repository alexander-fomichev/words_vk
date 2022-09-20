import typing
from typing import List
from logging import getLogger

from app.base.base_accessor import BaseAccessor
from app.store.bot.game import Game
from app.store.bot.messages import registration_message, start_message, player_move_message, status_message, \
    vote_message, vote_self_message
from app.store.vk_api.dataclasses import Update
from app.words.models import GameModel

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app
        self.bot = None
        self._games: typing.Dict[int, Game] = dict()

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            peer_id = update.object.peer_id
            cmd = update.object.body.lower()
            # Если игры нет, создаем ее
            if peer_id not in self._games or self._games[peer_id].game_db.status == "finished":
                game = Game(
                    self,
                    self.app.store,
                    peer_id,
                )
                await game.init()
                self._games[peer_id] = game
            else:
                game = await self._games[peer_id].reload()
            if cmd == "!статус":
                game_id = game.game_db.id
                status = game.game_db.status
                if game.game_db.status == "init":
                    games_db = await self.app.store.words.list_games(peer_id=peer_id, status='finished')
                    if games_db:
                        game_id = games_db[-1].id
                        status = games_db[-1].status
                score = await self.get_score(game_id=game_id)

                await status_message(self.app.store.vk_api, peer_id, status, score)
            else:
                if game.game_db.status == "init":
                    setting = await self.app.store.words.get_setting_by_title(cmd)
                    if setting:
                        game.setting_title = cmd
                        await game.registration(setting)
                        await registration_message(self.app.store.vk_api, peer_id, setting.timeout, cmd)
                    else:
                        await start_message(self.app.store.vk_api, peer_id)
                elif game.game_db.status == "registration":
                    if cmd == "я":
                        await game.add_player(user_id=update.object.user_id)
                    else:
                        await registration_message(self.app.store.vk_api, peer_id, game.game_db.setting.timeout, game.game_db.setting.title)
                elif game.game_db.status == "started":
                    if update.object.user_id == game.game_db.current_move:
                        await game.check_word(cmd)
                    else:
                        name = game.get_player_name_by_user_id(game.game_db.current_move)
                        last_word = game.game_db.last_word
                        await player_move_message(self.app.store.vk_api, game.peer_id, name, last_word, game.game_db.setting.timeout)
                elif game.game_db.status == "vote_word":
                    name = game.get_player_name_by_user_id(update.object.user_id)
                    if update.object.user_id == game.game_db.current_move:
                        await vote_self_message(self.app.store.vk_api, game.peer_id, name)
                    else:
                        if cmd == "да":
                            await game.add_vote(True, update.object.user_id)
                        elif cmd == "нет":
                            await game.add_vote(False, update.object.user_id)
                        else:
                            await vote_message(self.app.store.vk_api, peer_id, game.game_db.vote_word, game.game_db.setting.timeout)
                return

    async def connect(self, app: "Application"):
        games_db: List[GameModel] = await app.store.words.list_games()
        self._games = {
            game_db.peer_id: Game(self, app.store, game_db.peer_id, game_db.setting.title, game_db)
            for game_db in games_db
        }
        for game in self._games.values():
            await game.re_init()

    async def disconnect(self, app: "Application"):
        for game in self._games.values():
            if game.task:
                game.task.cancel()

    async def get_score(self, game_id: int):
        """ возвращает счет игры """
        players_from_db = await self.app.store.words.list_player(game_id)
        players = [(num, player.name, player.score) for num, player in enumerate(players_from_db, 1)]
        return players
