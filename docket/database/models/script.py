from __future__ import annotations

from apgorm import ForeignKey, Model, types

from .guild import Guild


class Script(Model):
    script_id = types.Serial().field()
    guild_id = types.Numeric().field()
    name = types.Text().field()
    code = types.Text().field()

    name.add_validator(lambda name: len(name) <= 32)
    code.add_validator(lambda code: len(code) <= 1_024)

    guild_fk = ForeignKey(guild_id, Guild.guild_id)

    primary_key = (script_id,)
