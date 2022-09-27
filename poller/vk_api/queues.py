import aio_pika


class Mq:
    def __init__(self):
        self.connection = None
        self.queue_name = "test_queue"
        self.channel = None
        self.queue = None

    async def start(self):
        self.connection = await aio_pika.connect_robust(
            "amqp://guest:guest@rabbitmq/",
        )
        self.channel = await self.connection.channel()
        # self.queue = await self.channel.declare_queue(self.queue_name, auto_delete=True)

    async def stop(self):
        await self.connection.close()
