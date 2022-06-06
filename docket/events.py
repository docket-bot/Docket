from __future__ import annotations

import hikari

EVENT_MAP: dict[type[hikari.Event], int] = {hikari.GuildMessageCreateEvent: 1}
EVENT_ID_MAP: dict[int, type[hikari.Event]] = {v: k for k, v in EVENT_MAP.items()}
