from __future__ import annotations

from typing import Any

import hikari
from apgorm import Database as BaseDB
from apgorm import ForeignKey, Index, IndexType, Model, types

from docket.config import CONFIG

EVENT_MAP: dict[type[hikari.Event], int] = {hikari.GuildMessageCreateEvent: 2}
VALID_TYPES = {0, 1} | set(EVENT_MAP.values())


class Guild(Model):
    guild_id = types.Numeric().field()
    log_channel = types.Numeric().nullablefield()

    primary_key = (guild_id,)


class Script(Model):
    name = types.Text().field()
    guild_id = types.Numeric().field()
    script_type = types.SmallInt().field()
    code = types.Text().field()

    name.add_validator(lambda name: len(name) <= 32)
    script_type.add_validator(lambda event_type: event_type in VALID_TYPES)
    code.add_validator(lambda code: len(code) <= 1_024)

    guild_fq = ForeignKey(guild_id, Guild.guild_id)

    primary_key = (name, guild_id)


class Database(BaseDB):
    guilds = Guild
    triggers = Script

    indexes = [Index(Script, Script.script_type, IndexType.HASH)]

    def __init__(self) -> None:
        super().__init__("docket/database/migrations")

    async def connect(self, **_: Any) -> None:
        await super().connect(
            host=CONFIG.db_host,
            user=CONFIG.db_user,
            password=CONFIG.db_password,
            database=CONFIG.db_name,
        )

        if self.must_create_migrations():
            print("Making migrations...")
            self.create_migrations()
        if await self.must_apply_migrations():
            print("Applying migrations...")
            await self.apply_migrations()
