from __future__ import annotations

import typing

import attrs
import hikari

from .lua_executor import execute_lua
from .lua_py_dict import LuaPyDict

BAD_ATTRS = ["app", "shard"]


def _middleware(
    function: typing.Callable[[hikari.Event], typing.Dict[str, typing.Any]]
) -> typing.Callable[[hikari.Event], None]:
    def inner(event: hikari.Event) -> None:
        data = function(event)
        # pretend this is the executor
        code = event.message.content  # type: ignore
        execute_lua(event.app, event.guild_id, code, LuaPyDict(data))  # type: ignore

    return inner


def _default_serialize(event: hikari.Event) -> typing.Dict[str, typing.Any]:
    return attrs.asdict(event, recurse=True, filter=_filter)


def _filter(attr: attrs.Attribute[typing.Any], value: typing.Any) -> bool:
    if attr.name.startswith("_") or attr.name in BAD_ATTRS:
        return False
    return True


@_middleware
def default(event: hikari.Event) -> typing.Dict[str, typing.Any]:
    return _default_serialize(event)
