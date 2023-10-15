class MockBattlePokemon:
    def __init__(self):
        self.mon_hps = {}
        self.mon_hp_changes = {}

    # quick implementation for testing
    def get_pnum_and_name(self, raw_name):
        """
        example raw_name = 'p1a: May Day Parade'
        """
        pnum_split_name = raw_name.split(": ")
        pnum = int(pnum_split_name[0][1])
        name = pnum_split_name[1]
        return pnum, name

    def update_hp_for_pokemon(self, raw_name: str, new_hp: float) -> None:
        # assumes not called before get_current_hp, which inits mon_hps
        current_hp = self.get_pokemon_current_hp(raw_name)
        self.mon_hp_changes[raw_name] = new_hp - current_hp
        self.mon_hps[raw_name] = new_hp

    def get_pokemon_hp_change(self, raw_name: str) -> float:
        # assumes not called before get_current_hp, which inits mon_hps
        return self.mon_hp_changes[raw_name]

    def get_pokemon_current_hp(self, raw_name: str) -> float:
        if not raw_name in self.mon_hps:
            self.mon_hps[raw_name] = 100.0
        return self.mon_hps[raw_name]


class MockTurn:
    def __init__(self, number: int, text: str):
        self.number = number
        self.text = text


class MockBattle:
    def __init__(self):
        turns = []

    # quick implementation for testing
    def get_turns(self) -> list:
        return self.turns


# =================== useful functions for testing ===================
def strip_leading_spaces(text: str) -> str:
    return "\n".join(line.lstrip() for line in text.strip().split("\n"))
