from __future__ import annotations

import asyncpg
import crescent
import hikari

from docket.config import CONFIG
from docket.database.models.event import EventTrigger
from docket.database.models.script import Script
from docket.errors import DocketBaseError, ScriptNotFound
from docket.events import EVENT_ID_MAP, EVENT_MAP
from docket.plugins._checks import has_guild_perms
from docket.plugins._group import docket_group
from docket.plugins.config_scripts import script_name_autocomplete

EVENT_CHOICES = [(k.__name__, v) for k, v in EVENT_MAP.items()]

plugin = crescent.Plugin(
    "config-event-triggers",
    command_hooks=[has_guild_perms(hikari.Permissions.MANAGE_GUILD)],
)
events = docket_group.sub_group("event-triggers", "Manage event triggers")


@plugin.include
@events.child
@crescent.command(name="create", description="Create a new event trigger")
class CreateEventTrigger:
    event = crescent.option(
        int, "The event to trigger the script on", choices=EVENT_CHOICES
    )
    script = crescent.option(
        str, "The name of the script to trigger", autocomplete=script_name_autocomplete
    )

    async def callback(self, ctx: crescent.Context) -> None:
        assert ctx.guild_id
        script = await Script.exists(name=self.script, guild_id=ctx.guild_id)
        if not script:
            raise ScriptNotFound(self.script)

        event = await EventTrigger.goc(ctx.guild_id, self.event)
        try:
            await event.scripts.add(script)
        except asyncpg.UniqueViolationError as e:
            raise DocketBaseError(
                f"Script '{self.script}' is already triggered on this event."
            ) from e

        event_name = EVENT_ID_MAP[self.event].__name__
        await ctx.respond(f"Script '{self.script}' will be run on '{event_name}'.")


@plugin.include
@events.child
@crescent.command(name="delete", description="Delete an event trigger")
class DeleteEventTrigger:
    event = crescent.option(
        int, "The event to delete the trigger from", choices=EVENT_CHOICES
    )
    script = crescent.option(
        str,
        "The name of the script to no longer trigger",
        autocomplete=script_name_autocomplete,
    )

    async def callback(self, ctx: crescent.Context) -> None:
        assert ctx.guild_id
        script = await Script.exists(name=self.script, guild_id=ctx.guild_id)
        if not script:
            raise ScriptNotFound(self.script)

        event = await EventTrigger.exists(guild_id=ctx.guild_id, event_type=self.event)
        if not event:
            raise DocketBaseError("This event doesn't trigger this script.")

        await event.scripts.remove(script)
        event_name = EVENT_ID_MAP[self.event].__name__
        await ctx.respond(
            f"Script '{self.script}' will no longer be run on '{event_name}'."
        )


@plugin.include
@events.child
@crescent.command(name="view", description="View event triggers")
class ViewEventTriggers:
    async def callback(self, ctx: crescent.Context) -> None:
        assert ctx.guild_id

        events = (
            await EventTrigger.fetch_query().where(guild_id=ctx.guild_id).fetchmany()
        )
        result: list[str] = []
        for event in events:
            scripts: list[Script] = await event.scripts.fetchmany()  # type: ignore
            if not scripts:
                continue

            event_name = EVENT_ID_MAP[event.event_type].__name__
            script_str = "\n - ".join(s.name for s in scripts)
            result.append(f"{event_name}:\n - {script_str}")

        if not result:
            raise DocketBaseError("This server has no event triggers.")

        embed = hikari.Embed(
            title="Event Triggers", description="\n".join(result), color=CONFIG.theme
        )
        await ctx.respond(embed=embed)
