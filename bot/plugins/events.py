import crescent
import hikari
from bot import event_middleware as events

plugin = crescent.Plugin("events")


@plugin.include
@crescent.event
async def on_message(event: hikari.MessageCreateEvent):
    events.default(event)


@plugin.include
@crescent.event
async def on_guild_typing_event(event: hikari.GuildTypingEvent):
    events.handle_guild_typing_event(event)
