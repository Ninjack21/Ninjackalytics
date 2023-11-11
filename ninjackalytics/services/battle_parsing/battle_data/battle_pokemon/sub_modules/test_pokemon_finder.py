import unittest

from . import PokemonFinder, Pokemon


class TestPokemonFinder(unittest.TestCase):
    def setUp(self):
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
        pf = PokemonFinder(self.full_log)
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
        pf = PokemonFinder(self.full_log)
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
        pf = PokemonFinder(self.full_log)
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

    def test_handle_zoroark(self):
        # https://replay.pokemonshowdown.com/gen9ou-1988000398
        """
        Need to handle Zoroark which won't have a typical entrance log and contains unique names in the team preview
        due to there being multiple forms (where the form is dropped once you're in the battle). Due to the weirdness
        of this 'mon and the ability disguise I'm just going to do a custom solution for now
        """
        preview = """
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
        |poke|p1|Samurott-Hisui, F|
        |poke|p1|Sandy Shocks|
        |poke|p1|Toedscruel, F|
        |poke|p1|Ogerpon-Cornerstone, F|
        |poke|p1|Corviknight, F|
        |poke|p1|Zoroark-Hisui, M|
        |poke|p2|Garganacl, F|
        |poke|p2|Infernape, F|
        |poke|p2|Cresselia, F|
        |poke|p2|Landorus-Therian, M|
        |poke|p2|Ambipom, M|
        |poke|p2|Slowbro, F|
        |teampreview
        |inactive|Battle timer is ON: inactive players will automatically lose when time's up. (requested by nikfang)
        |
        |t:|1699657703
        |start
        """
        desired_name = "Zoroark"
        finder = PokemonFinder(preview)
        found = finder.get_pokemon()
        found_names = [p.real_name for p in found]
        self.assertTrue(desired_name in found_names)

        # test case where zoroark has nickname
        log = """
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
            |poke|p1|Sneasler, F|
            |poke|p1|Zoroark-Hisui, M|
            |poke|p1|Gliscor, M|
            |poke|p1|Talonflame, F|
            |poke|p1|Grimmsnarl, M|
            |poke|p1|Greninja-*, M|
            |poke|p2|Slowking-Galar, F|
            |poke|p2|Hatterene, F|
            |poke|p2|Corviknight, M|
            |poke|p2|Manaphy|
            |poke|p2|Glimmora, M|
            |poke|p2|Landorus-Therian, M|
            |teampreview
            |inactive|Battle timer is ON: inactive players will automatically lose when time's up. (requested by Yellow rat Hunter)
            |
            |t:|1699719912
            |start
            |
            |replace|p1a: ScizorHands|Zoroark-Hisui, M
            |-end|p1a: ScizorHands|Illusion
            """
        nickname = "ScizorHands"
        finder = PokemonFinder(log)
        found = finder.get_pokemon()
        found_names = [p.real_name for p in found]
        self.assertTrue(nickname not in found_names)
        self.assertTrue(nickname in [p.nickname for p in found])

    def test_handling_of_showteam_to_ignore_it(self):
        # https://replay.pokemonshowdown.com/gen9vgc2023regulationd-1977737796
        log = """
        |gen|9
        |tier|[Gen 9] VGC 2023 Regulation D
        |rule|Species Clause: Limit one of each Pokémon
        |rule|Item Clause: Limit one of each item
        |clearpoke
        |poke|p1|Amoonguss, L50, F|
        |poke|p1|Indeedee-F, L50, F|
        |poke|p1|Armarouge, L50, M|
        |poke|p1|Ursaluna, L50, F|
        |poke|p1|Klefki, L50, F|
        |poke|p1|Decidueye, L50, M|
        |poke|p2|Iron Jugulis, L50|
        |poke|p2|Toxtricity, L50, F|
        |poke|p2|Chi-Yu, L50|
        |poke|p2|Meowscarada, L50, M|
        |poke|p2|Dondozo, L50, F|
        |poke|p2|Tatsugiri, L50, F|
        |teampreview|4
        passint0theiris has agreed to open team sheets.
        Craisans has agreed to open team sheets.
        |showteam|p1|Amoonguss||AguavBerry|Regenerator|ClearSmog,Spore,RagePowder,StompingTantrum|||F|||50|,,,,,Fairy]Indeedee-F||PsychicSeed|PsychicSurge|TrickRoom,FollowMe,DazzlingGleam,Psychic|||F|||50|,,,,,Fairy]Armarouge||LifeOrb|FlashFire|AuraSphere,TrickRoom,HeatWave,ExpandingForce|||M|||50|,,,,,Fire]Ursaluna||FlameOrb|Guts|Protect,HeadlongRush,Facade,RockSlide|||F|||50|,,,,,Ghost]Klefki||LightClay|Prankster|TrickRoom,Reflect,LightScreen,DazzlingGleam|||F|||50|,,,,,Water]Decidueye||FocusSash|Overgrow|LeafBlade,BraveBird,Protect,KnockOff|||M|||50|,,,,,Flying
        |showteam|p2|Iron Jugulis||BoosterEnergy|QuarkDrive|Tailwind,AirSlash,EarthPower,Taunt||||||50|,,,,,Ghost]Toxtricity||ThroatSpray|PunkRock|Boomburst,Protect,TeraBlast,Taunt|||F|||50|,,,,,Dark]Chi-Yu||ChoiceSpecs|BeadsofRuin|HeatWave,DarkPulse,Psychic,Snarl||||||50|,,,,,Ghost]Meowscarada||FocusSash|Protean|FlowerTrick,Uturn,Taunt,PlayRough|||M|||50|,,,,,Fairy]Dondozo||Leftovers|Unaware|OrderUp,WaveCrash,Protect,TeraBlast|||F|||50|,,,,,Grass]Tatsugiri||ToxicOrb|Commander|DracoMeteor,Endure,Protect,MuddyWater|||F|||50|,,,,,Grass
        |c|☆Craisans|glhf!
        |
        |t:|1698443913
        |start
        |turn|1
        |
        |t:|1698443972
        |-terastallize|p2a: Rockstar Made|Dark
        |move|p1a: Andromeda|Follow Me|p1a: Andromeda
        |-singleturn|p1a: Andromeda|move: Follow Me
        |move|p2b: What the Grouper?|Dark Pulse|p1a: Andromeda
        |-supereffective|p1a: Andromeda
        |-damage|p1a: Andromeda|0 fnt
        |faint|p1a: Andromeda
        |move|p2a: Rockstar Made|Tera Blast|p1b: Orion|[anim] Tera Blast Dark
        |-supereffective|p1b: Orion
        |-damage|p1b: Orion|0 fnt
        |faint|p1b: Orion
        |
        |upkeep
        |
        |t:|1698443986
        |switch|p1a: The Big Dipper|Amoonguss, L50, F|100/100
        |switch|p1b: Ursa Major|Ursaluna, L50, F|100/100
        """
        finder = PokemonFinder(log)
        found = finder.get_pokemon()
        found_names = [p.real_name for p in found]
        # now confirm that for Amoonguss the nickname The Big Dipper is found
        amoonguss = [p for p in found if "Amoonguss" in p.real_name][0]
        self.assertEqual(amoonguss.nickname, "The Big Dipper")

    def test_remove_showteam(self):
        log = """
        |gen|9
        |tier|[Gen 9] VGC 2023 Regulation D
        |rule|Species Clause: Limit one of each Pokémon
        |rule|Item Clause: Limit one of each item
        |clearpoke
        |poke|p1|Amoonguss, L50, F|
        |poke|p1|Indeedee-F, L50, F|
        |poke|p1|Armarouge, L50, M|
        |poke|p1|Ursaluna, L50, F|
        |poke|p1|Klefki, L50, F|
        |poke|p1|Decidueye, L50, M|
        |poke|p2|Iron Jugulis, L50|
        |poke|p2|Toxtricity, L50, F|
        |poke|p2|Chi-Yu, L50|
        |poke|p2|Meowscarada, L50, M|
        |poke|p2|Dondozo, L50, F|
        |poke|p2|Tatsugiri, L50, F|
        |teampreview|4
        passint0theiris has agreed to open team sheets.
        Craisans has agreed to open team sheets.
        |showteam|p1|Amoonguss||AguavBerry|Regenerator|ClearSmog,Spore,RagePowder,StompingTantrum|||F|||50|,,,,,Fairy]Indeedee-F||PsychicSeed|PsychicSurge|TrickRoom,FollowMe,DazzlingGleam,Psychic|||F|||50|,,,,,Fairy]Armarouge||LifeOrb|FlashFire|AuraSphere,TrickRoom,HeatWave,ExpandingForce|||M|||50|,,,,,Fire]Ursaluna||FlameOrb|Guts|Protect,HeadlongRush,Facade,RockSlide|||F|||50|,,,,,Ghost]Klefki||LightClay|Prankster|TrickRoom,Reflect,LightScreen,DazzlingGleam|||F|||50|,,,,,Water]Decidueye||FocusSash|Overgrow|LeafBlade,BraveBird,Protect,KnockOff|||M|||50|,,,,,Flying
        |showteam|p2|Iron Jugulis||BoosterEnergy|QuarkDrive|Tailwind,AirSlash,EarthPower,Taunt||||||50|,,,,,Ghost]Toxtricity||ThroatSpray|PunkRock|Boomburst,Protect,TeraBlast,Taunt|||F|||50|,,,,,Dark]Chi-Yu||ChoiceSpecs|BeadsofRuin|HeatWave,DarkPulse,Psychic,Snarl||||||50|,,,,,Ghost]Meowscarada||FocusSash|Protean|FlowerTrick,Uturn,Taunt,PlayRough|||M|||50|,,,,,Fairy]Dondozo||Leftovers|Unaware|OrderUp,WaveCrash,Protect,TeraBlast|||F|||50|,,,,,Grass]Tatsugiri||ToxicOrb|Commander|DracoMeteor,Endure,Protect,MuddyWater|||F|||50|,,,,,Grass
        |c|☆Craisans|glhf!
        |
        |t:|1698443913
        |start
        |turn|1
        |
        |t:|1698443972
        |-terastallize|p2a: Rockstar Made|Dark
        |move|p1a: Andromeda|Follow Me|p1a: Andromeda
        |-singleturn|p1a: Andromeda|move: Follow Me
        |move|p2b: What the Grouper?|Dark Pulse|p1a: Andromeda
        |-supereffective|p1a: Andromeda
        |-damage|p1a: Andromeda|0 fnt
        |faint|p1a: Andromeda
        |move|p2a: Rockstar Made|Tera Blast|p1b: Orion|[anim] Tera Blast Dark
        |-supereffective|p1b: Orion
        |-damage|p1b: Orion|0 fnt
        |faint|p1b: Orion
        |
        |upkeep
        |
        |t:|1698443986
        |switch|p1a: The Big Dipper|Amoonguss, L50, F|100/100
        |switch|p1b: Ursa Major|Ursaluna, L50, F|100/100
        """
        new_log = PokemonFinder(log)._remove_showteam(log)
        self.assertTrue("showteam" not in new_log)


if __name__ == "__main__":
    unittest.main()
