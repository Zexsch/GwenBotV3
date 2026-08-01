"""Houses the Help cog."""

import discord
from discord.ext import commands


# pylint: disable=line-too-long
# ruff: noqa: E501
class HelpCog(commands.Cog):
    """Any commands relating to help."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _get_help_embed(self) -> discord.Embed:
        """Gets the embed for the help command.

        Returns:
            discord.Embed: Embed
        """
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
        embed.add_field(name="Counter", value="See the `+counterhelp` command.")
        embed.add_field(
            name="Privacy",
            value=(
                "[Privacy Policy](https://github.com/Zexsch/GwenBotV3/blob/main/PRIVACY.md)\n"
                "See the `+privacy` command."
            ),
            inline=False,
        )
        embed.set_footer(text="GwenBot is open source: github.com/Zexsch/GwenBotV3")
        return embed

    async def _get_wrhelp_embed(self) -> discord.Embed:
        """Gets the embed for the wrhelp command.

        Returns:
            discord.Embed: Embed
        """
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

    async def _get_privacy_embed(self) -> discord.Embed:
        """Gets the embed for the privacy help command.

        Returns:
            discord.Embed: Embed
        """
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

    async def _get_counter_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="Counter",
            description="Format: `+command (aliases)` - description",
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="Counter",
            value=(
                "Server moderators can initialise a channel to start counting a symbol. "
                "Once a channel is initialised, Gwen will count the amount of occurences "
                "of this symbol sent in the specified channel."
            ),
        )
        embed.add_field(
            name="Commands",
            value=(
                "`+initialise` - See the initialise section.\n"
                "`+strict` - See the strictness section.\n"
                "`+recount` - Recounts the number of symbols. In long chats, this will take a while.\n"
                "`+amount` - Tells you the amount of symbols sent.\n"
                "`+amountu` - Tells you the amount of symbols sent by a user.\n"
                "`+leaderboard` - See the leaderboard section."
            ),
        )
        embed.add_field(
            name="Initialise",
            value=(
                "# Usage\n"
                "`+initialise` *symbol* *channel*\n\n"
                "# Symbol\n"
                "A symbol can be any string of characters which is at most 200 characters long.\n\n"
                "# Channel\n"
                "The channel to start counting in. By definition, this means that only symbols sent "
                "in this specific channel will be counted, not server-wide.\n"
                "You can either tag the channel directly or use an ID."
            ),
        )
        embed.add_field(
            name="Strictness",
            value=(
                "# Not strict\n"
                "When the counter is set to not be strict, which is the default, Gwen will simply "
                "ignore all instances of a counter's rules being broken.\n\n"
                "# Rules\n"
                "- Only the specified symbol is allowed to be sent in the chat.\n"
                "- A user may only send one symbol in a row.\n\n"
                "# Strict\n"
                "When strictness is turned on, any infraction of the rules will not be counted.\n"
                "The user that first initialised the counter will also be pinged in the channel where "
                "the `+strict` command was used every time a rule gets broken.\n\n"
                "# Usage\n"
                "The `+strict` command flips the strictness for the counter. If it was disabled, it "
                "will then be enabled, and vice-versa."
            ),
        )

        return embed

    @commands.command(aliases=["Menu"])
    async def help(self, ctx: commands.Context[commands.Bot]) -> None:
        """Sends the help message."""
        user: discord.Member | discord.User = ctx.message.author
        embed = await self._get_help_embed()

        await user.send(embed=embed)

    @commands.command(aliases=["wrhelp"])
    async def winratehelp(self, ctx: commands.Context[commands.Bot]) -> None:
        """Sends the winratehelp message."""
        user: discord.Member | discord.User = ctx.message.author
        embed = await self._get_wrhelp_embed()

        await user.send(embed=embed)

    @commands.command(aliases=["policy"])
    async def privacy(self, ctx: commands.Context[commands.Bot]) -> None:
        """Sends the privacy help message."""
        user: discord.Member | discord.User = ctx.message.author
        embed = await self._get_privacy_embed()

        await user.send(embed=embed)
