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

    # lua runtime
    max_memory: int = 128  # kb
    max_cycles: int = 1_000_000


with open(".config.json") as f:
    CONFIG = Config(**json.loads(f.read()))
