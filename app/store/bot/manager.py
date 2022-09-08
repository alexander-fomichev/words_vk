import typing
from logging import getLogger

from app.store.vk_api.dataclasses import Message, Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def handle_updates(self, updates: list[Update]):
        if updates:
            for update in updates:
                if update.object.body.lower() == "старт":
                    players = await self.app.store.vk_api.get_players(
                        peer_id=update.object.peer_id
                    )
                    print(players)
                    active_players = tuple(filter(lambda x: x.online > 0, players))
                    if len(active_players) < 2:
                        await self.app.store.vk_api.send_message(
                            Message(
                                peer_id=update.object.peer_id,
                                text="Для старта игры необходимо 2 и более игроков онлайн",
                            )
                        )
                else:
                    await self.app.store.vk_api.send_message(
                        Message(
                            peer_id=update.object.peer_id,
                            text=f"И тебе {update.object.body}",
                        )
                    )
