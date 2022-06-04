import crescent

from bot.config import CONFIG


class Bot(crescent.Bot):
    def __init__(self) -> None:
        super().__init__(token=CONFIG.discord_token)

        self.plugins.load("bot.plugins.info")
        self.plugins.load("bot.plugins.events")
