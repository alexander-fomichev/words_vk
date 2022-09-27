import logging
from typing import Optional

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from vk_api.config import BotConfig
from vk_api.data_classes import Update, UpdateObject
from vk_api.poller import Poller
from vk_api.queues import Mq

API_PATH = "https://api.vk.com/method/"


class VkApiAccessor:
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger("accessor")
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.ts: Optional[int] = None
        self.config: Optional[BotConfig] = None
        self.mq = None

    async def connect(self):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        try:
            await self._get_long_poll_service()
        except Exception as e:
            self.logger.error("Exception", exc_info=e)
        self.poller = Poller(self)
        self.mq = Mq()
        await self.mq.start()
        self.logger.info("start polling")
        await self.poller.start()

    async def disconnect(self):
        if self.poller:
            await self.poller.stop()
        if self.session:
            await self.session.close()
        if self.mq:
            await self.mq.stop()

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
                        "group_id": self.config.group_id,
                        "access_token": self.config.token,
                    },
                )
        ) as resp:
            data = (await resp.json())["response"]
            self.logger.info(data)
            self.key = data["key"]
            self.server = data["server"]
            self.ts = data["ts"]
            self.logger.info(self.server)

    async def poll(self):
        async with self.session.get(
                self._build_query(
                    host=self.server,
                    method="",
                    params={
                        "act": "a_check",
                        "key": self.key,
                        "ts": self.ts,
                        "wait": 5,
                    },
                )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)
            ts = data.get("ts", None)
            updates = []
            if ts is not None:
                self.ts = ts
                raw_updates = data.get("updates", [])
                for update in raw_updates:
                    updates.append(
                        Update(
                            type=update["type"],
                            object=UpdateObject(
                                peer_id=update["object"]["message"]["peer_id"],
                                user_id=update["object"]["message"]["from_id"],
                                body=update["object"]["message"]["text"],
                            ),
                        )
                    )
        print(updates)
        return updates
