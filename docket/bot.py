import asyncio
from typing import Any

import crescent

from docket.config import CONFIG
from docket.core.sync_async import SyncAsync
from docket.database.database import Database


class Docket(crescent.Bot):
    def __init__(self) -> None:
        super().__init__(token=CONFIG.discord_token)

        self.plugins.load("docket.plugins.info")
        self.plugins.load("docket.plugins.events")
        self.plugins.load("docket.plugins.config")

        self.sync_async = SyncAsync()
        self.database = Database()

    async def start(self, *args: Any, **kwargs: Any) -> None:
        self.sync_async_task = asyncio.create_task(
            self.sync_async.complete_callbacks_loop()
        )
        await self.database.connect()
        return await super().start(*args, **kwargs)

    async def join(self, until_close: bool = True) -> None:
        try:
            await super().join(until_close)
        finally:
            await self.database.cleanup()
