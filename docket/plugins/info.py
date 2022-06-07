import crescent

from docket.plugins._group import docket_group

plugin = crescent.Plugin("info")


@plugin.include
@docket_group.child
@crescent.command(description="See the bot's ping.")
async def ping(ctx: crescent.Context) -> None:
    await ctx.respond(f"Ping is {round(ctx.app.heartbeat_latency*1000)}ms")
