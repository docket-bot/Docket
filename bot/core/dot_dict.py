from typing import Any


class DotDict(dict[str, Any]):
    def __getitem__(self, key: str) -> Any:
        val = super().__getitem__(key)
        if isinstance(val, dict):
            return DotDict(val)
        return val

    def __getattr__(self, key: str) -> Any:
        return self.__getitem__(key)

    def __setattr__(self, key: str, value: Any) -> None:
        self.__setitem__(key, value)

    def __delattr__(self, key: str) -> None:
        self.__delitem__(key)
