from logging import Logger

from discord.ext import commands

from Bot.models import Champion, WinrateNotFoundException
from Bot.winrate_fetcher import WinrateFetcher
from request import FailedRequest

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
        
        self.current_patch = ".".join(self.winrate_fetcher.patch_version.split(".")[:-1])
        
    @commands.command(aliases=['winrate'])
    async def wr(self, ctx: commands.Context, champion_name: str, *args: str) -> None:
        self.logger.debug(f"Calling winrate in channel {ctx.channel.id} for champion {champion_name} with arguments {args}")
        
        champ = Champion(name=champion_name)
        
        try:
            result = self.winrate_fetcher.get_stats(champ, args)
        except FailedRequest as e:
            await ctx.send(f"Oh no! Seems like Gwen was unable to fetch u.gg! Is it currently down?")
            self.logger.critical(f"Request failed with exception {e}")
            return
        except WinrateNotFoundException:
            await ctx.send(f"Oh no! Seems like Gwen ran into some issues whilst fetching the winrate! Are you sure that there's enough matches played?")
            self.logger.critical(f"GwenBot was unable to fetch the winrate for champion {champion_name} with arguments {args} in channel {ctx.channel.id}")
            return
        
        if champ.patch:
            minor_patch = self.winrate_fetcher.patch_minor_version
            
                
            try:
                if champ.patch and (int(champ.patch[-2:]) < int(minor_patch) - 5):
                    await ctx.send(f"Gwen can only gets stats for the past 5 patches! The current patch is {self.current_patch}.")
                    return
            except ValueError:
                if champ.patch and (int(champ.patch[-1:]) < int(minor_patch) - 5):
                    await ctx.send(f"Gwen can only gets stats for the past 5 patches! The current patch is {self.current_patch}.")
                    return
            
        if result.champ.elo:
            result.champ.beautify_elo(self.beautified_elo_list)
            
        message: list[str] = [f"{result.champ.name.capitalize()} has a {result.win_rate} winrate"]
        
        if result.champ.elo:
            message.append(f"in {result.champ.elo}")
            
        if result.champ.role:
            message.append(f"in {result.champ.role}")
            
        message.append(result.final_string)
        
        if result.champ.patch:
            message.append(result.champ.patch)
            
        message.append('.')
        
        await ctx.send(" ".join(p for p in message if p))
    
    @commands.command(aliases=['checkver', 'patch'])
    async def version(self, ctx: commands.Context):
        await ctx.send(f'Currently on league patch {self.current_patch}.')