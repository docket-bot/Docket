from __future__ import annotations

import asyncpg
from apgorm import Model, types


class Guild(Model):
    guild_id = types.Numeric().field()
    log_channel = types.Numeric().nullablefield()

    primary_key = (guild_id,)

    @staticmethod
    async def goc(guild_id: int) -> Guild:
        try:
            return await Guild(guild_id=guild_id).create()
        except asyncpg.UniqueViolationError:
            return await Guild.fetch(guild_id=guild_id)
