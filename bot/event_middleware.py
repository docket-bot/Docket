from __future__ import annotations

import typing
import hikari
import attrs

BAD_ATTRS = ["app", "shard"]


def _middleware(
    function: typing.Callable[[hikari.Event], typing.Dict[str, typing.Any]]
):
    def inner(event: hikari.Event):
        data = function(event)
        # Pretend this is the event handler
        print(data)

    return inner


def _default_serialize(event: hikari.Event):
    return attrs.asdict(event, recurse=True, filter=filter)


def filter(attr: attrs.Attribute[typing.Any], value: typing.Any) -> bool:
    if attr.name.startswith("_") or attr.name in BAD_ATTRS:
        return False
    return True


@_middleware
def default(event: hikari.Event):
    return _default_serialize(event)


@_middleware
def handle_guild_typing_event(event: hikari.GuildTypingEvent):
    return _default_serialize(event)
