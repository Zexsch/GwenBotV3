HELPMESSAGE: str = """
**GwenBot Help**
Format: `+command (aliases)` - description

**General**
`+help` - Displays this help menu in DMs.
`+wrhelp (winratehelp)` - Displays the winrate help menu in DMs.
`+gwenadd (add, gwenadd)` - Makes the bot auto-reply to any message containing "Gwen", server-wide.
`+gwenremove (remove, rem, removesub)` - Removes you from the autoreplies.
`+list` - Sends a list of all accepted champions in DMs. Note: some champions have unusual official names.
`+elolist` - Sends a list of all accepted elos in DMs.
`+rolelist (roles)` - Lists available roles.
`+patch (version, checkver)` - Shows the current League patch GwenBot uses. Champs added after this patch may not work.

**Fun**
`+evasion (jax)`
`+gwen (g, immune)`
`+listenhere (lh)`
`+aatrox`
`+emo`
`+sylas (george)`

**Privacy**
Privacy Policy: <https://github.com/Zexsch/GwenBotV3/blob/main/PRIVACY.md>
`+anonymise (anonymize, pseudonymise)` - Pseudonymises your data. Your username is removed from Gwen's database and your interactions are deleted where possible. Your user ID is kept so blacklists still work.
`+unanonymise` - Restores username storage if you previously ran `+anonymise`.

GwenBot is open source: <https://github.com/Zexsch/GwenBotV3>
"""


WRHELPMESSAGE: str = """
**Winrate Help**
Format: `+command (aliases)` - description

`+wr (winrate) | (champion)` - Gives the winrate of the given champion.

**Optional parameters:** elo, role, opposing champ, patch

**Example:**
`+wr vayne top d2+ 15.20 aatrox`
*Gives the winrate of Vayne in top lane, in D2+ elo, against Aatrox, on patch 15.20.*

`+wr vayne`
*Gives the winrate of Vayne in her primary lane in all elos in the current patch.*

`+wr vayne leesin jgl`
*Gives the winrate of Vayne in jungle against Lee Sin. 

**Notes:**
- Only the latest 5 patches are available. Check the current patch with `+patch`.
- If u.gg is up but the command isn't working, message @zexsch.
"""


PRIVACY_POLCIY: str = """
You may find the latest up-to-date privacy policy on GwenBot's github:
https://github.com/Zexsch/GwenBotV3
or a direct link to the privacy policy:
https://github.com/Zexsch/GwenBotV3/blob/main/PRIVACY.md"""
