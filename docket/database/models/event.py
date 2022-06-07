from __future__ import annotations

import asyncpg
from apgorm import ForeignKey, ManyToMany, Model, Unique, types

from docket.database.models.script import Script


class EventTrigger(Model):
    trigger_id = types.Serial().field()
    guild_id = types.Numeric().field()
    event_type = types.SmallInt().field()

    scripts: ManyToMany[Script, "EventTriggerScript"] = ManyToMany(
        "trigger_id",
        "event_trigger_scripts.trigger_id",
        "event_trigger_scripts.script_id",
        "scripts.script_id",
    )
    guild_event_unique = Unique(guild_id, event_type)

    primary_key = (trigger_id,)

    @staticmethod
    async def goc(guild_id: int, event_type: int) -> EventTrigger:
        try:
            return await EventTrigger(guild_id=guild_id, event_type=event_type).create()
        except asyncpg.UniqueViolationError:
            return await EventTrigger.fetch(guild_id=guild_id, event_type=event_type)


class EventTriggerScript(Model):
    trigger_id = types.Int().field()
    script_id = types.Int().field()

    trigger_fk = ForeignKey(trigger_id, EventTrigger.trigger_id)
    script_fk = ForeignKey(script_id, Script.script_id)

    primary_key = (trigger_id, script_id)
