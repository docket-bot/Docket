from __future__ import annotations

import asyncio
from time import sleep
from typing import Any, Awaitable, Generic, TypeVar

from docket.undefined import UNDEF

_T = TypeVar("_T")


class Callback(Generic[_T]):
    def __init__(self, manager: SyncAsync, awaitable: Awaitable[_T]) -> None:
        self.awaitable = awaitable
        self.manager = manager
        self.response: _T | UNDEF = UNDEF.UNDEF
        self.error: Exception | None = None

    async def complete(self) -> None:
        try:
            ret = await self.awaitable
        except Exception as e:
            self.error = e
        else:
            self.response = ret

    def sync_wait(self) -> None:
        while self.response is UNDEF.UNDEF and self.error is None:
            sleep(0.1)


class SyncAsync:
    def __init__(self) -> None:
        self.callbacks: list[Callback[Any]] = []

    async def complete_callbacks_loop(self) -> None:
        while True:
            if not self.callbacks:
                await asyncio.sleep(0.1)
                continue

            callbacks = self.callbacks.copy()
            self.callbacks.clear()
            await asyncio.gather(
                *[cb.complete() for cb in callbacks], return_exceptions=True
            )

    def sync_call(self, awaitable: Awaitable[_T]) -> _T:
        cb = Callback(self, awaitable)
        self.callbacks.append(cb)
        cb.sync_wait()
        if cb.error is not None:
            raise cb.error
        assert cb.response is not UNDEF.UNDEF
        return cb.response
