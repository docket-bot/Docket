from typing import Any, Awaitable, Callable, Type, TypeVar

import crescent
import hikari

from docket.core import event_middleware

plugin = crescent.Plugin("events")

EVENT = TypeVar("EVENT", bound=Type[hikari.Event])


def include_event(
    event: EVENT,
    predicate: Callable[[Any], bool],
    callback: Callable[[hikari.Event], Awaitable[None]] = event_middleware.default,
) -> None:
    @plugin.include
    @crescent.event(event_type=event)
    async def _(_event: hikari.Event) -> None:
        if not predicate(_event):
            return
        await callback(_event)


include_event(
    hikari.MessageCreateEvent, predicate=lambda event: not event.author.is_bot
)
