from __future__ import annotations

from typing import Any


class LuaPyDict(dict):  # type: ignore
    def __getitem__(self, key: str) -> Any:
        val = super().__getitem__(key)
        if isinstance(val, dict):
            return LuaPyDict(val)
        if isinstance(val, int):
            return str(val)
        return val
