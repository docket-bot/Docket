import dataclasses
import json


@dataclasses.dataclass
class Config:
    discord_token: str


with open(".config.json") as f:
    CONFIG = Config(**json.loads(f.read()))
