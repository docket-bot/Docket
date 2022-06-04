import crescent
import hikari
from bot import event_middleware as events

plugin = crescent.Plugin("events")


@plugin.include
@crescent.event
async def on_message(event: hikari.MessageCreateEvent):
    await events.default(event)
