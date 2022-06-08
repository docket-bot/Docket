from __future__ import annotations

import typing

import hikari
from apgorm import LazyList

from docket.core.lua.lua_py_dict import LuaPyDict
from docket.core.serialize import serialize
from docket.database.models.event import EventTrigger
from docket.database.models.script import Script
from docket.events import EVENT_MAP

if typing.TYPE_CHECKING:
    from docket.bot import Docket


async def get_scripts(  # TODO: cache
    guild_id: int, event: type[hikari.Event]
) -> LazyList[typing.Any, Script] | None:
    event_trigger = await EventTrigger.exists(
        guild_id=guild_id, event_type=EVENT_MAP[event]
    )
    if not event_trigger:
        return None
    return await event_trigger.scripts.fetchmany()  # type: ignore


def _middleware(
    function: typing.Callable[[hikari.GuildEvent], typing.Dict[str, typing.Any]]
) -> typing.Callable[[hikari.GuildEvent], typing.Awaitable[None]]:
    async def inner(event: hikari.GuildEvent) -> None:
        bot = typing.cast("Docket", event.app)
        scripts = await get_scripts(event.guild_id, type(event))
        if not scripts:
            return
        for script in scripts:
            bot.runtime.execute(
                event.guild_id,
                script.script_id,
                script.code,
                LuaPyDict(function(event)),
            )

    return inner


@_middleware
def default(event: hikari.GuildEvent) -> typing.Dict[str, typing.Any]:
    return serialize(event)
