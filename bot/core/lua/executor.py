from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import lupa

from bot.core.lua import callbacks
from bot.core.lua.lua_py_dict import LuaPyDict

if TYPE_CHECKING:
    from bot.bot import Bot

INITIAL_LUA = "function (code, env) pcall(load(code, nil, 't', env)) end"
SAFE_BUILTINS = ["tostring", "tonumber", "math"]


def get_env(bot: Bot, runtime: Any, guild: int) -> dict[str, Any]:
    env = {
        # callbacks
        "send_message": callbacks.send_message(bot, guild)
    }
    env.update(
        {
            # builtins
            name: runtime.eval(name)
            for name in SAFE_BUILTINS
        }
    )
    return env


def execute_lua(bot: Bot, guild: int, code: str, ctx: LuaPyDict) -> None:
    asyncio.get_event_loop().run_in_executor(None, _execute_lua, bot, guild, code, ctx)


def _execute_lua(bot: Bot, guild: int, code: str, ctx: LuaPyDict) -> Any:
    runtime = lupa.LuaRuntime()
    lua_func = runtime.eval(INITIAL_LUA)
    env = get_env(bot, runtime, guild)
    env["ctx"] = ctx
    return lua_func(code, env)
