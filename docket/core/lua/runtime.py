from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Any, NoReturn

import lupa

from docket.config import CONFIG
from docket.core.lua import callbacks
from docket.core.lua.lua_py_dict import LuaPyDict

if TYPE_CHECKING:
    from docket.bot import Docket


with open(Path("docket/core/lua/boot.lua"), "r") as f:
    LUA_BOOT = f.read()
LUA_WHITELIST: list[str] = []


def _getter(obj: object, key: str) -> Any:
    if isinstance(obj, dict) and key in obj:
        return obj[key]
    raise AttributeError(f"access denied for {key}")


def _setter(obj: object, key: str, value: Any) -> NoReturn:
    raise AttributeError(f"access denied for {key}")


class LuaManager:
    def __init__(self, bot: Docket) -> None:
        self.bot = bot
        self.runtimes: dict[int, tuple[lupa.LuaRuntime, Any]] = {}

    def execute(
        self, guild_id: int, script_id: int, source: str, ctx: LuaPyDict
    ) -> None:
        asyncio.get_event_loop().run_in_executor(
            None, self._execute, guild_id, script_id, source, ctx
        )

    def _execute(
        self, guild_id: int, script_id: int, source: str, ctx: LuaPyDict
    ) -> None:
        lua, boot = self._prepare_runtime(guild_id, script_id, source)
        boot.call(ctx)

    def _make_env(self, guild_id: int) -> dict[str, Any]:
        return {"send_message": callbacks.send_message(self.bot, guild_id)}

    def _prepare_runtime(
        self, guild_id: int, script_id: int, source: str
    ) -> tuple[lupa.LuaRuntime, Any]:
        # this function was adapted from code provided by the dev of cleanerbot.xyz,
        # which permission
        if script_id in self.runtimes:
            return self.runtimes[script_id]

        lua = lupa.LuaRuntime(
            unpack_returned_tuples=True,
            register_eval=False,
            register_builtins=False,
            attribute_handlers=(_getter, _setter),
            # max_memory=max_memory,
        )
        boot = lua.execute(LUA_BOOT)
        lua_globals = lua.globals()
        for key in tuple(lua_globals):
            if key not in LUA_WHITELIST:
                del lua_globals[key]
        for k, v in self._make_env(guild_id).items():
            lua_globals[k] = v

        try:
            boot.set_cycle_limit(CONFIG.max_cycles)
            boot.set_script(source)
        except lupa.LuaError as e:
            raise RuntimeError(
                f"error during booting worker {guild_id}-{script_id}"
            ) from e

        self.runtimes[script_id] = (lua, boot)
        return lua, boot
