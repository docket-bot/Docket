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
        self.errored: bool = False
        self.response: _T
        self.exc: Exception

    async def complete(self) -> None:
        try:
            ret = await self.awaitable
        except Exception as e:
            self.set_error(e)
        else:
            self.set_result(ret)

    def set_result(self, result: _T) -> None:
        self.response = result
        self.responded = True

    def set_error(self, exc: Exception) -> None:
        self.exc = exc
        self.errored = True

    def sync_wait(self) -> None:
        while not (self.responded or self.errored):
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
        if cb.errored:
            raise cb.exc
        return cb.response
