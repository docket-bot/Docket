import asyncio
from typing import Any

import crescent

from docket.config import CONFIG
from docket.core.sync_async import SyncAsync


class Docket(crescent.Bot):
    def __init__(self) -> None:
        super().__init__(token=CONFIG.discord_token)

        self.plugins.load("docket.plugins.info")
        self.plugins.load("docket.plugins.events")

        self.sync_async = SyncAsync()

    async def start(self, *args: Any, **kwargs: Any) -> None:
        self.sync_async_task = asyncio.create_task(
            self.sync_async.complete_callbacks_loop()
        )
        return await super().start(*args, **kwargs)
