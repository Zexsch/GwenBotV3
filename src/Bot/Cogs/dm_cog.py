import discord

from discord.ext import commands

from Bot.winrate_fetcher import WinrateFetcher
from Config.help_message import HELPMESSAGE, WRHELPMESSAGE

class DMCog(commands.Cog):
    def __init__(self, bot: commands.Bot, winrate_fetcher: WinrateFetcher):
        self.bot = bot
        self.winrate_fetcher = winrate_fetcher
        
    @commands.command()
    async def list(self, ctx: commands.Context):
        user: discord.Member | discord.User = ctx.message.author
        await user.send(', '.join(map(str, self.winrate_fetcher.all_champions)))
    
    @commands.command()
    async def elolist(self, ctx: commands.Context):
        user: discord.Member | discord.User = ctx.message.author
        await user.send(', '.join(map(str,self.winrate_fetcher.elo_list)))
        
    @commands.command(aliases=['roles', 'role', 'rolelist'])
    async def role_list(self, ctx: commands.Context):
        user: discord.Member | discord.User = ctx.message.author
        await user.send(', '.join(map(str, self.winrate_fetcher.role_list)))
    
    #  Change the strings in helpmsg.py to edit the help messages.
    @commands.command(aliases=['Menu'])
    async def help(self, ctx: commands.Context):
        user: discord.Member | discord.User = ctx.message.author
        await user.send(HELPMESSAGE)
    
    @commands.command(aliases=['wrhelp'])
    async def winratehelp(self, ctx: commands.Context):
        user: discord.Member | discord.User = ctx.message.author
        await user.send(WRHELPMESSAGE)