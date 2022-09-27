import asyncio
import pickle
import random

import typing
from typing import Optional

import aio_pika
from aio_pika import connect
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractQueue
from aiohttp import ClientSession, TCPConnector

from app.base.base_accessor import BaseAccessor

from app.store.vk_api.dataclasses import Message, Update, UpdateObject, Player

if typing.TYPE_CHECKING:
    from app.web.app import Application
    from app.store.bot.manager import BotManager

API_PATH = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.queue: Optional[AbstractQueue] = None
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.ts: Optional[int] = None

    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        try:
            await self._get_long_poll_service()
        except Exception as e:
            self.logger.error("Exception", exc_info=e)
        self.logger.info("waiting for messages")
        self.connection = await connect(f"amqp://guest:guest@rabbitmq/")
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue("test_queue", auto_delete=True)
        await self.queue.consume(self.process_message)

    async def process_message(self,
                              message: aio_pika.abc.AbstractIncomingMessage,
                              ) -> None:
        async with message.process():
            update_dict = (pickle.loads(message.body))
            update_object = UpdateObject(**update_dict)
            print(update_object)
            await self.app.store.bots_manager.handle_updates(update_object)

    async def disconnect(self, app: "Application"):
        if self.connection:
            await self.connection.close()
        if self.session:
            await self.session.close()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        async with self.session.get(
            self._build_query(
                host=API_PATH,
                method="groups.getLongPollServer",
                params={
                    "group_id": self.app.config.bot.group_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = (await resp.json())["response"]
            self.logger.info(data)
            self.key = data["key"]
            self.server = data["server"]
            self.ts = data["ts"]
            self.logger.info(self.server)

    async def send_message(self, message: Message) -> None:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.send",
                params={
                    "random_id": random.randint(1, 2**32),
                    "peer_id": message.peer_id,
                    "message": message.text,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def get_players(self, peer_id) -> list[Player]:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.getConversationMembers",
                params={
                    "peer_id": peer_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = (await resp.json())["response"]
            self.logger.info(data)
            players = [
                Player(
                    user_id=value["id"],
                    online=value["online"],
                    name=f"{value['first_name']} {value['last_name']}",
                )
                for value in data["profiles"]
            ]
            return players
