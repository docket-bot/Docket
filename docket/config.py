import dataclasses
import json


@dataclasses.dataclass
class Config:
    discord_token: str
    db_password: str
    db_name: str = "docket"
    db_user: str = "docket"
    db_host: str = "localhost"
    theme: int = 0x21BE93


with open(".config.json") as f:
    CONFIG = Config(**json.loads(f.read()))
