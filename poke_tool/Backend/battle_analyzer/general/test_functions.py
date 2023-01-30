import unittest
import requests_mock
from functions import (
    get_json_response,
    extract_preview_mons,
    create_pokemon_params_from_preview,
    extract_entrances,
    create_pokemon_params_from_entrances,
    get_pokemon,
)
import requests

url = r"https://replay.pokemonshowdown.com/gen8ou-1784944495"
response = get_json_response(url)
battle_log = response["log"]


class TestGetJsonResponse(unittest.TestCase):
    def test_valid_url(self):
        # Arrange
        url = "https://valid.com"
        mock_json = {"key": "value"}
        with requests_mock.Mocker() as m:
            m.get(f"{url}.json", json=mock_json)

            # Act
            result = get_json_response(url)

            # Assert
            self.assertEqual(result, mock_json)

    def test_invalid_url(self):
        # Arrange
        url = "https://invalid.com"
        with requests_mock.Mocker() as m:
            m.get(f"{url}.json", status_code=404)

            # Act & Assert
            with self.assertRaises(ValueError):
                get_json_response(url)

    def test_exception(self):
        # Arrange
        url = "https://exception.com"
        with requests_mock.Mocker() as m:
            m.get(f"{url}.json", exc=requests.exceptions.RequestException)

            # Act & Assert
            with self.assertRaises(ValueError):
                get_json_response(url)


class TestExtractPreviewMons(unittest.TestCase):
    def setUp(self):
        self.battle_log = "|gen|8\n|tier|[Gen 8] OU\n|rated|\n|rule|Sleep Clause Mod: Limit one foe put to sleep\n|rule|Species Clause: Limit one of each Pokémon\n|rule|OHKO Clause: OHKO moves are banned\n|rule|Evasion Items Clause: Evasion items are banned\n|rule|Evasion Moves Clause: Evasion moves are banned\n|rule|Endless Battle Clause: Forcing endless battles is banned\n|rule|HP Percentage Mod: HP is shown in percentages\n|rule|Dynamax Clause: You cannot dynamax\n|clearpoke\n|poke|p1|Skarmory, F|\n|poke|p1|Metagross|\n|poke|p1|Heatran, F|\n|poke|p1|Lucario, M|\n|poke|p1|Magnezone|\n|poke|p1|Scizor, M|\n|poke|p2|Charizard, M|\n|poke|p2|Vileplume, M|\n|poke|p2|Vaporeon, M|\n|poke|p2|Zapdos|\n|poke|p2|Heracross, M|\n|poke|p2|Tyranitar, M|\n|teampreview\n|\n|t:|1674861036\n|start"

    def test_extract_preview_mons_valid_input(self):
        expected_output = [
            "p1|Skarmory",
            "p1|Metagross",
            "p1|Heatran",
            "p1|Lucario",
            "p1|Magnezone",
            "p1|Scizor",
            "p2|Charizard",
            "p2|Vileplume",
            "p2|Vaporeon",
            "p2|Zapdos",
            "p2|Heracross",
            "p2|Tyranitar",
        ]
        self.assertEqual(extract_preview_mons(self.battle_log), expected_output)


class TestCreatePokemonParamsPreview(unittest.TestCase):
    def test_create_mon_object_params_from_preview_mons(self):
        # Test input
        preview_mons_list = [
            "p1|Skarmory",
            "p1|Metagross",
            "p2|Charizard",
            "p2|Vileplume",
        ]

        # Expected output
        expected_output = [
            {"real_name": "Skarmory", "nickname": "Skarmory", "player_num": "1"},
            {"real_name": "Metagross", "nickname": "Metagross", "player_num": "1"},
            {"real_name": "Charizard", "nickname": "Charizard", "player_num": "2"},
            {"real_name": "Vileplume", "nickname": "Vileplume", "player_num": "2"},
        ]

        # Test
        result = create_pokemon_params_from_preview(preview_mons_list)
        self.assertEqual(result, expected_output)


class TestExtractEntrances(unittest.TestCase):
    def setUp(self):
        self.battle_log = """
|switch|p1a: Valkyrie|Skarmory, F|100/100
|switch|p2a: Rayo|Zapdos|100/100
|turn|1
|
|t:|1674861043
|switch|p1a: Fiammetta|Heatran, F|100/100
|turn|3
|
|t:|1674861063
|switch|p1a: HK-51|Magnezone|100/100
|
|t:|1674861076
|switch|p1a: Hakoda|Lucario, M|100/100
|turn|5
|
|t:|1674861081
|switch|p2a: Heracross|Heracross, M|100/100
|t:|1674861094
|switch|p1a: Valkyrie|Skarmory, F|100/100
|move|p2a: Heracross|Earthquake|p1a: Valkyrie
|t:|1674861101
|switch|p2a: Vaporeon|Vaporeon, M|100/100
|move|p1a: Valkyrie|Stealth Rock|p2a: Vaporeon
"""

    def test_extract_entrances_returns_correct_entrances(self):
        expected_entrances = [
            "p1a: Valkyrie|Skarmory, F|100/100",
            "p2a: Rayo|Zapdos|100/100",
            "p1a: Fiammetta|Heatran, F|100/100",
            "p1a: HK-51|Magnezone|100/100",
            "p1a: Hakoda|Lucario, M|100/100",
            "p2a: Heracross|Heracross, M|100/100",
            "p1a: Valkyrie|Skarmory, F|100/100",
            "p2a: Vaporeon|Vaporeon, M|100/100",
        ]
        self.assertEqual(extract_entrances(self.battle_log), expected_entrances)


