import re

from . import Pokemon


class PokemonFinder:
    def __init__(self, log: str):
        """
        Initialize PokemonFinder object.

        Parameters
        ----------
        log : str
            The battle log string to extract Pokemon data from.
        """
        self.log = self._remove_showteam(log)

    def get_pokemon(self) -> list:
        """
        Extract and return a list of Pokemon objects found in the log.

        Returns
        -------
        list
            A list of Pokemon objects
        """
        preview_mons = self._extract_previews(self.log)
        # look to see if Zoroark is in the real name of any of the preview mons and if so, update the real name
        # to be only 'Zoroark' (thus stripping any forms associated) since it will only say Zoroark in battle.
        # handling custom here because of weirdness of this mon
        for mon in preview_mons:
            if "Zoroark" in mon["real_name"]:
                mon["real_name"] = "Zoroark"
                self._deal_with_zoroark_family(mon)
            elif "Zorua" in mon["real_name"]:
                mon["real_name"] = "Zorua"
                self._deal_with_zoroark_family(mon)
        entrance_mons = self._extract_entrances(self.log)
        pokemon_parameters = self._create_pokemon_parameters(
            preview_mons + entrance_mons
        )
        mons = self._create_pokemon_objects(pokemon_parameters)
        return self._remove_duplicates(mons)

    def _extract_previews(self, battle_log: str) -> list:
        """
        Extract and return a list of Pokemon data from the log preview.

        Parameters
        ----------
        battle_log : str
            The battle log string to extract Pokemon data from.

        Returns
        -------
        list
            A list of dictionaries, with each dictionary containing the real name and player number of a
            Pokemon.
        """
        try:
            preview = battle_log.split("|gen")[1].split("|start")[0]
            team_preview_pattern = (
                r"p(?P<player_num>[1-4]+)" + r"\|(?P<real_name>[A-z| |-]+[^,|\-*|\n])"
            )

            return [
                match.groupdict()
                for match in re.finditer(team_preview_pattern, preview)
            ]

        except IndexError:
            return []

    def _extract_entrances(self, battle_log: str) -> list:
        """
        Extract and return a list of Pokemon data from the log entrances.

        Parameters
        ----------
        battle_log : str
            The battle log string to extract Pokemon data from.

        Returns
        -------
        list
            A list of dictionaries, with each dictionary containing the real name, nickname, and
            player number of a Pokemon.
        """
        pattern = (
            r"p(?P<player_num>[1-4]){1}[a-c]{1}: "
            + r"(?P<nickname>.*)\|"
            + r"(?P<real_name>[A-Z]+[a-z]+.+)\|[0-9]+\/[0-9]+"
        )
        return [match.groupdict() for match in re.finditer(pattern, battle_log)]

    def _create_pokemon_parameters(self, pokemon_found: list) -> list:
        """
        Extract and return a list of dictionaries containing Pokemon parameters.

        Parameters
        ----------
        pokemon_found : list
            A list of dictionaries containing the real name, nickname, and player number of a Pokemon.

        Returns
        -------
        list
            A list of dictionaries, with each dictionary containing the real name, nickname, and player number of a Pokemon.
        """
        return [
            {
                "real_name": match.get("real_name"),
                "nickname": match.get("real_name"),
                "player_num": match.get("player_num"),
            }
            if not match.get("nickname")
            else match
            for match in pokemon_found
        ]

    def _create_pokemon_objects(self, pokemon_params: list) -> dict:
        """
        Create and return a dictionary of Pokemon objects.

        Parameters
        ----------
        pokemon_object_params : list
            A list of dictionaries containing Pokemon parameters.

        Returns
        -------
            A list of Pokemon objects
        """
        return [Pokemon(**pokemon_param) for pokemon_param in pokemon_params]

    def _remove_duplicates(self, mons: list) -> list:
        """
        Return a list of unique Pokemon objects - giving priority to those with nicknames

        Paramters
        ---------
        mons : list
            A list of all Pokemon objects found - even duplicates found in the team preview and in the
            entrances.

        Returns
        -------
            A list of unique Pokemon objects
        """
        nicknamed_mons = [mon for mon in mons if mon.nickname != mon.real_name]
        other_mons = [mon for mon in mons if mon not in nicknamed_mons]

        nicknamed_mons = list(set(nicknamed_mons))  # ensure no duplicates exist
        other_mons = list(set(other_mons))  # ensure no duplicates exist

        unique_mons = nicknamed_mons + other_mons
        form_handled_mons = self._handle_pokemon_with_multiple_forms(unique_mons)

        return form_handled_mons

    def _handle_pokemon_with_multiple_forms(self, mons: list) -> list:
        """
        Handle Pokemon with multiple forms.

        Parameters
        ----------
        mons : list
            A list of Pokemon objects.

        Returns
        -------
        list
            A list of Pokemon objects with unidentified forms from the preview removed if the
            identified form appears in the entrances.

        Example
        -------
        Preview: Urshifu-*
        Entrance: Urshifu-Rapid-Strike
        """
        unique_mons = []
        for mon in mons:
            other_mons = [other_mon for other_mon in mons if other_mon != mon]
            full_form_names = [
                possible_full_form
                for possible_full_form in other_mons
                if mon.real_name
                in possible_full_form.real_name  # Urshifu in Urshifu-Rapid-Strike
                and possible_full_form.player_num
                == mon.player_num  # ensure same player
            ]
            if len(full_form_names) == 0:
                # this means the current mon's name was not a smaller part of another mon's name
                # which would indicate the current mon is actually the preview mon's unidentified form
                unique_mons.append(mon)

        return unique_mons

    def _deal_with_zoroark_family(self, mon: Pokemon) -> list:
        """
        Handle Zoroark.

        Parameters
        ----------
        mon : Pokemon
            the pokemon object for zoroark/zorua

        Returns
        -------
        list
            A list of Pokemon objects with Zoroark's forms removed.

        Example
        -------
        |replace|p1a: ScizorHands|Zoroark-Hisui, M
        |-end|p1a: ScizorHands|Illusion
        """
        # now need to see if a nickname existed for it. look for the nickname in the unique
        # zoroark entrances
        pattern = (
            r"\|replace\|p[1-4][a-d]: (?P<nickname>[^\|]*)\|(?P<real_name>[^\|]*)\n"
        )
        matches = re.findall(pattern, self.log)
        # use the first match since this will show up the earliest. I'm not sure if it always follows the above pattern
        # or not
        if len(matches) > 0:
            match1 = matches[0]
            nickname = match1[0]
            # update mon object nickname
            mon["nickname"] = nickname

    def _remove_showteam(self, log: str) -> str:
        """
        Remove the showteam portion of the log.

        Parameters
        ----------
        log : str
            The battle log string to extract Pokemon data from.

        Returns
        -------
        str
            The battle log string with the showteam portion removed.
        """
        preview = log.split("|teampreview")[0]
        battle = log.split("|start")[1]
        battle = "|start" + battle
        new_log = preview + "\n" + battle
        return new_log
