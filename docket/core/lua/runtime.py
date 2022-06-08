from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, NoReturn

import lupa

from docket.config import CONFIG
from docket.core.lua import callbacks
from docket.core.lua.lua_py_dict import LuaPyDict

if TYPE_CHECKING:
    from docket.bot import Docket


# LUA_BOOT was provided by the developer of cleanerbot.xyz, with permission
LUA_BOOT = """
local debug_sethook = debug.sethook
local coroutine = coroutine
local error = error
local setmetatable = setmetatable
local unpack = unpack or table.unpack
local script, cycle_limit
local load = load
local pairs = pairs
local type = type
_G.load = function(chunk, chunkname, mode, env)
    if mode ~= "t" then return nil, "mode must be 't'" end
    return load(chunk, chunkname, "t", env)
end
local function safe_call(fn, ...)
    if cycle_limit == nil then
        error("no cycle limit, call set_cycle_limit")
    end
    local coro = coroutine.create(fn)
    local limit_exceeded = false
    debug_sethook(coro, function()
        limit_exceeded = true
        debug_sethook(function() error("reached cycle limit") end, "cr", 1)
        error("reached cycle limit")
    end, "", cycle_limit)
    local result = {coroutine.resume(coro, ...)}
    if limit_exceeded then
        error("reached cycle limit")
    end
    for _, v in pairs(result) do
        if type(v) == "table" then
            setmetatable(v, {})
        end
    end
    if not result[1] then
        error(unpack(result, 2))
    end
    return unpack(result, 2)
end
return {
    set_cycle_limit = function(limit)
        cycle_limit = limit
    end,
    set_script = function(source)
        local fn, err = load(source, "<worker>", "t")
        if fn == nil then
            error(err)
        end
        script = safe_call(fn)
    end,
    call = function(...)
        return safe_call(script, ...)
    end,
}
"""

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
        return {
            "send_message": callbacks.send_message(self.bot, guild_id),
            "print": print,
        }

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
