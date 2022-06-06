from __future__ import annotations

import typing

import hikari
from apgorm import LazyList

from docket.core.lua.executor import execute_lua
from docket.core.lua.lua_py_dict import LuaPyDict
from docket.core.serialize import serialize
from docket.database.database import EVENT_MAP, Script

if typing.TYPE_CHECKING:
    from docket.bot import Docket


async def get_scripts(  # TODO: cache
    guild_id: int, event: type[hikari.Event]
) -> LazyList[typing.Any, Script]:
    return (
        await Script.fetch_query()
        .where(guild_id=guild_id, script_type=EVENT_MAP[event])
        .fetchmany()
    )


def _middleware(
    function: typing.Callable[[hikari.Event], typing.Dict[str, typing.Any]]
) -> typing.Callable[[hikari.Event], typing.Awaitable[None]]:
    async def inner(event: hikari.Event) -> None:
        guild_id = typing.cast(int, event.guild_id)  # type: ignore
        for script in await get_scripts(guild_id, type(event)):
            execute_lua(
                typing.cast("Docket", event.app),
                guild_id,
                script.code,
                LuaPyDict(function(event)),
            )

    return inner


@_middleware
def default(event: hikari.Event) -> typing.Dict[str, typing.Any]:
    return serialize(event)
