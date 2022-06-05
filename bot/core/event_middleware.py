from __future__ import annotations

import typing

import hikari

from .lua.executor import execute_lua
from .lua.lua_py_dict import LuaPyDict
from .serialize import serialize


def _middleware(
    function: typing.Callable[[hikari.Event], typing.Dict[str, typing.Any]]
) -> typing.Callable[[hikari.Event], None]:
    def inner(event: hikari.Event) -> None:
        data = function(event)
        # pretend this is the executor
        code = event.message.content  # type: ignore
        execute_lua(event.app, event.guild_id, code, LuaPyDict(data))  # type: ignore

    return inner


@_middleware
def default(event: hikari.Event) -> typing.Dict[str, typing.Any]:
    return serialize(event)
