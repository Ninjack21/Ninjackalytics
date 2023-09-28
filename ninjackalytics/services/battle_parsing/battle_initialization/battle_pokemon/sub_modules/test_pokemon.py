import unittest
from unittest.mock import patch, Mock, MagicMock

from .pokemon import Pokemon


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
        pokemon2 = Pokemon("Venusaur, F", "Venus", 3)
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


if __name__ == "__main__":
    unittest.main()
