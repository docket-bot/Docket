from __future__ import annotations


class DocketBaseError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ScriptNotFound(DocketBaseError):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Script '{name}' not found.")
