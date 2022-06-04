import crescent
import hikari
from bot.core import event_middleware as events

plugin = crescent.Plugin("events")


@plugin.include
@crescent.event
async def on_message(event: hikari.MessageCreateEvent) -> None:
    await events.default(event)
