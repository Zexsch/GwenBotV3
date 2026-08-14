## General
1. Your Gwen is Global-State, e.g. it isn't per-guild but per-user. Build her once, she's the same in every other guild. Honestly I'm not 100% sure about this, especially since other bots (think mudae) don't do this, but mudae is also very different
2. Your Gwen has actual stats. From league. HP, AD, AP, armour, etc.
3. You have 3 core dailies/hourlies you can do: Stitch, Fill (with cotton), Train. All 3 will increase an affection stat, but more importantly, stitch and fill will restore HP (more about that later again) and train will give a semi-permanent stat increase. I've also thought about only fill restoring HP, whilst stitching will increase armour, where armour drops the more hurt she is. Making it rather punishing.
4. Main gameplay loop will be league themed combat! Yes, this shall be an idle game. You make gwen fight minions to get gold and levels, you can use that gold to buy items, and every few levels you fight an actual champion. At first, the amount of gold you get and items you can buy will be limited. But fight the level 18 uber-boss and you go up in elo, starting at iron, all the way up to challenger. The higher your elo, the more items you can buy and upgrade, and the stronger the enemies will be. Uber bosses will be hard counters, with the final challenger uber boss being Vayne for obvious reasons.

## Core gameplay loop
1. Make Gwen fight minions, get gold, get items
2. Upgrade those items if necessary (not into higher components, but just + stats, you can choose what stats you want, you can + upgrade up to your current level)
3. Fill and stitch her up, train her
4. Make gwen fight more minions if necessary, or try your hands at a boss.

## Builds
To not make builds monotonous, I was thinking of having clear advantages for them. Early game, AD might be very good, as it increases damage to minions, same with armour, as it decreases damage from minions or damage from AD champs, but at the same time, I might just throw a malphite at you. 

## Other, more difficult, ideas
~~To not make it just a statcheck, I could add actual buttons during combat, where you can decide what abilit to get and upgrade if you're lower level, and then also decide when in combat to use them, with cooldowns of course. Maybe add slight RNG mechanics like Q sometimes hitting centre for true damage, sometimes hitting the edges for magic damage.~~ **I have decided not to do this.**
W could give you extra armour and mr, like it does in the game, and a dodge chance against ranged enemies to emulate Gwen is immune, You could time ult wisely to heal a lot via passive. Shit like that. But at the same time, this would be pretty difficult to actually implement and would be slash-commands only.


# For a V1 build:
1. Add Gwen and her stats
2. Add fill, stitch, train (I think that fill should get one stack every hour, max stacks of 5, stitch gets one stack every 3h, max stack 3, train one stack every 6h, max 2) (I'm also thinking of adding a cotton/thread resource which can be bought via gold and can be used to avoid these waits)
3. Add minion combat, hardcoded champ encounters at level 6, 13 and 18
4. Iron elo only, so you're limited to dorans items and T1 items
5. Once you've beaten level 18 boss you would normally increase to bronze rank

Also, instead of upgrading item stats willy nilly, maybe I can add specialisations (e.g. later on, nashors can go toward a full AP build or a more ASPD focused build)


# Item upgrades
Below a specific elo, you can just upgrade the items directly, giving it a stat boost
I think base max level of 3 is good, increasing by 1 per elo
each upgrade gives 1.1* stats, so +3 would give a 1.33* boost, not 1.3*
Maybe starting diamond you can start specialising items directly, giving them a specific
main stat which gets upgraded at 1.3* or so instead.
Maybe then also starting master you need to combine two of the same item with the same
specialisation to upgrade it, instead of just gold.


# Extra bossfights
At later elos, I could add extra bossfights like baron, dragons and elder dragon.
These would be level locked.
For example, every 3 levels you can do a dragon fight, which gives bonuses this elo.
Miss it, and you won't get the bonuses. In fact, in gm+ you could have the enemy
get these bonuses instead. Would make strategising more important.
You could then do elder at lv15 for a big damage buff, and nash at lv16 or 17 to prep
for the final bossfight.