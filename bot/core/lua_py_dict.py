from typing import Any

MAX_LUA_INT = 982688721935675392


class LuaPyDict(dict[str, Any]):
    def __getitem__(self, key: str) -> Any:
        val = super().__getitem__(key)
        if isinstance(val, dict):
            return LuaPyDict(val)
        if isinstance(val, int) and val > MAX_LUA_INT:
            return str(val)
        return val

    def __getattr__(self, key: str) -> Any:
        return self.__getitem__(key)

    def __setattr__(self, key: str, value: Any) -> None:
        self.__setitem__(key, value)

    def __delattr__(self, key: str) -> None:
        self.__delitem__(key)
