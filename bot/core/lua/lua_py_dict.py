from __future__ import annotations

from typing import Any

# Lua will automatically convert integers that are greater than 32 bits to
# floats. To deal with inaccuracies caused by this, integers above 32 bits
# are converted to strings.
MAX_LUA_INT = 2**32


class LuaPyDict(dict):  # type: ignore
    def __getitem__(self, key: str) -> Any:
        val = super().__getitem__(key)
        if isinstance(val, dict):
            return LuaPyDict(val)
        if isinstance(val, int) and val > MAX_LUA_INT:
            return str(val)
        return val
