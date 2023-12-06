import unittest
from .team import Team
from .pokemon import Pokemon


class TestTeam(unittest.TestCase):
    def test_verify_mon_names(self):
        # Create a list of Pokemon objects with valid names
        pokemon_list = [
            Pokemon("Pikachu", "Pika", 1),
            Pokemon("Charizard", "Char", 1),
            Pokemon("Bulbasaur", "Bulba", 1),
        ]

        # Create a Team object with the list of Pokemon
        team = Team(pokemon_list)

        # Verify that no ValueError is raised
        self.assertIsNone(team._verify_mon_names())

        # Create a list of Pokemon objects with invalid names
        pokemon_list = [
            Pokemon("Pikachu|", "Pika", 1),
            Pokemon("Charizard", "Char|", 1),
            Pokemon("Bulbasaur|", "Bulba|", 1),
        ]

        # Verify that a ValueError is raised with the correct error message
        with self.assertRaises(ValueError) as context:
            # Create a Team object with the list of Pokemon
            team = Team(pokemon_list)
        self.assertEqual(
            str(context.exception),
            "Pokemon names cannot contain '|' --> Pokemon: real_name: Pikachu| | nickname: Pika",
        )


if __name__ == "__main__":
    unittest.main()
