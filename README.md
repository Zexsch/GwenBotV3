# GwenBotV3
GwenBotV3 is the third iteration of GwenBot, a Gwen from League of Legends themed discord bot.
## Commands
For a mostly full list of commands, see `src/gwenbotv3/bot/cogs/help_cog.py`<br>
The main commands are:<br>
1. `winrate` - Fetches the winrate of a given champion from u.gg. With optional arguments being elo, opponent, patch and role.
2. `gwenadd` - Subscribes a user to GwenBot, making Gwen reply with "Gwen is immune." whenever gwen is mentioned in chat by this user.
3. `gwenseek` - Uses the Deepseek API to give Gwen themed AI responses.

## Installation
### Discord Setup
Add your discord bot token as an environment variable called `TOKEN` <br>
Add your deepseek token as an Environment Variable called `DEEPSEEK_TOKEN`<br>
Add your discord user ID as an environment variable called `OWNER_ID`<br>
Add a test guild ID for slash commands as an environment variable called `TEST_GUILD`<br>
### Database Setup
Currently, only mysql is supported.<br><br>
Add your database service username as an environment variable called `DB_USER` <br>
Add your database password as an environment variable called `DB_PASS` <br>
Add your dtabase host FQDN or IP as an environment variable called `DB_HOST` <br>
Add your database port as an environment variable called `DB_PORT` <br>
Add your database name as an environment variable called `DB_NAME` <br>
### Usage
Clone this repo, then either run `main.py` directly or install via pip. If installed via pip, you can use the `gwenbot-init` command to start the bot.

## Legal
GwenBot was created under Riot Games' "Legal Jibber Jabber" policy using assets owned by Riot Games.  Riot Games does not endorse or sponsor this project.