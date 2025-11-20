from discord.ext import commands
from logging import Logger

from Database.database import DatabaseHandler

class GwensubCog(commands.Cog):
    def __init__(self, bot: commands.Bot, database: DatabaseHandler, logger: Logger):
        self.bot = bot
        self.database = database
        self.logger = logger
        
    @commands.command(name='GwenAdd', aliases=['add'])
    async def gwen_add(self, ctx: commands.Context) -> None:
        """Command to add user to the subscribed database"""
        
        if ctx.guild is None:
            await ctx.send('Command must be used in a server.')
            return
        
        if self.database.fetch_blacklist(ctx.author.id, ctx.guild.id):
            await ctx.send('You are blacklisted from using this function.')
            return
        
        if self.database.fetch_quote(ctx.guild.id):
            await ctx.send('The server has blocked this function.')
            return
        
        if not self.database.fetch_gwen_sub(ctx.author.id, ctx.guild.id):
            self.database.add_to_gwen_sub(ctx.author.id, ctx.guild.id)
            await ctx.send('Successfully subscribed to GwenBot.')
            self.logger.debug(f"Added user {ctx.author.id} to GwenSubs in guild {ctx.guild.id}") # type: ignore
            return
        
        await ctx.send('You are already subscribed to GwenBot.')
        
    
    @commands.command(name='remove', aliases=['gwenremove', 'Gwenremove', 'rem', 'removesub'])
    async def gwen_remove(self, ctx: commands.Context) -> None:
        """Command to remove user from the subscribed database"""
        
        if ctx.guild is None:
            await ctx.send('Command must be used in a server.')
            return
        
        if self.database.fetch_gwen_sub(ctx.author.id, ctx.guild.id):
            self.database.remove_from_gwen_sub(ctx.author.id, ctx.guild.id)
            await ctx.send('Successfully removed from the GwenBot Subscription.')
            self.logger.debug(f"Removed user {ctx.author.id} from GwenSubs in guild {ctx.guild.id}") # type: ignore
            return
        
        await ctx.send('You are not currently subscribed to GwenBot.', ephemeral=True)
        
    
    @commands.command(name='checkgs', aliases=['checksub'])
    async def checkgs(self, ctx: commands.Context, user_id: str | int | None = None) -> None:
        """Command to check if a user is subbed. +checkgs id[optional]"""
        
        if ctx.guild is None:
            await ctx.send('Command must be used in a server.')
            return
        
        if user_id is None:
            if self.database.fetch_gwen_sub(ctx.author.id, ctx.guild.id):
                await ctx.send('You are subscribed.')
                return
            await ctx.send('You are not subscribed.')
            return
            
        try:
            user_id = int(user_id) # Type: ignore
        except ValueError:
            if len(ctx.message.mentions) == 0:
                await ctx.send('Invalid id...', ephemeral=True)
                return
            
            user_id = ctx.message.mentions[0].id
            
        if self.database.fetch_gwen_sub(user_id, ctx.guild.id):
            await ctx.send("User is subscribed.")
            return
        await ctx.send("User is not subscribed.")
        

    @commands.has_permissions(kick_members=True)    
    @commands.command(name='quote')
    async def quote(self, ctx: commands.Context) -> None:
        """Command to add/undo Quote"""
        
        if ctx.guild is None:
            await ctx.send('Command must be used in a server.')
            return
        
        if self.database.fetch_quote(ctx.guild.id):
            self.database.remove_from_quote(ctx.guild.id)
            await ctx.send('Gwen will now respond to chat.')
            self.logger.warning(f"Removed quote from guild {ctx.guild.id}")
            return
        
        self.database.add_to_quote(ctx.guild.id)
        self.logger.warning(f"Enabled quote in guild {ctx.guild.id}")
        await ctx.send('Gwen will no longer respond to chat.')
        
        
    @commands.command(name='modremove')
    @commands.has_permissions(kick_members=True)
    async def removesubmod(self, ctx: commands.Context, user_id) -> None:
        """Command to forcefully remove a user from the GwenBot subscription.
        Usable only by users with kick_members permissions."""
        
        if ctx.guild is None:
            await ctx.send('Command must be used in a server.')
            return
        
        try: 
            id = int(user_id)
        except ValueError:
            if len(ctx.message.mentions) == 0:
                await ctx.send('Invalid id...', ephemeral=True)
                return
            
            id = ctx.message.mentions[0].id
        
        if not self.database.fetch_gwen_sub(id, ctx.guild.id):
            await ctx.send('User is not subscribed to GwenBot.')
            return
        
        self.database.remove_from_gwen_sub(id, ctx.guild.id)
        self.logger.debug(f"Forcefully removed user {user_id} from GwenSub in guild {ctx.guild.id} by {ctx.author.id}")
        await ctx.send('User removed from GwenBot subscription.')
        
        
    @commands.command(name='blacklist', aliases=['bl', 'Bl', 'BL'])
    @commands.has_permissions(kick_members=True)
    async def blacklist(self, ctx: commands.Context, user_id) -> None:
        """Command to add a user to the blacklist. Requires the user to have kick_members permissions."""
        
        if ctx.guild is None:
            await ctx.send('Command must be used in a server.')
            return
        
        try:
            user_id = int(user_id)
        except ValueError:
            if len(ctx.message.mentions) == 0:
                await ctx.send('Invalid id...', ephemeral=True)
                return
            
            user_id = ctx.message.mentions[0].id
        
        if not self.database.fetch_blacklist(user_id, ctx.guild.id):
            self.database.add_to_blacklist(user_id, ctx.guild.id)
            self.database.remove_from_gwen_sub(user_id, ctx.guild.id)
            await ctx.send('User successfully added to the Blacklist.')
            self.logger.debug(f"Blacklisted user {user_id} from GwenSub in guild {ctx.guild.id} by {ctx.author.id}")
            return
        
        
        await ctx.send('User is already in blacklist.')
        
    
    @commands.command(name='blremove', aliases=['blr', 'blacklistremove', 'unblacklist', 'unbl'])
    @commands.has_permissions(kick_members=True)
    async def blremove(self, ctx: commands.Context, user_id) -> None:
        """Command to remove a user from the blacklist. Requires the user to have kick_members permissions."""
        
        if ctx.guild is None:
            await ctx.send('Command must be used in a server.')
            return
    
        try:
            user_id = int(user_id)
        except ValueError:
            if len(ctx.message.mentions) == 0:
                await ctx.send('Invalid id...', ephemeral=True)
                return
            
            user_id = ctx.message.mentions[0].id
        
        if self.database.fetch_blacklist(user_id, ctx.guild.id):
            self.database.remove_from_blacklist(user_id, ctx.guild.id)
            await ctx.send('User successfully removed from the Blacklist.')
            self.logger.debug(f"Removed user {user_id} from blacklist in guild {ctx.guild.id} by {ctx.author.id}")
            return
        
        await ctx.send('User is not Blacklisted.')
        
    
    @commands.command(name='checkbl', aliases=['check', 'checkblacklist'])
    async def checkbl(self, ctx: commands.Context, user_id=None) -> None:
        """Command to check if a user is blacklisted. +checkbl id[optional]"""
        
        if ctx.guild is None:
            await ctx.send('Command must be used in a server.')
            return
        
        if user_id == None:
            if self.database.fetch_blacklist(ctx.author.id, ctx.guild.id):
                await ctx.send('You are Blacklisted.')
                return
            await ctx.send('You are not Blacklisted.')
            return

        try:
            user_id = int(user_id)
        except ValueError:
            if len(ctx.message.mentions) == 0:
                await ctx.send('Invalid id...', ephemeral=True)
                return
            
            user_id = ctx.message.mentions[0].id
        
        if self.database.fetch_blacklist(user_id, ctx.guild.id):
            await ctx.send('User is Blacklisted.')
            return
        await ctx.send('User is not Blacklisted.')
        
    
    #  To add any permissions command error:
    #  Add @commands.has_permissions(permissions) before the command. Then add:
    #  @command.error
    #  To this command.
    
    @quote.error
    @removesubmod.error
    @blremove.error
    @blacklist.error
    async def _error(self, ctx: commands.Context, error) -> None:
        """Run if a user does not have the permissions necessary to run a command."""
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('You do not have the permissions to use this command.')