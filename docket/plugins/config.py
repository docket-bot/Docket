from __future__ import annotations

import asyncio
from difflib import get_close_matches
from typing import cast

import asyncpg
import crescent
import hikari

from docket.database.database import EVENT_MAP, Script, goc_guild
from docket.errors import DocketBaseError
from docket.plugins._checks import has_guild_perms
from docket.plugins._group import docket_group

TYPE_CHOICES = [("Custom", 0), *[(val.__name__, key) for val, key in EVENT_MAP.items()]]


plugin = crescent.Plugin(
    "config", command_hooks=[has_guild_perms(hikari.Permissions.MANAGE_GUILD)]
)
scripts = docket_group.sub_group("scripts", "Manage scripts")


async def wait_for_script(ctx: crescent.Context) -> str | None:
    def predicate(message: hikari.GuildMessageCreateEvent) -> bool:
        return (
            message.channel_id == ctx.channel_id
            and message.author.id == ctx.user.id
            and (message.content is not None or message.message.attachments is not None)
        )

    try:
        msg = await ctx.app.wait_for(
            hikari.GuildMessageCreateEvent, timeout=30, predicate=predicate
        )
    except asyncio.TimeoutError:
        return None

    if not msg.message.content:
        attachment = msg.message.attachments[0]
        content = str(await attachment.read())
    else:
        content = msg.message.content
        if content.startswith("```lua"):
            content = content.lstrip("```lua")
        content = msg.message.content.strip("```")
    return content


async def script_name_autocomplete(
    ctx: crescent.Context, option: hikari.AutocompleteInteractionOption
) -> list[hikari.CommandChoice]:
    if not ctx.guild_id:
        return []
    prefix = cast(str, option.value)
    scripts = await Script.fetch_query().where(guild_id=ctx.guild_id).fetchmany()
    script_names = [script.name for script in scripts]
    return [
        hikari.CommandChoice(name=name, value=name)
        for name in get_close_matches(prefix, script_names, 10, 0.2)
    ]


@plugin.include
@scripts.child
@crescent.command(name="create", description="Create a new script")
class CreateScript:
    name = crescent.option(str, "The name of the script")
    event = crescent.option(
        int, "The event this script will run on", choices=TYPE_CHOICES
    )

    async def callback(self, ctx: crescent.Context) -> None:
        assert ctx.guild_id
        await ctx.respond(
            "Please send the Lua script (either in a code block or file " "upload)."
        )
        content = await wait_for_script(ctx)
        if not content:
            await ctx.edit("Script creation timed out.")

        await goc_guild(ctx.guild_id)
        try:
            await Script(
                guild_id=ctx.guild_id,
                name=self.name,
                code=content,
                script_type=self.event,
            ).create()
        except asyncpg.UniqueViolationError:
            await ctx.edit("A script with that name already exists.")

        await ctx.edit(f"Script '{self.name}' created.")


@plugin.include
@scripts.child
@crescent.command(name="delete", description="Delete a script")
class DeleteScript:
    name = crescent.option(
        str, "The name of the script", autocomplete=script_name_autocomplete
    )

    async def callback(self, ctx: crescent.Context) -> None:
        assert ctx.guild_id
        script = await Script.exists(name=self.name, guild_id=ctx.guild_id)
        if not script:
            raise DocketBaseError(f"No script with name '{self.name}' exists.")
        await script.delete()
        await ctx.respond(f"Script '{self.name}' deleted.")
