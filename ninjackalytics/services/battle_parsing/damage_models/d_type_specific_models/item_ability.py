from typing import Dict, Tuple, List
import re
import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.damage_models.d_type_specific_models import (
    DamageDataFinder,
    BattlePokemon,
    Turn,
    Battle,
)


class ItemAbilityDataFinder(DamageDataFinder):
    def __init__(self, battle_pokemon: BattlePokemon):
        super().__init__(battle_pokemon)

    def get_damage_data(
        self, event: str, turn: Turn, battle: Battle = None
    ) -> Dict[str, str]:
        """
        Get the damage data from an item or ability event.

        Parameters:
        -----------
        event: str
            The item or ability event.
        turn: Turn
            The turn the event occurred on.

        Returns:
        --------
        Dict[str, str]:
            The damage data from the item or ability event.
        ---
        """
        damage_dict = {}

        dealer_pnum, dealer = self._get_dealer(event)
        damage_dict["Dealer"] = dealer
        damage_dict["Dealer_Player_Number"] = dealer_pnum

        receiver_pnum, receiver = self._get_receiver(event)
        damage_dict["Receiver"] = receiver
        damage_dict["Receiver_Player_Number"] = receiver_pnum

        source_name = self._get_source_name(event)
        damage_dict["Source_Name"] = source_name

        # need raw receiver for _get_hp_change
        receiver_raw_name = event.split("|")[2]
        hp_change = self._get_hp_change(event, receiver_raw_name)
        damage_dict["Damage"] = abs(hp_change)

        damage_dict["Type"] = self._get_damage_source(event)
        damage_dict["Turn"] = turn.number

        return damage_dict

    def _get_source_name(self, event: str) -> str:
        # should see at least 5 elements when split by "|" for an item or ability event
        if len(event.split("|")) < 5:
            raise ValueError(f"Event does not appear to be item or ability: {event}")
        return event.split("|")[4].split(": ")[1]

    def _get_dealer(self, event: str) -> Tuple[int, str]:
        line_pattern = (
            "[^\|]+"  # this breaks out a line into its key parts by "|" dividers
        )
        dmg_line = re.findall(line_pattern, event)
        if len(dmg_line) == 5:  # this indicates [of] exists : which tells dealer mon
            dealer_raw_name = dmg_line[4].split("[of] ")[1]
            return self.battle_pokemon.get_pnum_and_name(dealer_raw_name)
        else:  # if no 5th element, then dealer is source name, pnum assumed same as receiver
            pnum, name = self._get_receiver(event)
            return (pnum, self._get_source_name(event))

    def _get_damage_source(self, event: str) -> str:
        if "item" in event:
            return "Item"
        elif "ability" in event:
            return "Ability"
        else:
            raise ValueError(f"Invalid event: {event}")
