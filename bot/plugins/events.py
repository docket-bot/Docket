from typing import Awaitable, Callable, Type, TypeVar

import crescent
import hikari

from bot.core import event_middleware as events

plugin = crescent.Plugin("events")

EVENT = TypeVar("EVENT", bound=Type[hikari.Event])


def include_event(
    event: EVENT, callback: Callable[[hikari.Event], Awaitable[None]] = events.default
) -> None:
    @plugin.include
    @crescent.event(event_type=event)
    async def _(_event: hikari.Event) -> None:
        await callback(_event)


include_event(hikari.MessageCreateEvent)
