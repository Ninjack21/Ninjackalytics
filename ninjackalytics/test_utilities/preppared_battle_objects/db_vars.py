log = """
|inactive|Battle timer is ON: inactive players will automatically lose when time's up.
|t:|1697914252
|gametype|singles
|player|p1|Airi Pearl|#wcop2023latinamerica2|
|player|p2|RED WHITE and TEAL|#splxisharks|
|teamsize|p1|6
|teamsize|p2|6
|gen|9
|tier|[Gen 9] OU
|rule|Sleep Clause Mod: Limit one foe put to sleep
|rule|Species Clause: Limit one of each Pokémon
|rule|OHKO Clause: OHKO moves are banned
|rule|Evasion Items Clause: Evasion items are banned
|rule|Evasion Moves Clause: Evasion moves are banned
|rule|Endless Battle Clause: Forcing endless battles is banned
|rule|HP Percentage Mod: HP is shown in percentages
|clearpoke
|poke|p1|Gliscor, M|
|poke|p1|Clefable, F|
|poke|p1|Cinderace, F|
|poke|p1|Dragapult, F|
|poke|p1|Kingambit, M|
|poke|p1|Iron Valiant|
|poke|p2|Hatterene, F|
|poke|p2|Roaring Moon|
|poke|p2|Manaphy|
|poke|p2|Ursaluna, M|
|poke|p2|Kingambit, M|
|poke|p2|Heatran, M|
|teampreview
|c|☆RED WHITE and TEAL|hf
|c|☆Airi Pearl|U2
|inactive|RED WHITE and TEAL has 270 seconds left.
|inactive|RED WHITE and TEAL has 240 seconds left.
|
|t:|1697914316
|start
|switch|p1a: Dragapult|Dragapult, F|100/100
|switch|p2a: Manaphy|Manaphy|100/100
|turn|1
|
|t:|1697914326
|switch|p2a: Kingambit|Kingambit, M|100/100
|move|p1a: Dragapult|Thunderbolt|p2a: Kingambit
|-damage|p2a: Kingambit|59/100
|
|-heal|p2a: Kingambit|66/100|[from] item: Leftovers
|upkeep
|turn|2
|
|t:|1697914346
|switch|p1a: Gliscor|Gliscor, M|100/100
|move|p2a: Kingambit|Iron Head|p1a: Gliscor
|-damage|p1a: Gliscor|70/100
|
|-heal|p2a: Kingambit|72/100|[from] item: Leftovers
|-status|p1a: Gliscor|tox|[from] item: Toxic Orb
|upkeep
|turn|3
|
|t:|1697914356
|-end|p2a: Kingambit|fallenundefined|[silent]
|switch|p2a: Hatterene|Hatterene, F|100/100
|move|p1a: Gliscor|Knock Off|p2a: Hatterene
|-damage|p2a: Hatterene|81/100
|-enditem|p2a: Hatterene|Leftovers|[from] move: Knock Off|[of] p1a: Gliscor
|
|-heal|p1a: Gliscor|83/100 tox|[from] ability: Poison Heal
|upkeep
|turn|4
|
|t:|1697914366
|switch|p1a: Cinderace|Cinderace, F|100/100
|move|p2a: Hatterene|Calm Mind|p2a: Hatterene
|-boost|p2a: Hatterene|spa|1
|-boost|p2a: Hatterene|spd|1
|
|upkeep
|turn|5
|
|t:|1697914373
|move|p1a: Cinderace|Pyro Ball|p2a: Hatterene
|-damage|p2a: Hatterene|38/100
|move|p2a: Hatterene|Nuzzle|p1a: Cinderace
|-damage|p1a: Cinderace|96/100
|-status|p1a: Cinderace|par
|
|upkeep
|turn|6
|
|t:|1697914392
|switch|p2a: Heatran|Heatran, M|100/100
|-item|p2a: Heatran|Air Balloon
|move|p1a: Cinderace|U-turn|p2a: Heatran
|-resisted|p2a: Heatran
|-damage|p2a: Heatran|96/100
|-enditem|p2a: Heatran|Air Balloon
|
|t:|1697914403
|switch|p1a: Gliscor|Gliscor, M|83/100 tox|[from] U-turn
|
|-heal|p1a: Gliscor|95/100 tox|[from] ability: Poison Heal
|upkeep
|turn|7
|
|t:|1697914410
|switch|p2a: Hatterene|Hatterene, F|38/100
|move|p1a: Gliscor|Knock Off|p2a: Hatterene
|-damage|p2a: Hatterene|25/100
|
|-heal|p1a: Gliscor|100/100 tox|[from] ability: Poison Heal
|upkeep
|turn|8
|
|t:|1697914417
|switch|p1a: Cinderace|Cinderace, F|96/100 par
|move|p2a: Hatterene|Draining Kiss|p1a: Cinderace
|-resisted|p1a: Cinderace
|-damage|p1a: Cinderace|84/100 par
|-heal|p2a: Hatterene|36/100|[from] drain|[of] p1a: Cinderace
|
|upkeep
|turn|9
|
|t:|1697914429
|move|p1a: Cinderace|U-turn|p2a: Hatterene
|-damage|p2a: Hatterene|18/100
|
|t:|1697914436
|switch|p1a: Kingambit|Kingambit, M|100/100|[from] U-turn
|move|p2a: Hatterene|Draining Kiss|p1a: Kingambit
|-damage|p1a: Kingambit|75/100
|-heal|p2a: Hatterene|41/100|[from] drain|[of] p1a: Kingambit
|
|upkeep
|turn|10
|
|t:|1697914443
|move|p1a: Kingambit|Kowtow Cleave|p2a: Hatterene
|-damage|p2a: Hatterene|0 fnt
|faint|p2a: Hatterene
|
|upkeep
|
|t:|1697914449
|switch|p2a: Heatran|Heatran, M|96/100
|turn|11
|
|t:|1697914454
|-end|p1a: Kingambit|fallenundefined|[silent]
|switch|p1a: Gliscor|Gliscor, M|100/100 tox
|move|p2a: Heatran|Stealth Rock|p1a: Gliscor
|-sidestart|p1: Airi Pearl|move: Stealth Rock
|
|upkeep
|turn|12
|
|t:|1697914459
|switch|p2a: Manaphy|Manaphy|100/100
|move|p1a: Gliscor|Protect||[still]
|-fail|p1a: Gliscor
|
|upkeep
|turn|13
|
|t:|1697914467
|switch|p1a: Iron Valiant|Iron Valiant|100/100
|move|p2a: Manaphy|Take Heart|p2a: Manaphy
|-boost|p2a: Manaphy|spa|1
|-boost|p2a: Manaphy|spd|1
|
|upkeep
|turn|14
|
|t:|1697914473
|switch|p2a: Heatran|Heatran, M|96/100
|move|p1a: Iron Valiant|Encore||[still]
|-fail|p1a: Iron Valiant
|
|upkeep
|turn|15
|
|t:|1697914481
|-end|p1a: Iron Valiant|Quark Drive|[silent]
|switch|p1a: Gliscor|Gliscor, M|100/100 tox
|-damage|p1a: Gliscor|88/100 tox|[from] Stealth Rock
|-terastallize|p2a: Heatran|Ghost
|move|p2a: Heatran|Magma Storm|p1a: Gliscor|[miss]
|-miss|p2a: Heatran|p1a: Gliscor
|
|-heal|p1a: Gliscor|100/100 tox|[from] ability: Poison Heal
|upkeep
|turn|16
|
|t:|1697914490
|switch|p2a: Manaphy|Manaphy|100/100
|move|p1a: Gliscor|Toxic|p2a: Manaphy
|-status|p2a: Manaphy|tox
|
|-damage|p2a: Manaphy|94/100 tox|[from] psn
|upkeep
|turn|17
|
|t:|1697914493
|switch|p1a: Iron Valiant|Iron Valiant|100/100
|move|p2a: Manaphy|Take Heart|p2a: Manaphy
|-boost|p2a: Manaphy|spa|1
|-boost|p2a: Manaphy|spd|1
|-curestatus|p2a: Manaphy|tox|[msg]
|
|-heal|p2a: Manaphy|100/100|[from] item: Leftovers
|upkeep
|turn|18
|
|t:|1697914498
|switch|p2a: Heatran|Heatran, M, tera:Ghost|96/100
|move|p1a: Iron Valiant|Encore||[still]
|-fail|p1a: Iron Valiant
|
|upkeep
|turn|19
|
|t:|1697914514
|-end|p1a: Iron Valiant|Quark Drive|[silent]
|switch|p1a: Gliscor|Gliscor, M|100/100 tox
|-damage|p1a: Gliscor|88/100 tox|[from] Stealth Rock
|switch|p2a: Ursaluna|Ursaluna, M|100/100
|
|-heal|p1a: Gliscor|100/100 tox|[from] ability: Poison Heal
|-status|p2a: Ursaluna|brn|[from] item: Flame Orb
|upkeep
|turn|20
|
|t:|1697914526
|move|p1a: Gliscor|Spikes|p2a: Ursaluna
|-sidestart|p2: RED WHITE and TEAL|Spikes
|move|p2a: Ursaluna|Facade|p1a: Gliscor
|-damage|p1a: Gliscor|22/100 tox
|
|-heal|p1a: Gliscor|34/100 tox|[from] ability: Poison Heal
|-damage|p2a: Ursaluna|94/100 brn|[from] brn
|upkeep
|turn|21
|
|t:|1697914544
|move|p1a: Gliscor|Spikes|p2a: Ursaluna
|-sidestart|p2: RED WHITE and TEAL|Spikes
|move|p2a: Ursaluna|Trailblaze|p1a: Gliscor
|-damage|p1a: Gliscor|17/100 tox
|-boost|p2a: Ursaluna|spe|1
|
|-heal|p1a: Gliscor|29/100 tox|[from] ability: Poison Heal
|-damage|p2a: Ursaluna|88/100 brn|[from] brn
|upkeep
|turn|22
|
|t:|1697914558
|move|p1a: Gliscor|Protect|p1a: Gliscor
|-singleturn|p1a: Gliscor|Protect
|move|p2a: Ursaluna|Swords Dance|p2a: Ursaluna
|-boost|p2a: Ursaluna|atk|2
|
|-heal|p1a: Gliscor|42/100 tox|[from] ability: Poison Heal
|-damage|p2a: Ursaluna|82/100 brn|[from] brn
|upkeep
|turn|23
|
|t:|1697914564
|switch|p1a: Dragapult|Dragapult, F|100/100
|-damage|p1a: Dragapult|88/100|[from] Stealth Rock
|move|p2a: Ursaluna|Trailblaze|p1a: Dragapult
|-resisted|p1a: Dragapult
|-damage|p1a: Dragapult|48/100
|-boost|p2a: Ursaluna|spe|1
|
|-damage|p2a: Ursaluna|76/100 brn|[from] brn
|upkeep
|turn|24
|
|t:|1697914572
|move|p1a: Dragapult|Draco Meteor|p2a: Ursaluna
|-damage|p2a: Ursaluna|0 fnt
|-unboost|p1a: Dragapult|spa|2
|faint|p2a: Ursaluna
|
|upkeep
|
|t:|1697914576
|switch|p2a: Kingambit|Kingambit, M|72/100
|-damage|p2a: Kingambit|55/100|[from] Spikes
|-activate|p2a: Kingambit|ability: Supreme Overlord
|-start|p2a: Kingambit|fallen2|[silent]
|turn|25
|
|t:|1697914581
|switch|p1a: Gliscor|Gliscor, M|42/100 tox
|-damage|p1a: Gliscor|29/100 tox|[from] Stealth Rock
|move|p2a: Kingambit|Swords Dance|p2a: Kingambit
|-boost|p2a: Kingambit|atk|2
|
|-heal|p2a: Kingambit|61/100|[from] item: Leftovers
|-heal|p1a: Gliscor|42/100 tox|[from] ability: Poison Heal
|upkeep
|turn|26
|
|t:|1697914598
|move|p1a: Gliscor|Knock Off|p2a: Kingambit
|-resisted|p2a: Kingambit
|-damage|p2a: Kingambit|53/100
|-enditem|p2a: Kingambit|Leftovers|[from] move: Knock Off|[of] p1a: Gliscor
|move|p2a: Kingambit|Iron Head|p1a: Gliscor
|-damage|p1a: Gliscor|0 fnt
|faint|p1a: Gliscor
|
|upkeep
|
|t:|1697914603
|switch|p1a: Iron Valiant|Iron Valiant|100/100
|turn|27
|
|t:|1697914618
|-terastallize|p1a: Iron Valiant|Fairy
|move|p2a: Kingambit|Sucker Punch|p1a: Iron Valiant
|-resisted|p1a: Iron Valiant
|-damage|p1a: Iron Valiant|36/100
|move|p1a: Iron Valiant|Moonblast|p2a: Kingambit
|-damage|p2a: Kingambit|0 fnt
|faint|p2a: Kingambit
|-end|p2a: Kingambit|fallen2|[silent]
|
|upkeep
|
|t:|1697914624
|switch|p2a: Roaring Moon|Roaring Moon|100/100
|-damage|p2a: Roaring Moon|84/100|[from] Spikes
|-enditem|p2a: Roaring Moon|Booster Energy
|-activate|p2a: Roaring Moon|ability: Protosynthesis|[fromitem]
|-start|p2a: Roaring Moon|protosynthesisatk
|turn|28
|
|t:|1697914638
|-end|p1a: Iron Valiant|Quark Drive|[silent]
|switch|p1a: Clefable|Clefable, F|100/100
|move|p2a: Roaring Moon|Dragon Dance|p2a: Roaring Moon
|-boost|p2a: Roaring Moon|atk|1
|-boost|p2a: Roaring Moon|spe|1
|
|upkeep
|turn|29
|
|t:|1697914643
|move|p2a: Roaring Moon|Acrobatics|p1a: Clefable
|-damage|p1a: Clefable|56/100
|move|p1a: Clefable|Moonblast|p2a: Roaring Moon
|-supereffective|p2a: Roaring Moon
|-damage|p2a: Roaring Moon|0 fnt
|faint|p2a: Roaring Moon
|-end|p2a: Roaring Moon|Protosynthesis|[silent]
|
|upkeep
|
|t:|1697914650
|switch|p2a: Manaphy|Manaphy|100/100
|-damage|p2a: Manaphy|84/100|[from] Spikes
|turn|30
|
|t:|1697914661
|switch|p1a: Iron Valiant|Iron Valiant, tera:Fairy|36/100
|move|p2a: Manaphy|Take Heart|p2a: Manaphy
|-boost|p2a: Manaphy|spa|1
|-boost|p2a: Manaphy|spd|1
|
|-heal|p2a: Manaphy|90/100|[from] item: Leftovers
|upkeep
|turn|31
|
|t:|1697914665
|switch|p2a: Heatran|Heatran, M, tera:Ghost|96/100
|-damage|p2a: Heatran|79/100|[from] Spikes
|move|p1a: Iron Valiant|Encore||[still]
|-fail|p1a: Iron Valiant
|
|upkeep
|turn|32
|
|t:|1697914669
|-end|p1a: Iron Valiant|Quark Drive|[silent]
|switch|p1a: Cinderace|Cinderace, F|84/100 par
|switch|p2a: Manaphy|Manaphy|90/100
|-damage|p2a: Manaphy|73/100|[from] Spikes
|
|-heal|p2a: Manaphy|80/100|[from] item: Leftovers
|upkeep
|turn|33
|
|t:|1697914673
|move|p2a: Manaphy|Scald|p1a: Cinderace
|-supereffective|p1a: Cinderace
|-damage|p1a: Cinderace|15/100 par
|move|p1a: Cinderace|U-turn|p2a: Manaphy
|-damage|p2a: Manaphy|65/100
|
|t:|1697914677
|switch|p1a: Dragapult|Dragapult, F|48/100|[from] U-turn
|-damage|p1a: Dragapult|36/100|[from] Stealth Rock
|
|-heal|p2a: Manaphy|71/100|[from] item: Leftovers
|upkeep
|turn|34
|
|t:|1697914680
|switch|p2a: Heatran|Heatran, M, tera:Ghost|79/100
|-damage|p2a: Heatran|63/100|[from] Spikes
|move|p1a: Dragapult|Shadow Ball|p2a: Heatran
|-supereffective|p2a: Heatran
|-damage|p2a: Heatran|0 fnt
|faint|p2a: Heatran
|
|upkeep
|
|t:|1697914682
|switch|p2a: Manaphy|Manaphy|71/100
|-damage|p2a: Manaphy|54/100|[from] Spikes
|turn|35
|
|t:|1697914685
|move|p1a: Dragapult|Shadow Ball|p2a: Manaphy
|-damage|p2a: Manaphy|10/100
|move|p2a: Manaphy|Scald|p1a: Dragapult
|-resisted|p1a: Dragapult
|-damage|p1a: Dragapult|18/100
|
|-heal|p2a: Manaphy|16/100|[from] item: Leftovers
|upkeep
|turn|36
|
|t:|1697914687
|move|p1a: Dragapult|Shadow Ball|p2a: Manaphy
|-damage|p2a: Manaphy|0 fnt
|faint|p2a: Manaphy
|
|win|Airi Pearl
|c|☆RED WHITE and TEAL|gg
|c|☆Airi Pearl|gg
"""

b_format = "gen9ou"

b_id = "smogtours-gen9ou-725192"
