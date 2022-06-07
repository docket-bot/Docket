from __future__ import annotations

from apgorm import Model, types
from asyncpg import UniqueViolationError


class Guild(Model):
    guild_id = types.Numeric().field()
    log_channel = types.Numeric().nullablefield()

    primary_key = (guild_id,)

    @staticmethod
    async def get_or_create(guild_id: int) -> Guild:
        try:
            return await Guild(guild_id=guild_id).create()
        except UniqueViolationError:
            return await Guild.fetch(guild_id=guild_id)
