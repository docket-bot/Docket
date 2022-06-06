from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable

from docket.core.lua.lua_py_dict import LuaPyDict
from docket.core.serialize import serialize

if TYPE_CHECKING:
    from docket.bot import Docket


def lua_callable(
    func: Callable[..., Awaitable[Any]]
) -> Callable[[Docket, int], Callable[..., Any]]:
    # generates a function, that when called, will create a lua callable bound to a
    # specific guild
    def constructor(bot: Docket, guild: int) -> Callable[..., Any]:
        # when called, binds the initial callback to a guild
        def inner(*args: Any, **kwargs: Any) -> Any:
            # calls the initial callback using the SyncAsync manager
            return bot.sync_async.sync_call(func(bot, guild, *args, **kwargs))

        return inner

    return constructor


@lua_callable
async def send_message(
    bot: Docket, guild: int, channel: str, message: str
) -> LuaPyDict:
    ch_id = int(channel)
    ch = bot.cache.get_guild_channel(ch_id)
    assert ch and ch.guild_id == guild
    msg = await bot.rest.create_message(ch_id, message)
    return LuaPyDict(serialize(msg))
