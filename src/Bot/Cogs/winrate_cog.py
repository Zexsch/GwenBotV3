from logging import Logger

from discord.ext import commands

from Bot.models import Champion
from Bot.winrate_fetcher import WinrateFetcher

from Config.config import OWNER_ID

class WinrateCog(commands.Cog):
    def __init__(self, bot: commands.Bot, winrate_fetcher: WinrateFetcher, logger: Logger):
        self.bot = bot
        self.winrate_fetcher = winrate_fetcher
        self.logger = logger
        
        self.beautified_elo_list: dict[str, str] = {'platinum_plus' : 'Plat+',
                                                    'diamond_2_plus' : 'D2+',
                                                    'diamond_plus' : 'D+',
                                                    'master_plus' : "M+",
                                                    }
        
    @commands.command(aliases=['winrate'])
    async def wr(self, ctx: commands.Context, champion_name: str, *args: str) -> None:
        self.logger.debug(f"Calling winrate in channel {ctx.channel.id} for champion {champion_name} with arguments {args}")
        
        champ = Champion(name=champion_name)
        result = self.winrate_fetcher.get_stats(champ, args)
        
        if not result.win_rate:
            await ctx.send(f"Oh no! Seems like Gwen ran into some issues whilst fetching the winrate! Are you sure that there's enough matches played?")
            self.logger.critical(f"GwenBot was unable to fetch the winrate for champion {champion_name} with arguments {args} in channel {ctx.channel.id}")
            return
        
        if result.champ.role:
            if result.champ.elo:
                result.champ.beautify_elo(self.beautified_elo_list)
                await ctx.send(f"{result.champ.name.capitalize()} has a {result.win_rate} winrate in {result.champ.elo} in {result.champ.role}{result.final_string}.")
                return
            
            await ctx.send(f"{result.champ.name.capitalize()} has a {result.win_rate} winrate in {result.champ.role}{result.final_string}.")
            return
        
        if result.champ.elo:
                result.champ.beautify_elo(self.beautified_elo_list)
                await ctx.send(f"{result.champ.name.capitalize()} has a {result.win_rate} winrate in {result.champ.elo}{result.final_string}.")
                return
            
        await ctx.send(f"{result.champ.name.capitalize()} has a {result.win_rate} winrate{result.final_string}.")