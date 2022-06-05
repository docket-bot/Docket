from __future__ import annotations

import time
import asyncio
from typing import Any, TYPE_CHECKING

import lupa
from .dot_dict import DotDict
from . import callbacks

if TYPE_CHECKING:
    from bot.bot import Bot

INITIAL_LUA = "function (code, env) load(code, nil, nil, env)() end"
SAFE_BUILTINS = ["tostring"]


def get_env(bot: Bot, runtime: Any, guild: int) -> dict[str, Any]:
    return {
        # callbacks
        "send_message": callbacks.send_message(bot, guild),
        "sleep": time.sleep,
    } | {
        # builtins
        name: runtime.eval(name)
        for name in SAFE_BUILTINS
    }


def execute_lua(
    bot: Bot, guild: int, code: str, ctx: DotDict
) -> None:
    asyncio.get_event_loop().run_in_executor(
        None, _execute_lua, bot, guild, code, ctx
    )


def _execute_lua(
    bot: Bot, guild: int, code: str, ctx: DotDict
) -> Any:
    runtime = lupa.LuaRuntime()
    lua_func = runtime.eval(INITIAL_LUA)
    env = get_env(bot, runtime, guild)
    env["ctx"] = ctx
    return lua_func(code, env)
