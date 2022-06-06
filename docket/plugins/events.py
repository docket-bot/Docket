from typing import Callable, Type, TypeVar

import crescent
import hikari

from docket.core import event_middleware

plugin = crescent.Plugin("events")

EVENT = TypeVar("EVENT", bound=Type[hikari.Event])


def include_event(
    event: EVENT, callback: Callable[[hikari.Event], None] = event_middleware.default
) -> None:
    @plugin.include
    @crescent.event(event_type=event)
    async def _(_event: hikari.Event) -> None:
        callback(_event)


include_event(hikari.MessageCreateEvent)
