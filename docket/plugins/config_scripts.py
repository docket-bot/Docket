from __future__ import annotations

import re
import asyncio
from difflib import get_close_matches
from typing import cast

import asyncpg
import crescent
import hikari

from docket.config import CONFIG
from docket.database.models.guild import Guild
from docket.database.models.script import Script
from docket.errors import DocketBaseError, ScriptNotFound
from docket.plugins._checks import has_guild_perms
from docket.plugins._group import docket_group

plugin = crescent.Plugin(
    "config-scripts", command_hooks=[has_guild_perms(hikari.Permissions.MANAGE_GUILD)]
)
scripts = docket_group.sub_group("scripts", "Manage scripts")


CODE_BLOCK = re.compile(r"^`*\w*?\s*(?P<code>.+)\s*`*$")


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
    elif not msg.message.attachments:
        match = CODE_BLOCK.search(msg.message.content)
        assert match
        content = match.group("code").strip("`")
    else:
        raise DocketBaseError("You can't send both a code block and an attachment.")
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

    async def callback(self, ctx: crescent.Context) -> None:
        name = self.name.lower().casefold().replace(" ", "-")
        assert ctx.guild_id
        await ctx.respond(
            "Please send the Lua script (either in a code block or file " "upload)."
        )
        content = await wait_for_script(ctx)
        if not content:
            await ctx.edit("Script creation timed out.")

        await Guild.get_or_create(ctx.guild_id)
        try:
            await Script(guild_id=ctx.guild_id, name=name, code=content).create()
        except asyncpg.UniqueViolationError:
            await ctx.edit("A script with that name already exists.")
            return

        await ctx.edit(f"Script '{name}' created.")


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
            raise ScriptNotFound(self.name)
        await script.delete()
        await ctx.respond(f"Script '{self.name}' deleted.")


@plugin.include
@scripts.child
@crescent.command(name="edit", description="Edit a script")
class EditScript:
    name = crescent.option(
        str, "The name of the script", autocomplete=script_name_autocomplete
    )

    async def callback(self, ctx: crescent.Context) -> None:
        assert ctx.guild_id
        script = await Script.exists(name=self.name, guild_id=ctx.guild_id)
        if not script:
            raise ScriptNotFound(self.name)
        await ctx.respond(
            "Please send the Lua script (either in a code block or file " "upload)."
        )
        content = await wait_for_script(ctx)
        if not content:
            await ctx.edit("Script creation timed out.")
            return
        script.code = content
        await script.save()
        await ctx.edit(f"Script '{self.name}' edited.")


@plugin.include
@scripts.child
@crescent.command(name="view", description="View a script")
class ViewScript:
    name = crescent.option(
        str,
        "The name of the script",
        autocomplete=script_name_autocomplete,
        default=None,
    )

    async def callback(self, ctx: crescent.Context) -> None:
        assert ctx.guild_id
        if self.name is None:
            scripts = (
                await Script.fetch_query().where(guild_id=ctx.guild_id).fetchmany()
            )
            if not scripts:
                raise DocketBaseError("This server has no scripts.")

            embed = hikari.Embed(
                title="Server Scripts",
                description="-" + "\n-".join(s.name for s in scripts),
                color=CONFIG.theme,
            )
            await ctx.respond(embed=embed)

        else:
            script = await Script.exists(name=self.name, guild_id=ctx.guild_id)
            if not script:
                raise ScriptNotFound(self.name)

            embed = hikari.Embed(
                title=f"Script '{script.name}'",
                description=f"```lua\n{script.code}\n```",
                color=CONFIG.theme,
            )
            await ctx.respond(embed=embed)
