import unittest

from . import PokemonFinder, Pokemon


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

    def test_handle_pokemon_with_forms(self):
        """
        There is a bug currently (4/26/23) where if a pokemon has multiple forms, like Urshifu, the tool
        will consider both to be unique. Example was first found in this battle:
        https://replay.pokemonshowdown.com/gen8ou-1849244413
        """
        # only providing parts where Urshifu appeared
        log_with_urshifu = """
        |gen|8
        |poke|p1|Urshifu-*, M|
        |start
        |switch|p1a: Urshifu|Urshifu-Rapid-Strike, M|100/100|[from] U-turn
        |switch|p1a: Urshifu|Urshifu-Rapid-Strike, M|53/100
        """
        finder = PokemonFinder(log_with_urshifu)
        expected_mon_real_name = "Urshifu-Rapid-Strike"
        expected_pnum = 1

        # only expect 1 pokemon to be found
        self.assertEqual(len(finder.get_pokemon()), 1)

        mon = finder.get_pokemon()[0]

        self.assertEqual(mon.real_name, expected_mon_real_name)
        self.assertEqual(mon.player_num, expected_pnum)


if __name__ == "__main__":
    unittest.main()
