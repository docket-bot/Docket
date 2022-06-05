from __future__ import annotations

from typing import Any, Awaitable, Callable, TYPE_CHECKING

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
async def send_message(
    bot: Bot, guild: int, channel: int, message: str
) -> None:
    assert channel in bot.cache.get_guild_channels_view_for_guild(guild)
    await bot.rest.create_message(channel, message)
