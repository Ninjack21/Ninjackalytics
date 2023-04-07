import unittest
from unittest.mock import patch, Mock, MagicMock
from models import PokemonFinder, Pokemon, BattlePokemon, Team


class TestPokemonFinder(unittest.TestCase):
    def setUp(self):
        self.log = "example log"
        self.preview_log = """
        |gen|9
        |poke|p1|Baxcalibur, F|
        |poke|p1|Weavile, F|
        |poke|p1|Espeon, M|
        |poke|p1|Palossand, M|
        |poke|p1|Wo-Chien|
        |poke|p1|Bellibolt, F|
        |poke|p2|Corviknight, M|
        |poke|p2|Iron Thorns|
        |poke|p2|Charizard, M|
        |poke|p2|Grafaiai, F|
        |poke|p2|Flamigo, M|
        |poke|p2|Rotom-Frost|
        |teampreview
        |
        |t:|1677443521
        |start
        """
        self.entrance_log = """
        |start
        |switch|p1a: Espeon|Espeon, M|100/100
        |switch|p2a: Corviknight|Corviknight, M, shiny|100/100
        |-ability|p2a: Corviknight|Pressure
        |turn|1
        """
        self.full_log = """
        |gen|9
        |poke|p1|Baxcalibur, F|
        |poke|p1|Weavile, F|
        |poke|p1|Espeon, M|
        |poke|p1|Palossand, M|
        |poke|p1|Wo-Chien|
        |poke|p1|Bellibolt, F|
        |poke|p2|Corviknight, M|
        |poke|p2|Iron Thorns|
        |poke|p2|Charizard, M|
        |poke|p2|Grafaiai, F|
        |poke|p2|Flamigo, M|
        |poke|p2|Rotom-Frost|
        |teampreview
        |
        |t:|1677443521
        |start
        |switch|p1a: Esp-nickname|Espeon, M|100/100
        |switch|p2a: Corv-nickname|Corviknight, M, shiny|100/100
        |-ability|p2a: Corviknight|Pressure
        |turn|1
        """

    def test_init(self):
        pf = PokemonFinder(self.log)
        self.assertEqual(pf.log, self.log)

    def test_extract_previews(self):
        pf = PokemonFinder(self.preview_log)
        expected_output = [
            {"player_num": "1", "real_name": "Baxcalibur"},
            {"player_num": "1", "real_name": "Weavile"},
            {"player_num": "1", "real_name": "Espeon"},
            {"player_num": "1", "real_name": "Palossand"},
            {"player_num": "1", "real_name": "Wo-Chien"},
            {"player_num": "1", "real_name": "Bellibolt"},
            {"player_num": "2", "real_name": "Corviknight"},
            {"player_num": "2", "real_name": "Iron Thorns"},
            {"player_num": "2", "real_name": "Charizard"},
            {"player_num": "2", "real_name": "Grafaiai"},
            {"player_num": "2", "real_name": "Flamigo"},
            {"player_num": "2", "real_name": "Rotom-Frost"},
        ]
        self.assertEqual(pf._extract_previews(self.preview_log), expected_output)

    def test_extract_entrances(self):
        pf = PokemonFinder(self.entrance_log)
        expected_output = [
            {"player_num": "1", "real_name": "Espeon, M", "nickname": "Espeon"},
            {
                "player_num": "2",
                "real_name": "Corviknight, M, shiny",
                "nickname": "Corviknight",
            },
        ]
        self.assertEqual(pf._extract_entrances(self.entrance_log), expected_output)

    def test_create_pokemon_parameters(self):
        pf = PokemonFinder(self.log)
        pokemon_found = [
            {"player_num": "1", "real_name": "charizard"},
            {"player_num": "2", "nickname": "pikachu", "real_name": "PIKACHU"},
        ]
        expected_output = [
            {"player_num": "1", "nickname": "charizard", "real_name": "charizard"},
            {"player_num": "2", "nickname": "pikachu", "real_name": "PIKACHU"},
        ]
        self.assertEqual(pf._create_pokemon_parameters(pokemon_found), expected_output)

    def test_create_pokemon_objects(self):
        pf = PokemonFinder(self.log)
        pokemon_params = [
            {"player_num": "1", "nickname": "charizard", "real_name": "charizard"},
            {"player_num": "2", "nickname": "pikachu", "real_name": "PIKACHU"},
        ]
        expected_output = [
            Pokemon(
                real_name="charizard",
                nickname="charizard",
                hp=100,
                hp_change=None,
                player_num="1",
            ),
            Pokemon(
                real_name="PIKACHU",
                nickname="pikachu",
                hp=100,
                hp_change=None,
                player_num="2",
            ),
        ]
        self.assertEqual(pf._create_pokemon_objects(pokemon_params), expected_output)

    def test_remove_duplicates(self):
        pf = PokemonFinder(self.log)
        mons = [
            Pokemon(
                real_name="charizard",
                nickname="charizard",
                hp=100,
                hp_change=None,
                player_num="1",
            ),
            Pokemon(
                real_name="PIKACHU",
                nickname="pikachu",
                hp=100,
                hp_change=None,
                player_num="2",
            ),
            Pokemon(
                real_name="PIKACHU",
                nickname="pikachu",
                hp=100,
                hp_change=None,
                player_num="2",
            ),
        ]

        found = pf._remove_duplicates(mons)

        self.assertTrue(len(found) == 2)

    def test_get_pokemon(self):
        expected_output = [
            Pokemon(real_name="Baxcalibur", nickname="Baxcalibur", player_num="1"),
            Pokemon(real_name="Weavile", nickname="Weavile", player_num="1"),
            Pokemon(real_name="Espeon", nickname="Esp-nickname", player_num="1"),
            Pokemon(real_name="Palossand", nickname="Palossand", player_num="1"),
            Pokemon(real_name="Wo-Chien", nickname="Wo-Chien", player_num="1"),
            Pokemon(real_name="Bellibolt", nickname="Bellibolt", player_num="1"),
            Pokemon(real_name="Corviknight", nickname="Corv-nickname", player_num="2"),
            Pokemon(real_name="Iron Thorns", nickname="Iron Thorns", player_num="2"),
            Pokemon(real_name="Charizard", nickname="Charizard", player_num="2"),
            Pokemon(real_name="Grafaiai", nickname="Grafaiai", player_num="2"),
            Pokemon(real_name="Flamigo", nickname="Flamigo", player_num="2"),
            Pokemon(real_name="Rotom-Frost", nickname="Rotom-Frost", player_num="2"),
        ]

        finder = PokemonFinder(self.full_log)
        output = finder.get_pokemon()
        output_real_names = [p.real_name for p in output]
        expected_output_real_names = [p.real_name for p in expected_output]

        missing = [
            mon.real_name
            for mon in expected_output
            if mon.real_name not in output_real_names
        ]
        self.assertTrue(len(missing) == 0)

        extras = [
            mon.real_name
            for mon in output
            if mon.real_name not in expected_output_real_names
        ]
        self.assertTrue(len(extras) == 0)


