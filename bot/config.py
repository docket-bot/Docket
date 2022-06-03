from dataclasses import dataclass
from dotenv import dotenv_values


@dataclass
class Config:
    DISCORD_TOKEN: str


CONFIG = Config(**{key:value for key, value in dotenv_values(".env").items() if value})
