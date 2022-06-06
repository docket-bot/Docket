from __future__ import annotations

import crescent
from apgorm.exceptions import InvalidFieldValue

from docket.errors import DocketBaseError, ScriptNotFound

plugin = crescent.Plugin("error-handling")


@plugin.include
@crescent.catch_command(DocketBaseError, ScriptNotFound, InvalidFieldValue)
async def base_error(
    error: DocketBaseError | InvalidFieldValue, ctx: crescent.Context
) -> None:
    await ctx.respond(error.message, ephemeral=True)
