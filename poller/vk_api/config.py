import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from vk_api.accessor import VkApiAccessor


@dataclass
class BotConfig:
    token: str
    group_id: int


def setup_config(accessor: "VkApiAccessor", config_path: str):
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)

    accessor.config = BotConfig(
            token=raw_config["bot"]["token"],
            group_id=raw_config["bot"]["group_id"],
        )

