# using gen9OU as this is the current format
# https://replay.pokemonshowdown.com/gen9ou-1954574413

"""
This file is to provide a Response and Battle object for testing purposes. As such we mimic the interface
without requiring the actual connectivity. Over time this battle will become more and more dated. 

It may be good practice to occasionally manually run a more recent battle and then update the tests
accordingly. Though, admittedly, this sounds like a total pain :p

I think instead of that we may want to put a shelf life on all test battles of 5 years. After 5 years
that particular battle and its tests are removed from the testing suite and considered sunset. We should
find enough bugs overtime to continually replenish the test suite with new battles that represent the 
more important features of the game.

Date: 9-28-2023
"""


class TestResponse:
    def __init__(self):
        """
        Initialize a Response object from a JSON response.

        Parameters:
        -----------
        response: dict
            A dictionary containing the JSON response.

        """
        self._log = log
        self._battle_id = b_id
        self._format = b_format

        try:
            battle_start = self.log.split("|start\n")[1]
            log_turns = battle_start.split("|turn|")
            self.turns = [
                Turn(turn_num, turn_str) for turn_num, turn_str in enumerate(log_turns)
            ]
        except:
            self.turns = []

    @property
    def battle_id(self) -> str:
        """
        Get the battle ID.

        Returns:
        --------
        str:
            The battle ID.
        """
        return self._battle_id

    @property
    def format(self) -> str:
        """
        Get the battle format.

        Returns:
        --------
        str:
            The battle format.
        """
        return self._format

    @property
    def log(self) -> str:
        """
        Get the battle format.

        Returns:
        --------
        str:
            The battle format.
        """
        return self._log


class TestBattle:
    def __init__(self):
        """
        Initialize a Battle object from a URL

        Parameters:
        -----------
        url: str
            The URL of the Pokemon battle

        """
        self.url = url
        self.response = TestResponse()

    def get_lines(self) -> list:
        """
        Get a list of all Line objects in the battle.

        Returns:
        --------
        List[Line]:
            A list of all Line objects in the battle.
        """
        lines = [
            line
            for turn in self.get_turns()
            for line in turn.lines
            if bool(line.text.strip())
        ]
        return lines

    def get_turn(self, turn_num: int) -> Optional["Turn"]:
        """
        Get the Turn object for the specified turn number.

        Parameters:
        -----------
        turn_num: int
            The turn number for which to retrieve the Turn object.

        Returns:
        --------
        Turn or None:
            The Turn object for the specified turn number, or None if it does not exist.
        """
        try:
            return self.response.turns[turn_num]
        except IndexError:
            return None

    def get_turns(self) -> list:
        """
        Get an iterable of all Turn objects in the battle.

        Returns:
        --------
        Iterable[Turn]:
            An iterable of all Turn objects in the battle.
        """
        return self.response.turns

    def get_id(self) -> str:
        """
        Get the battle ID.

        Returns:
        --------
        str:
            The battle ID.
        """
        return self.response.battle_id

    def get_format(self) -> str:
        """
        Get the battle format.

        Returns:
        --------
        str:
            The battle format.
        """
        return self.response.format

    def get_log(self) -> str:
        """
        Get the battle format.

        Returns:
        --------
        str:
            The battle format.
        """
        return self.response.log


b_format = gen9ou

b_id = "gen9ou-1954574413"

