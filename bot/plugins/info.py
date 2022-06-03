import crescent

plugin = crescent.Plugin("info")


@plugin.include
@crescent.command(description="See the bot's ping.")
async def ping(ctx: crescent.Context):
    await ctx.respond(f"Ping is {round(ctx.app.heartbeat_latency*1000)}ms")
