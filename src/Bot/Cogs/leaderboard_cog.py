#import gc

from discord.ext import commands

from Database.database import DatabaseHandler
from Config.config import MESSAGE_CHANNEL, OWNER_ID

class LeaderboardCog(commands.Cog):
    def __init__(self, bot: commands.Bot, database: DatabaseHandler):
        self.bot = bot
        self.database = database
        
    @commands.command(aliases=['question', 'amount', 'qm', 'qms', 'questionmarks', 'questionmark', '?'])
    async def questions(self, ctx: commands.Context):
        await ctx.send(f'The current amount of question marks is {self.database.fetch_amount()}.')


    @commands.command(aliases=['question_user', 'amount_user', 'qm_user', 'qms_user', 'questionmarks_user', 'questionmark_user', '?_u', '?u'])
    async def questions_user(self, ctx: commands.Context, id):
        await ctx.send(f"Command is currently being reworked. Please be patient as I work on making it not bad...")
        #
        #try:
        #    id = int(id)
        #except ValueError:
        #    if len(ctx.message.mentions) == 0:
        #        await ctx.send('Invalid id...', ephemeral=True)
        #        return
        #    else:
        #        id = ctx.message.mentions[0].id
        #
        #count = 0
        #await ctx.send('Fetching the amount of question marks. This may take a while.')
        #async for message in self.bot.get_channel(MESSAGE_CHANNEL).history(limit=None): #type: ignore
        #    if message.author.id == id:
        #        count += 1
        #
        #await ctx.send(f'The current amount of question marks by <@{id}> is {count}.')

    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx: commands.Context):
        await ctx.send(f"Command is currently being reworked. Please be patient as I work on making it not bad...")
        #await ctx.send('Fetching the leaderboard. This may take a while.')
        
        #user_dict: dict[int, int] = {}
        #
        #async for message in self.bot.get_channel(MESSAGE_CHANNEL).history(limit=None): #type: ignore
        #    if not (message.author.id in user_dict.keys()):
        #        user_dict[message.author.id] = 1
        #    else:
        #        user_dict[message.author.id] += 1
        #
        #ordered_dict = {k: v for k, v in sorted(user_dict.items(), key=lambda item: item[1], reverse=True)}
        #del user_dict
        #
        #user_list = []
        #count = 0
        #for key, value in ordered_dict.items():
        #    count += 1
        #    user_list.append([(await self.bot.fetch_user(key)).display_name, value])
        #
        #    if count >= 10:
        #        break
        #
        #del ordered_dict
        #await ctx.send(f"""1. {user_list[0][0]} with {user_list[0][1]} question marks sent.\n2. {user_list[1][0]} with {user_list[1][1]} question marks sent.\n3. {user_list[2][0]} with {user_list[2][1]} question marks sent.\n4. {user_list[3][0]} with {user_list[3][1]} question marks sent.\n5. {user_list[4][0]} with {user_list[4][1]} question marks sent.\n6. {user_list[5][0]} with {user_list[5][1]} question marks sent.\n7. {user_list[6][0]} with {user_list[6][1]} question marks sent.\n8. {user_list[7][0]} with {user_list[7][1]} question marks sent.\n9. {user_list[8][0]} with {user_list[8][1]} question marks sent.\n10. {user_list[9][0]} with {user_list[9][1]} question marks sent.""")
        #
        #del user_list
        #gc.collect()