class TestPokemon(unittest.TestCase):
    def test_pokemon_creation(self):
        pokemon = Pokemon("Charizard, M", "Charity", 1, hp=75, hp_change=-15)
        self.assertEqual(pokemon.real_name, "Charizard")
        self.assertEqual(pokemon.nickname, "Charity")
        self.assertEqual(pokemon.player_num, 1)
        self.assertEqual(pokemon.hp, 75)
        self.assertEqual(pokemon.hp_change, -15)

    def test_pokemon_update_hp(self):
        pokemon = Pokemon("Pikachu, F", "Sparky", 2, hp=100)
        pokemon.update_hp(80)
        self.assertEqual(pokemon.hp, 80)
        self.assertEqual(pokemon.hp_change, -20)

    def test_pokemon_equality(self):
        pokemon1 = Pokemon("Venusaur, F", "Venus", 3)
        pokemon2 = Pokemon("Venusaur, M", "Vinny", 3)
        pokemon3 = Pokemon("Blastoise, F", "Blasty", 2)
        self.assertEqual(pokemon1, pokemon2)
        self.assertNotEqual(pokemon1, pokemon3)

    def test_check_if_name_is_self(self):
        pokemon = Pokemon("Espeon", "Espeon", 1)
        raw_name = "p1a: Espeon"
        self.assertTrue(pokemon.check_if_name_is_self(raw_name))

        raw_name = "p1a: Vaporeon"
        self.assertFalse(pokemon.check_if_name_is_self(raw_name))

        raw_name = "p2a: Espeon"
        self.assertFalse(pokemon.check_if_name_is_self(raw_name))


