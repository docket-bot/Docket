from __future__ import annotations

from typing import Any

import attrs


BAD_ATTRS = [
    "app",
    "shard",
]


def filter(attr: attrs.Attribute[Any], value: Any) -> bool:
    if attr.name.startswith("_"):
        return False
    if attr.name in BAD_ATTRS:
        return False
    return True


async def handle_event(
    event: object,
) -> None:
    data = attrs.asdict(
        event,
        recurse=True,
        filter=filter,
    )
    print(data)
