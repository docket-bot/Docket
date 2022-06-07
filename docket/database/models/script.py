from __future__ import annotations

from apgorm import ForeignKey, Model, Unique, types
from apgorm.exceptions import ModelNotFound

from docket.database.models.guild import Guild
from docket.errors import ScriptNotFound


class Script(Model):
    script_id = types.Serial().field()
    guild_id = types.Numeric().field()
    name = types.Text().field()
    code = types.Text().field()

    name.add_validator(lambda name: len(name) <= 32)
    code.add_validator(lambda code: len(code) <= 1_024)

    guild_name_unique = Unique(name, guild_id)
    guild_fk = ForeignKey(guild_id, Guild.guild_id)

    primary_key = (script_id,)

    @staticmethod
    async def get_by_name(name: str, guild_id: int) -> Script:
        try:
            return await Script.fetch(name=name, guild_id=guild_id)
        except ModelNotFound:
            raise ScriptNotFound(name) from None