class TestBattlePokemon(unittest.TestCase):
    def setUp(self):
        # Set up a mock battle object
        self.mock_battle = MagicMock()
        self.mock_battle.get_log.return_value = """
            |gen|9
            |poke|p1|Baxcalibur, F|
            |poke|p1|Weavile, F|
            |poke|p1|Espeon, M|
            |poke|p1|Palossand, M|
            |poke|p1|Wo-Chien|
            |poke|p1|Bellibolt, F|
            |poke|p2|Corviknight, M|
            |poke|p2|Iron Thorns|
            |poke|p2|Charizard, M|
            |poke|p2|Grafaiai, F|
            |poke|p2|Flamigo, M|
            |poke|p2|Rotom-Frost|
            |teampreview
            |
            |t:|1677443521
            |start
            |switch|p1a: Esp-nickname|Espeon, M|100/100
            |switch|p2a: Corv-nickname|Corviknight, M, shiny|100/100
            |-ability|p2a: Corviknight|Pressure
            |turn|1
            """

    def test_create_teams(self):
        bp = BattlePokemon(self.mock_battle)
        teams = bp.teams
        self.assertEqual(len(teams), 2)

        # Check that the teams contain the correct Pokemon objects
        alice_team = [p for p in bp.pokemon if p.player_num == 1]
        bob_team = [p for p in bp.pokemon if p.player_num == 2]
        self.assertEqual(len(teams[0].pokemon), len(alice_team))
        self.assertEqual(len(teams[1].pokemon), len(bob_team))

        for i, mon in enumerate(alice_team):
            self.assertEqual(mon, teams[0].pokemon[i])
        for i, mon in enumerate(bob_team):
            self.assertEqual(mon, teams[1].pokemon[i])

    def test_get_mon_obj(self):
        bp = BattlePokemon(self.mock_battle)

        # Test getting a valid Pokemon object
        mon = bp.get_mon_obj("p2a: Charizard")
        self.assertIsInstance(mon, Pokemon)
        self.assertEqual(mon.real_name, "Charizard")
        self.assertEqual(mon.nickname, "Charizard")
        self.assertEqual(mon.player_num, 2)

        # Test getting a non-existent Pokemon object
        with self.assertRaises(ValueError):
            bp.get_mon_obj("p1a: Blastoise")

    def test_update_hp_for_pokemon(self):
        bp = BattlePokemon(self.mock_battle)
        bp.update_hp_for_pokemon("p2a: Charizard", 75.0)

        self.assertEqual(bp.get_pokemon_current_hp("p2a: Charizard"), 75.0)

    def test_get_pokemon_hp_change(self):
        bp = BattlePokemon(self.mock_battle)
        bp.update_hp_for_pokemon("p2a: Charizard", 75.0)

        self.assertEqual(bp.get_pokemon_hp_change("p2a: Charizard"), -25)

    def test_get_pokemon_current_hp(self):
        bp = BattlePokemon(self.mock_battle)

        self.assertEqual(bp.get_pokemon_current_hp("p2a: Charizard"), 100)

        bp.update_hp_for_pokemon("p2a: Charizard", 75.0)

        self.assertEqual(bp.get_pokemon_current_hp("p2a: Charizard"), 75.0)

    def test_get_pnum_and_name(self):
        bp = BattlePokemon(self.mock_battle)

        raw_name = "p1a: Esp-nickname"
        pnum, name = bp.get_pnum_and_name(raw_name)

        expected_pnum = 1
        expected_name = "Espeon"

        self.assertEqual(pnum, expected_pnum)
        self.assertEqual(name, expected_name)


if __name__ == "__main__":
    unittest.main()
