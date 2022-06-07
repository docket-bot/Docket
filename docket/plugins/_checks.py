from __future__ import annotations

from typing import Awaitable, Callable, cast

import crescent
import hikari

from docket.errors import DocketBaseError


def has_guild_perms(
    perms: hikari.Permissions,
) -> Callable[[crescent.Context], Awaitable[crescent.HookResult | None]]:
    async def inner_hook(ctx: crescent.Context) -> crescent.HookResult | None:
        if not ctx.member:
            raise DocketBaseError("This command is guild-only.")

        assert isinstance(member := ctx.member, hikari.InteractionMember)

        if perms not in member.permissions:
            await ctx.respond(
                "You are missing the following permissions, required to use this "
                "command:\n"
                "-".join(
                    cast(str, perm.name)
                    for perm in (perms - member.permissions).split()
                ),
                ephemeral=True,
            )
            return crescent.HookResult(exit=True)

        return None

    return inner_hook
