from typing import Optional, Union

from pydantic import BaseModel


class User(BaseModel):
    id: int
    is_bot: bool
    username: str


class Guild(BaseModel):
    id: int
    name: str


class Channel(BaseModel):
    id: int
    guild: Guild
    name: str


class Member(BaseModel):
    user: User
    guild: Guild
    nickname: Optional[str] = None


class Message(BaseModel):
    id: int
    channel: Channel
    author: Union[Member, User]
    content: str
