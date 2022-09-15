import asyncio
import random
import typing
from asyncio import Task
from datetime import datetime
from typing import Optional

from app.store import Store
from app.words.models import GameModel

if typing.TYPE_CHECKING:
    from app.store.bot.manager import BotManager


class Game:
    def __init__(
        self, manager: "BotManager", store: Store, peer_id: int, setting_title: str = "слова", game: GameModel = None
    ):
        self.manager = manager
        self.store = store
        self.setting_title = setting_title
        self.peer_id = peer_id
        self.game: Optional[GameModel] = game
        self.task: Optional[Task] = None

    @property
    def timeout_with_elapsed_time(self):
        elapsed = 0
        if self.game and self.game.pause_timestamp:
            elapsed = self.game.pause_timestamp - self.game.event_timestamp
        return self.game.setting.timeout - int(elapsed)

    async def init(self):
        setting = await self.store.words.get_setting_by_title(self.setting_title)
        game = await self.store.words.create_game(setting.id, self.peer_id)
        self.game = await self.store.words.get_game_by_id(game.id)
        return self.game

    async def re_init(self):
        if self.game.status == "registration":
            await self.registration()

    async def registration(self):
        await self.store.words.patch_game(self.game.id, status="registration", event_timestamp=datetime.now())
        self.task = asyncio.create_task(self._timer(self.timeout_with_elapsed_time, self.check_registration))
        return

    async def check_registration(self):
        self.game = await self.store.words.get_game_by_id(self.game.id)
        players = [str(player.id) for player in self.game.players]
        if len(players) < 2:
            self.game = await self.store.words.clear_game(self.game.id)
            await self.manager.registration_failed_message(self.peer_id)
            return
        random.shuffle(players)
        moves_order = " ".join(players)
        self.store.words.patch_game(
            self.game.id, status="started", event_timestamp=None, moves_order=moves_order, current_move=0
        )

    async def _timer(self, timeout: int, callback=None, *args, **kwargs):
        try:
            await asyncio.sleep(timeout)
            if callback is not None:
                await callback(*args, **kwargs)
        except asyncio.CancelledError:
            self.store.words.patch_game(self.game.id, pause_timestamp=datetime.now())
            raise

    async def reload(self):
        self.game = await self.store.words.get_game_by_id(self.game.id)
        return self
