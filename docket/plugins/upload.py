import crescent
import hikari
import yaml
from yaml.scanner import ScannerError

plugin = crescent.Plugin("commands")


@plugin.include
@crescent.catch_command(IndexError)
async def handle_index_error(error: IndexError, ctx: crescent.Context) -> None:
    await ctx.respond(
        "When uploading messages with code blocks you must have 2 code blocks.",
        ephemeral=True,
    )


@plugin.include
@crescent.catch_command(ScannerError)
async def handle_yaml_error(error: ScannerError, ctx: crescent.Context) -> None:
    await ctx.respond(
        "There was an error parsing your config:"
        "```"
        f"{error.problem_mark}\n{error.problem}"
        "```",
        ephemeral=True,
    )


@plugin.include
@crescent.message_command
async def upload(ctx: crescent.Context, message: hikari.Message) -> None:
    if not message.content:
        await ctx.respond(
            "This message is empty or Docket can not see message content on"
            "this server.",
            ephemeral=True,
        )
        return

    code_block_count = int(len(message.content.split("```")) / 2)

    if code_block_count <= 1:
        # Must be using a single code block with yaml in the comments.

        lua_list = message.content.splitlines()
        yaml_list = list()

        if len(lua_list) <= 2:
            await ctx.respond("This code block is empty.", ephemeral=True)
            return

        if lua_list[0] in "```lua":
            lua_list.pop(0)
        if lua_list[-1] == "```":
            lua_list.pop(-1)

        while (next_line := lua_list.pop(0)).strip().startswith("--"):
            yaml_list.append(next_line[2:])

        lua_content = "\n".join(lua_list)
        yaml_content = "\n".join(yaml_list)
    else:
        # Must be using 2 code blocks.
        # 1st is yaml, second is lua.

        split = (
            message.content.replace("```yaml", "```")
            .replace("```lua", "```")
            .split("```")
        )

        yaml_content = split[1]
        lua_content = split[3]

    data = yaml.safe_load(yaml_content)
    lua = lua_content

    # Temporary
    await ctx.respond(f"```yaml\n{data}\n``````lua\n{lua}\n```", ephemeral=True)
