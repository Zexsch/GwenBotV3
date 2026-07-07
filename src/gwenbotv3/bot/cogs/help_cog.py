from logging import Logger

import discord
from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: Logger):
        self.bot = bot
        self.logger = logger

    async def get_help_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="GwenBot Help",
            description="Format: `+command (aliases)` _parameters_ - description",
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="General",
            value=(
                "`+help` - Displays this help menu in DMs.\n"
                "`+wrhelp (winratehelp)` - Displays the winrate help menu in DMs.\n"
                "`+gwenadd (add, gwenadd)` - Auto-replies to any message containing 'Gwen', server-wide.\n"
                "`+gwenremove (remove, rem, removesub)` - Removes you from the autoreplies.\n"
                "`+list` - Sends a list of all accepted champions in DMs.\n"
                "`+elolist` - Sends a list of all accepted elos in DMs.\n"
                "`+rolelist (roles)` - Lists available roles.\n"
                "`+patch (version, checkver)` - Shows the current League patch GwenBot uses."
            ),
            inline=False,
        )
        embed.add_field(
            name="Moderation",
            value=(
                "`+quote` - Disables `+gwenadd` in the current server entirely.\n"
                "`+blacklist` _user_ - Blacklist a user from using `+gwenadd`.\n"
                "`+unblacklist` _user_ - Remove a user from the blacklist."
            ),
            inline=False,
        )
        embed.add_field(
            name="Fun",
            value="`+evasion (jax)` `+gwen (g, immune)` `+listenhere (lh)` `+aatrox` `+emo` `+sylas (george)`",
            inline=False,
        )
        embed.add_field(
            name="Gwenseek",
            value=(
                "Gwenseek uses the Deepseek API to return Gwen-Themed AI responses.\n"
                "Gwen remembers your last 5 gwenseek messages and their response per-server.\n\n"
                "`+gwenseek` _message_ - Uses Deepseek's reasoning model to respond.\n"
                "`+gwenseekb (gwenseekbasic)` _message_ - Uses Deepseek's basic model to respond.\n"
                "`+clearhistory (ch)` - Clears your gwenseek history in the current server.\n"
                "`+clearhistoryall (cha, chall)` - Clears all your gwenseek history."
            ),
            inline=False,
        )
        embed.add_field(
            name="Privacy",
            value=(
                "[Privacy Policy](https://github.com/Zexsch/GwenBotV3/blob/main/PRIVACY.md)\n"
                "`+anonymise (anonymize, pseudonymise)` - Pseudonymises your data. Your username is removed from Gwen's database and your interactions are deleted where possible. **Your user ID is kept so blacklists still work.**\n"
                "`+unanonymise` - Restores username storage."
            ),
            inline=False,
        )
        embed.set_footer(text="GwenBot is open source: github.com/Zexsch/GwenBotV3")
        return embed

    async def get_wrhelp_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="Winrate Help",
            description="Format: `+command (aliases)` - description",
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="Command",
            value=(
                "`+wr` _champion_ - Sends the winrate of the given champion.\n"
                "_Optional parameters: elo, role, opposing champion, patch_"
            ),
            inline=False,
        )
        embed.add_field(
            name="Examples",
            value=(
                "`+wr vayne`\n"
                "*Gives the winrate of Vayne in her primary lane in all elos in the current patch.*\n\n"
                "`+wr vayne top d2+ 15.20 aatrox`\n"
                "*Gives the winrate of Vayne in top lane, in D2+ elo, against Aatrox, on patch 15.20.*\n\n"
                "`+wr vayne leesin jgl`\n"
                "*Gives the winrate of Vayne in jungle against Lee Sin."
            ),
            inline=False,
        )
        embed.add_field(
            name="Notes",
            value=(
                "> Only the latest 5 patches are available. Check the current patch with `+patch`.\n"
                "> If u.gg is up but the command isn't working, message @zexsch."
            ),
            inline=False,
        )

        return embed

    async def get_privacy_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="Privacy",
            description="Format: `+command (aliases)` - description",
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="Commands",
            value=(
                "`+privacy` - Show this help message.\n"
                "`+anonymise (anonymize, pseudonymise)` - Pseudonymises your data. "
                "Your username is removed from Gwen's database and your interactions are "
                "deleted where possible. **Your user ID is kept so blacklists still work.**\n"
                "`+unanonymise` - Restores username storage if you previously ran `+anonymise`.\n"
                "`+clearhistory (ch)` - Clears your gwenseek history in the current server.\n"
                "`+clearhistoryall (cha, chall)` - Clears all your gwenseek history."
            ),
        )

        embed.set_footer(
            text="Privacy Policy: https://github.com/Zexsch/GwenBotV3/blob/main/PRIVACY.md"
        )
        return embed

    @commands.command(aliases=["Menu"])
    async def help(self, ctx: commands.Context):
        user: discord.Member | discord.User = ctx.message.author
        embed = self.get_help_embed()

        if not isinstance(embed, discord.Embed):
            await ctx.send("Gwen ran into some major issues!")
            return

        await user.send(embed=embed)

    @commands.command(aliases=["wrhelp"])
    async def winratehelp(self, ctx: commands.Context):
        user: discord.Member | discord.User = ctx.message.author
        embed = self.get_wrhelp_embed()

        if not isinstance(embed, discord.Embed):
            await ctx.send("Gwen ran into some major issues!")
            return

        await user.send(embed=embed)

    @commands.command(aliases=["policy"])
    async def privacy(self, ctx: commands.Context):
        user: discord.Member | discord.User = ctx.message.author
        embed = self.get_privacy_embed()

        if not isinstance(embed, discord.Embed):
            await ctx.send("Gwen ran into some major issues!")
            return

        await user.send(embed=embed)
