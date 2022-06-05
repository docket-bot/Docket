from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable

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
async def send_message(bot: Bot, guild: int, channel: str, message: str) -> None:
    ch_id = int(channel)
    ch = bot.cache.get_guild_channel(ch_id)
    assert ch and ch.guild_id == guild
    await bot.rest.create_message(ch_id, message)
