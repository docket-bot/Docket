import crescent
import hikari

from bot.core import event_middleware

plugin = crescent.Plugin("events")


@plugin.include
@crescent.event
async def on_message(event: hikari.MessageCreateEvent) -> None:
    event_middleware.default(event)
