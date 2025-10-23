from discord.ext import commands

from Database.database import DatabaseHandler


class CommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot, database: DatabaseHandler):
        self.bot = bot
        self.database = database

    @commands.command(aliases=['Evasion', 'jax'])
    async def evasion(self, ctx: commands.Context):
        await ctx.send(r'Active: Jax enters Evasion, a defensive stance, for up to 2 seconds, causing all basic attacks against him to miss. Jax also takes 25% reduced damage from all champion area of effect abilities. After 1 second, Jax can reactivate to end it immediately.')
    
    @commands.command(aliases=['gwen', 'immune'])
    async def g(self, ctx: commands.Context):
        if not self.database.fetch_gwen_sub(ctx.author.id, ctx.guild.id): # type: ignore
            return
        await ctx.send('Gwen is immune.')
    
    @commands.command(aliases=['Aatrox'])
    async def aatrox(self, ctx: commands.Context):
        await ctx.send('Aatrox got ignited.')
    
    @commands.command(aliases=['lh', 'Lh', 'LH'])
    async def listenhere(self, ctx: commands.Context):
        await ctx.send('listen here you little shit')
        
    @commands.command(aliases=['Emo'])
    async def emo(self, ctx: commands.Context):
        await ctx.send("Aatrox's biggest fan (owns an Aatrox tshirt)")
        
    @commands.command(aliases=['george','George','Sylas'])
    async def sylas(self, ctx: commands.Context):
        await ctx.send('Sylas pressed W. https://imgur.com/IHyk5hl')
    
    @commands.command(aliases=["Wis'adel", 'w', 'W', 'balans'])
    async def wisadel(self, ctx: commands.Context):
        await ctx.send(r"Immediately summons 2 Shadows of Revenant within attack range (max 3, persists after the skill ends); ATK +180%, attack interval increases significantly, ATK increases to 220% when attacking, splash damage radius expands, and 1st Talent activation chance increases to 100%. Skill activation grants 6 ammo and the skill ends when all ammo are used (Can manually deactivate skill)")

    @commands.command()
    async def lana(self, ctx: commands.Context):
        await ctx.send("https://media.discordapp.net/attachments/1320437220116791406/1321894179646734366/IMG_6786.png?ex=676ee564&is=676d93e4&hm=f7bb76b71252e93f59dfc8a6508dfbc8218b35775c332561cd8a68235a43fbfa&=&format=webp&quality=lossless&width=814&height=793")

    @commands.command()
    async def zex(self, ctx: commands.Context):
        await ctx.send("https://media.discordapp.net/attachments/1320437220116791406/1338656615619887145/Screenshot_20250210_152123_Discord.jpg?ex=67abe0a0&is=67aa8f20&hm=27c2301565f3995aaec637387d3abf946d664bfa7880e7864215e5b266c21dad&=&format=webp")