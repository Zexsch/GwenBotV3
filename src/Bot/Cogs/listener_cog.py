from random import randint
from logging import Logger

import discord
from discord.ext import commands

from Database.database import DatabaseHandler
from Config.config import MESSAGE_CHANNEL, DEFAULT_CHANNEL, PREFIX, OWNER_ID


class ListenerCog(commands.Cog):
    def __init__(self, bot: commands.Bot, database: DatabaseHandler, logger: Logger):
        self.bot = bot
        self.database = database
        self.logger = logger
        
    @commands.Cog.listener("on_message")
    async def on_message(self, msg: discord.Message) -> None:
        """There can only be one on-message listener so you need to add all listen-related events in this function."""
        
        """Question mark counter""" 
        if msg.channel.id == MESSAGE_CHANNEL:

            if msg.content != '?':
                channel = self.bot.get_channel(DEFAULT_CHANNEL)
                if not '@' in msg.content:
                    self.logger.warning(f"User {msg.author.id} sent a non-question mark in the question mark channel.")
                    await channel.send(f'<@341238409311944705> <@281791015411646464> Somebody did a little fucky wuckie >.<!! A small oopsie woopsie uwu! Someone dared ruin the ? chain nya~!!! <@{msg.author.id}> what have you done!! (⁄ ⁄•⁄ω⁄•⁄ ⁄) They dared send "{msg.content}" in our holy channel nya!') # type: ignore
                else:
                    self.logger.warning(f"User {msg.author.id} sent a mention in the question mark channel.")
                    await channel.send(f'<@341238409311944705> <@281791015411646464> Somebody did a little fucky wuckie >.<!! A small oopsie woopsie uwu! Someone dared ruin the ? chain nya~!!! <@{msg.author.id}> what have you done!! (⁄ ⁄•⁄ω⁄•⁄ ⁄) They dared use an "@" in our holy channel nya!') # type: ignore
                return

            if self.database.fetch_latest_user() == msg.author.id:
                channel = self.bot.get_channel(DEFAULT_CHANNEL)
                await channel.send(f'<@341238409311944705> <@281791015411646464> Somebody did a little fucky wuckie >.<!! A small oopsie woopsie uwu! Someone dared ruin the ? chain nya~!!! <@{msg.author.id}> what have you done!! (⁄ ⁄•⁄ω⁄•⁄ ⁄) They dared send two ?s in a row nya!') # type: ignore
                return
            
            self.database.set_latest_user(msg.author.id)

            current = self.database.fetch_amount()
            current += 1
            self.database.set_amount(current)
            
        
        if PREFIX in msg.content:
            return
        
        if msg.guild is None:
            return
        
        """Make the bot send any message. Only usable by bot owner.
        sendshit (message)$(channel id)[optional]
        Trigger on-message, not a command.""" # pylint: disable=pointless-string-statement
        if msg.author.id == OWNER_ID and 'sendshit' in msg.content.lower():
            res: str = msg.content
            res = res.replace('sendshit','')
            channel = self.bot.get_channel(DEFAULT_CHANNEL)  # Default channel to send to. Change in Config.config.
            
            if "$" in msg.content:
                split = res.split("$",1)
                channel = self.bot.get_channel(int(split[1]))
                res = split[0]
                res = res.replace("$",'')
            
            self.logger.debug(f"Sent message '{res}' in channel {channel.id} by owner") # type: ignore
            await channel.send(res) # type: ignore
            return
    
        if 'gwen' in msg.content.lower():
            if not self.database.fetch_gwen_sub(msg.author.id, msg.guild.id) or msg.author == self.bot.user:
                return

            if self.database.fetch_quote(msg.guild.id):
                return
            
            ran_num: int = randint(0,99)
            
            if ran_num == 1:
                await msg.channel.send('Gwen is... not immune?')
                return
            
            await msg.channel.send('Gwen is immune.')
            return
        
        elif 'gw3n' in msg.content.lower():
            if not self.database.fetch_gwen_sub(msg.author.id, msg.guild.id) or msg.author == self.bot.user:
                return
            
            await msg.channel.send('Gwen is immune. You cannot escape.')
            return