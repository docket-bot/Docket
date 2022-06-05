import typing

import crescent
import hikari

from bot.core import event_middleware as events

plugin = crescent.Plugin("events")


def include_event(
    event: typing.Type[hikari.Event],
    callback: typing.Callable[[hikari.Event], typing.Awaitable[None]] = events.default,
):
    @plugin.include
    @crescent.event
    async def inner(_event: event) -> None:
        await callback(_event)

    return inner


include_event(hikari.MessageCreateEvent)
