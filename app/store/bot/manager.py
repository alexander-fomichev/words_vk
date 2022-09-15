import typing
from typing import List
from logging import getLogger

from sqlalchemy.exc import IntegrityError

from app.store.bot.game import Game
from app.store.vk_api.dataclasses import Message, Update
from app.words.models import GameModel

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")
        self._games: typing.Dict[int, Game] = dict()

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            peer_id = update.object.peer_id
            # Если игры нет, создаем ее
            if peer_id not in self._games:
                game = Game(self, self.app.store, peer_id,)
                await game.init()
                self._games[peer_id] = game
            else:
                game = await self._games[peer_id].reload()
            if game.game.status == "init":
                if update.object.body.lower() == "старт":
                    await game.registration()
                    await self.registration_message(peer_id)
                else:
                    await self.start_message(peer_id)
            if game.game.status == "registration":
                if update.object.body.lower() == "я":
                    await self.add_player(game_id=game.game.id, user_id=update.object.user_id, name="x")
                    await self.registration_ack_message(peer_id)
                else:
                    await self.registration_message(peer_id)
            return

    async def start_message(self, peer_id):
        await self.app.store.vk_api.send_message(
            Message(
                peer_id=peer_id,
                text=f"Для начала игры напишите старт",
            )
        )

    async def registration_message(self, peer_id):
        await self.app.store.vk_api.send_message(
            Message(
                peer_id=peer_id,
                text=f'Регистрация игроков. Если хотите участвовать, напишите "я"',
            )
        )

    async def registration_ack_message(self, peer_id):
        await self.app.store.vk_api.send_message(
            Message(
                peer_id=peer_id,
                text=f'Вы зарегистрированы',
            )
        )

    async def registration_failed_message(self, peer_id):
        await self.app.store.vk_api.send_message(
            Message(
                peer_id=peer_id,
                text=f"Для игры необходимо хотя бы 2 участника",
            )
        )

    async def connect(self):
        games_db: List[GameModel] = await self.app.store.words.list_active_games()
        self._games = {
            game_db.peer_id: Game(self, self.app.store, game_db.peer_id, game_db.setting.title, game_db)
            for game_db in games_db
        }
        for game in self._games.values():
            await game.re_init()

    async def disconnect(self):
        for game in self._games.values():
            if game.task:
                game.task.cancel()

    async def add_player(self, game_id, user_id, name):
        try:
            await self.app.store.words.create_player(game_id, user_id, name)
        except IntegrityError:
            pass



