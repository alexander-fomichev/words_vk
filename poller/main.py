import asyncio
import logging
import os

from vk_api.accessor import VkApiAccessor
from vk_api.config import setup_config


async def run(accessor: VkApiAccessor):
    await accessor.connect()


async def stop(accessor: VkApiAccessor):
    await accessor.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    accessor = VkApiAccessor()
    setup_config(accessor, config_path=os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "config.yml"
            ))
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(run(accessor))
        loop.run_forever()
    except KeyboardInterrupt:  # pragma: no branch
        pass
    finally:
        accessor.disconnect()
        loop.close()
