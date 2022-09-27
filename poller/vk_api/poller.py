import asyncio
import pickle
from asyncio import Task
from typing import Optional

import aio_pika


class Poller:
    def __init__(self, accessor):
        self.accessor = accessor
        self.is_running = False
        self.poll_task: Optional[Task] = None

    async def start(self):
        self.is_running = True
        self.poll_task = asyncio.create_task(self.poll())

    async def stop(self):
        self.is_running = False
        await self.poll_task

    async def poll(self):
        while self.is_running:
            updates = await self.accessor.poll()
            for update in updates:
                if update.type == "message_new":
                    await self.accessor.mq.channel.default_exchange.publish(
                        aio_pika.Message(body=pickle.dumps({"peer_id": update.object.peer_id,
                                                            "user_id": update.object.user_id,
                                                            "body": update.object.body,
                                                            })),
                        routing_key=self.accessor.mq.queue_name,
                    )
