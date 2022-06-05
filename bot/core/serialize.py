from __future__ import annotations

from typing import Any

import attrs

BAD_ATTRS = ["app", "shard"]


def serialize(event: object) -> dict[str, Any]:
    return attrs.asdict(event, recurse=True, filter=_filter)


def _filter(attr: attrs.Attribute[Any], value: Any) -> bool:
    if attr.name.startswith("_") or attr.name in BAD_ATTRS:
        return False
    return True
