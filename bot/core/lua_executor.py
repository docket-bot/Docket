from __future__ import annotations

import threading
from typing import Any, TYPE_CHECKING

from .dot_dict import DotDict
from . import callbacks

if TYPE_CHECKING:
    from bot.bot import Bot

INITIAL_LUA = "function (code, env) load(code, nil, nil, env)() end"


def get_env(bot: Bot, guild: int) -> dict[str, Any]:
    return {"send_message": callbacks.send_message(bot, guild)}


def execute_lua(
    bot: Bot, guild: int, code: str, runtime: Any, ctx: DotDict
) -> None:
    thread = threading.Thread(
        target=_execute_lua, args=(bot, guild, code, runtime, ctx)
    )
    thread.start()


def _execute_lua(
    bot: Bot, guild: int, code: str, runtime: Any, ctx: DotDict
) -> Any:
    lua_func = runtime.eval(INITIAL_LUA)
    env = get_env(bot, guild)
    env["ctx"] = ctx
    return lua_func(code, env)
