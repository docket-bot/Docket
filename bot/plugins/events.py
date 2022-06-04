from __future__ import annotations

import hikari
import crescent

from bot.core.event import handle_event


plugin = crescent.Plugin("custom-events")


@plugin.include
@crescent.event
async def on_message(event: hikari.GuildMessageCreateEvent) -> None:
    await handle_event(event)
