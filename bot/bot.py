import crescent

from bot.config import CONFIG


class Bot(crescent.Bot):
    def __init__(self):
        super().__init__(token=CONFIG.DISCORD_TOKEN)

        self.plugins.load("bot.plugins.info")
