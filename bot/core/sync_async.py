from __future__ import annotations

import asyncio
from time import sleep
from typing import Any, Awaitable, Generic, TypeVar

_T = TypeVar("_T")


class Callback(Generic[_T]):
    def __init__(self, manager: SyncAsync, awaitable: Awaitable[_T]) -> None:
        self.awaitable = awaitable
        self.manager = manager
        self.responded: bool = False
        self.response: _T

    async def complete(self) -> None:
        self.set_result(await self.awaitable)

    def set_result(self, result: _T) -> None:
        self.response = result
        self.responded = True

    def sync_wait(self) -> None:
        while not self.responded:
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
                *[cb.complete() for cb in callbacks],
                return_exceptions=True,
            )

    def sync_call(self, awaitable: Awaitable[_T]) -> _T:
        cb = Callback(self, awaitable)
        self.callbacks.append(cb)
        cb.sync_wait()
        return cb.response
