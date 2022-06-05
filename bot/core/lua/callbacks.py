from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable

from bot.core.lua.lua_py_dict import LuaPyDict

from bot.core.serialize import serialize

if TYPE_CHECKING:
    from bot.bot import Bot


def factory(
    func: Callable[..., Awaitable[Any]]
) -> Callable[[Bot, int], Callable[..., Any]]:
    def constructor(bot: Bot, guild: int) -> Callable[..., Any]:
        def inner(*args: Any, **kwargs: Any) -> Any:
            return bot.sync_async.sync_call(func(bot, guild, *args, **kwargs))

        return inner

    return constructor


@factory
async def send_message(bot: Bot, guild: int, channel: str, message: str) -> LuaPyDict:
    ch_id = int(channel)
    ch = bot.cache.get_guild_channel(ch_id)
    assert ch and ch.guild_id == guild
    msg = await bot.rest.create_message(ch_id, message)
    return LuaPyDict(serialize(msg))
