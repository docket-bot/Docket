from __future__ import annotations

import crescent
import hikari

from bot.core.event import handle_event

plugin = crescent.Plugin("custom-events")


# message events
@plugin.include
@crescent.event
async def on_message(event: hikari.GuildMessageCreateEvent) -> None:
    await handle_event(event)


@plugin.include
@crescent.event
async def on_message_delete(event: hikari.GuildMessageDeleteEvent) -> None:
    await handle_event(event)


@plugin.include
@crescent.event
async def on_message_edit(event: hikari.GuildMessageUpdateEvent) -> None:
    await handle_event(event)


@plugin.include
@crescent.event
async def on_message_bulk_delete(event: hikari.GuildBulkMessageDeleteEvent) -> None:
    await handle_event(event)


# reaction events
@plugin.include
@crescent.event
async def on_reaction_add(event: hikari.GuildReactionAddEvent) -> None:
    await handle_event(event)


@plugin.include
@crescent.event
async def on_reaction_remove(event: hikari.GuildReactionDeleteEvent) -> None:
    await handle_event(event)


@plugin.include
@crescent.event
async def on_reaction_clear(event: hikari.GuildReactionDeleteAllEvent) -> None:
    await handle_event(event)