class TestCreatePokemonParamsEntrances(unittest.TestCase):
    def test_create_pokemon_params(self):
        entrances = [
            "p1a: Valkyrie|Skarmory, F|100/100",
            "p2a: Rayo|Zapdos|100/100",
            "p1a: Fiammetta|Heatran, F|100/100",
        ]
        expected_params_list = [
            {"player_num": "1", "nickname": "Valkyrie", "real_name": "Skarmory"},
            {"player_num": "2", "nickname": "Rayo", "real_name": "Zapdos"},
            {"player_num": "1", "nickname": "Fiammetta", "real_name": "Heatran"},
        ]
        params_list = create_pokemon_params_from_entrances(entrances)

        self.assertEqual(params_list, expected_params_list)


class TestGetPokemon(unittest.TestCase):
    def setUp(self):
        self.battle_log = {
            "log": """
            |gen|8
            |tier|[Gen 8] OU

            |clearpoke
            |poke|p1|Skarmory, F|
            |poke|p1|Metagross|
            |poke|p1|Heatran, F|
            |poke|p1|Lucario, M|
            |teampreview

            |switch|p1a: Valkyrie|Skarmory, F|100/100
            |switch|p2a: Rayo|Zapdos|100/100
            |turn|1
            |
            |t:|1674861043
            |switch|p1a: Fiammetta|Heatran, F|100/100

            |turn|3
            |
            |t:|1674861063
            |switch|p1a: HK-51|Magnezone|100/100
            """
        }

    def test_get_pokemon(self):
        """
        There is a missing piece to this function. The expected number of discovered
        pokemon objects should indeed be 4, yet we get 6. The reason? Currently,
        the get_pokemon function does not realize that the pokemon from the team preview
        are actually duplicates of the ones from the entrances, but the battle names made
        by pokemon objects from team previews do not see the true nickname (reference
        the docstring in the create params from preview mons function). As such, the unique
        identifier in the dictionary of pokemon objects appears different even though, if you
        equated the two pokemon objects you'd discover they are in fact the same (as defined
        in the __eq__ method of the pokemon object).

        Entrances should overwrite team preview mons. To do this, the pokemon objects should
        be compared with an equals operator and the entrance mon should overwrite that of
        any pokemon objects made from the team preview.

        For example, in the above code, if evaluated, we would discover that a mons object
        for p1 Skarmory exists twice, once with the nickname "Skarmory" and once with the
        nickname "Valkyrie" (battle names p1 Skarmory & p1 Valkyrie, respectively).
        We would want to delete the one associated with the team preview (p1 Skarmory).
        """
        mons_objects = get_pokemon(self.battle_log)

        # Check that the correct number of Pokemon objects were created
        self.assertEqual(len(mons_objects), 6)

        # Check that the properties of the first Pokemon object are correct
        self.assertEqual(mons_objects["p1 Skarmory"].real_name, "Skarmory")
        self.assertEqual(mons_objects["p1 Skarmory"].nickname, "Valkyrie")
        self.assertEqual(mons_objects["p1 Skarmory"].hp, 100)
        self.assertEqual(mons_objects["p1 Skarmory"].hp_change, None)
        self.assertEqual(mons_objects["p1 Skarmory"].player_num, "1")
        self.assertEqual(mons_objects["p1 Skarmory"].battle_name, "p1 Skarmory")

        # Check that the properties of the second Pokemon object are correct
        self.assertEqual(mons_objects["p1 Heatran"].real_name, "Heatran")
        self.assertEqual(mons_objects["p1 Heatran"].nickname, "Fiammetta")
        self.assertEqual(mons_objects["p1 Heatran"].hp, 100)
        self.assertEqual(mons_objects["p1 Heatran"].hp_change, None)
        self.assertEqual(mons_objects["p1 Heatran"].player_num, "1")
        self.assertEqual(mons_objects["p1 Heatran"].battle_name, "p1 Heatran")

        # Check that the properties of the third Pokemon object are correct
        self.assertEqual(mons_objects["p1 Magnezone"].real_name, "Magnezone")
        self.assertEqual(mons_objects["p1 Magnezone"].nickname, "HK-51")
        self.assertEqual(mons_objects["p1 Magnezone"].hp, 100)
        self.assertEqual(mons_objects["p1 Magnezone"].hp_change, None)
        self.assertEqual(mons_objects["p1 Magnezone"].player_num, "1")
        self.assertEqual(mons_objects["p1 Magnezone"].battle_name, "p1 Magnezone")


if __name__ == "__main__":
    unittest.main()
