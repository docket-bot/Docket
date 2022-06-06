from __future__ import annotations


class DocketBaseError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
