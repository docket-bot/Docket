from __future__ import annotations

import logging
from typing import Any

from apgorm import Database as BaseDB
from apgorm import Index, IndexType

from docket.config import CONFIG

from .models.event import EventTrigger, EventTriggerScript
from .models.guild import Guild
from .models.script import Script

_LOG = logging.getLogger(__name__)


class Database(BaseDB):
    guilds = Guild
    scripts = Script
    event_triggers = EventTrigger
    event_trigger_scripts = EventTriggerScript

    indexes = [
        # scripts
        Index(Script, Script.guild_id, IndexType.HASH),
        Index(Script, Script.name, IndexType.HASH),
        # event_triggers
        Index(EventTrigger, EventTrigger.guild_id, IndexType.HASH),
        Index(EventTrigger, EventTrigger.event_type, IndexType.HASH),
    ]

    def __init__(self) -> None:
        super().__init__("docket/database/migrations")

    async def connect(self, **_: Any) -> None:
        await super().connect(
            host=CONFIG.db_host,
            user=CONFIG.db_user,
            password=CONFIG.db_password,
            database=CONFIG.db_name,
        )

        if self.must_create_migrations():
            _LOG.info("Creating migrations...")
            self.create_migrations()
        if await self.must_apply_migrations():
            _LOG.info("Applying migrations...")
            await self.apply_migrations()