log = """
|html|<div class="broadcast-blue"><strong>[Gen 9] OU is currently suspecting Ursaluna-Bloodmoon! For information on how to participate check out the <a href="https://www.smogon.com/forums/threads/np-sv-ou-suspect-process-round-6-the-killing-moon.3728637/">suspect thread</a>.</strong></div>
|j|☆shamasha
|j|☆Xmzx
|t:|1695909875
|gametype|singles
|player|p1|shamasha|169|1338
|player|p2|Xmzx|170|1307
|teamsize|p1|6
|teamsize|p2|6
|gen|9
|tier|[Gen 9] OU
|rated|
|rule|Sleep Clause Mod: Limit one foe put to sleep
|rule|Species Clause: Limit one of each Pokémon
|rule|OHKO Clause: OHKO moves are banned
|rule|Evasion Items Clause: Evasion items are banned
|rule|Evasion Moves Clause: Evasion moves are banned
|rule|Endless Battle Clause: Forcing endless battles is banned
|rule|HP Percentage Mod: HP is shown in percentages
|clearpoke
|poke|p1|Iron Valiant|
|poke|p1|Pincurchin, F|
|poke|p1|Iron Leaves|
|poke|p1|Iron Treads|
|poke|p1|Garganacl, M|
|poke|p1|Iron Moth|
|poke|p2|Torterra, M|
|poke|p2|Dragonite, F|
|poke|p2|Corviknight, F|
|poke|p2|Heatran, F|
|poke|p2|Ogerpon-Wellspring, F|
|poke|p2|Iron Valiant|
|teampreview
|inactive|Battle timer is ON: inactive players will automatically lose when time's up. (requested by shamasha)
|
|t:|1695909903
|start
|switch|p1a: Pincurchin|Pincurchin, F|100/100
|switch|p2a: Ogerpon|Ogerpon-Wellspring, F|100/100
|-fieldstart|move: Electric Terrain|[from] ability: Electric Surge|[of] p1a: Pincurchin
|turn|1
|
|t:|1695909916
|switch|p2a: Torterra|Torterra, M|100/100
|move|p1a: Pincurchin|Thunder Wave|p2a: Torterra
|-immune|p2a: Torterra
|
|upkeep
|turn|2
|
|t:|1695909929
|move|p2a: Torterra|Headlong Rush|p1a: Pincurchin
|-supereffective|p1a: Pincurchin
|-damage|p1a: Pincurchin|0 fnt
|-unboost|p2a: Torterra|def|1
|-unboost|p2a: Torterra|spd|1
|faint|p1a: Pincurchin
|
|upkeep
|
|t:|1695909944
|switch|p1a: Iron Leaves|Iron Leaves|100/100
|-activate|p1a: Iron Leaves|ability: Quark Drive
|-start|p1a: Iron Leaves|quarkdrivespe
|turn|3
|
|t:|1695909957
|switch|p2a: Heatran|Heatran, F|100/100
|move|p1a: Iron Leaves|Psyblade|p2a: Heatran
|-resisted|p2a: Heatran
|-damage|p2a: Heatran|62/100
|-damage|p1a: Iron Leaves|91/100|[from] item: Life Orb
|
|-heal|p2a: Heatran|68/100|[from] item: Leftovers
|upkeep
|turn|4
|
|t:|1695909966
|move|p1a: Iron Leaves|Close Combat|p2a: Heatran
|-supereffective|p2a: Heatran
|-damage|p2a: Heatran|0 fnt
|-unboost|p1a: Iron Leaves|def|1
|-unboost|p1a: Iron Leaves|spd|1
|faint|p2a: Heatran
|-damage|p1a: Iron Leaves|81/100|[from] item: Life Orb
|
|upkeep
|
|t:|1695909976
|switch|p2a: Dragonite|Dragonite, F|100/100
|turn|5
|
|t:|1695909982
|-terastallize|p1a: Iron Leaves|Ice
|move|p2a: Dragonite|Extreme Speed|p1a: Iron Leaves
|-damage|p1a: Iron Leaves|27/100
|move|p1a: Iron Leaves|Tera Blast|p2a: Dragonite|[anim] Tera Blast Ice
|-supereffective|p2a: Dragonite
|-damage|p2a: Dragonite|0 fnt
|faint|p2a: Dragonite
|-damage|p1a: Iron Leaves|17/100|[from] item: Life Orb
|
|-fieldend|move: Electric Terrain
|-end|p1a: Iron Leaves|Quark Drive
|upkeep
|
|t:|1695910002
|switch|p2a: Iron Valiant|Iron Valiant, shiny|100/100
|turn|6
|
|t:|1695910011
|move|p2a: Iron Valiant|Psyshock|p1a: Iron Leaves
|-damage|p1a: Iron Leaves|0 fnt
|faint|p1a: Iron Leaves
|-end|p1a: Iron Leaves|Quark Drive|[silent]
|
|upkeep
|
|t:|1695910017
|switch|p1a: Iron Treads|Iron Treads|100/100
|-item|p1a: Iron Treads|Air Balloon
|turn|7
|
|t:|1695910027
|-end|p2a: Iron Valiant|Quark Drive|[silent]
|switch|p2a: Ogerpon|Ogerpon-Wellspring, F|100/100
|move|p1a: Iron Treads|Iron Head|p2a: Ogerpon
|-resisted|p2a: Ogerpon
|-damage|p2a: Ogerpon|74/100
|
|upkeep
|turn|8
|
|t:|1695910038
|move|p2a: Ogerpon|Ivy Cudgel|p1a: Iron Treads
|-supereffective|p1a: Iron Treads
|-damage|p1a: Iron Treads|0 fnt
|-enditem|p1a: Iron Treads|Air Balloon
|faint|p1a: Iron Treads
|-end|p1a: Iron Treads|Quark Drive|[silent]
|
|upkeep
|
|t:|1695910042
|switch|p1a: Iron Valiant|Iron Valiant|100/100
|turn|9
|
|t:|1695910045
|switch|p2a: Corviknight|Corviknight, F|100/100
|-ability|p2a: Corviknight|Pressure
|move|p1a: Iron Valiant|Thunderbolt|p2a: Corviknight
|-supereffective|p2a: Corviknight
|-damage|p2a: Corviknight|36/100
|
|-heal|p2a: Corviknight|42/100|[from] item: Leftovers
|upkeep
|turn|10
|
|t:|1695910054
|move|p1a: Iron Valiant|Thunderbolt|p2a: Corviknight
|-supereffective|p2a: Corviknight
|-damage|p2a: Corviknight|0 fnt
|faint|p2a: Corviknight
|
|upkeep
|
|t:|1695910060
|switch|p2a: Torterra|Torterra, M|100/100
|turn|11
|
|t:|1695910073
|move|p1a: Iron Valiant|Moonblast|p2a: Torterra
|-crit|p2a: Torterra
|-damage|p2a: Torterra|13/100
|move|p2a: Torterra|Shell Smash|p2a: Torterra
|-unboost|p2a: Torterra|def|1
|-unboost|p2a: Torterra|spd|1
|-boost|p2a: Torterra|atk|2
|-boost|p2a: Torterra|spa|2
|-boost|p2a: Torterra|spe|2
|
|upkeep
|turn|12
|
|t:|1695910084
|move|p2a: Torterra|Bullet Seed|p1a: Iron Valiant
|-damage|p1a: Iron Valiant|47/100
|-damage|p1a: Iron Valiant|0 fnt
|faint|p1a: Iron Valiant
|-end|p1a: Iron Valiant|Quark Drive|[silent]
|-hitcount|p1: Iron Valiant|2
|
|upkeep
|
|t:|1695910090
|switch|p1a: Iron Moth|Iron Moth|100/100
|turn|13
|
|t:|1695910095
|move|p2a: Torterra|Headlong Rush|p1a: Iron Moth
|-supereffective|p1a: Iron Moth
|-damage|p1a: Iron Moth|0 fnt
|-unboost|p2a: Torterra|def|1
|-unboost|p2a: Torterra|spd|1
|faint|p1a: Iron Moth
|-end|p1a: Iron Moth|Quark Drive|[silent]
|
|upkeep
|
|t:|1695910098
|switch|p1a: Garganacl|Garganacl, M|100/100
|turn|14
|
|t:|1695910102
|move|p1a: Garganacl|Protect|p1a: Garganacl
|-singleturn|p1a: Garganacl|Protect
|move|p2a: Torterra|Bullet Seed|p1a: Garganacl
|-activate|p1a: Garganacl|move: Protect
|
|upkeep
|turn|15
|
|t:|1695910107
|move|p2a: Torterra|Bullet Seed|p1a: Garganacl
|-supereffective|p1a: Garganacl
|-damage|p1a: Garganacl|61/100
|-supereffective|p1a: Garganacl
|-damage|p1a: Garganacl|25/100
|-supereffective|p1a: Garganacl
|-damage|p1a: Garganacl|0 fnt
|faint|p1a: Garganacl
|-hitcount|p1: Garganacl|3
|
|win|Xmzx
|raw|shamasha's rating: 1338 &rarr; <strong>1316</strong><br />(-22 for losing)
|raw|Xmzx's rating: 1307 &rarr; <strong>1329</strong><br />(+22 for winning)
|l|☆shamasha
"""
