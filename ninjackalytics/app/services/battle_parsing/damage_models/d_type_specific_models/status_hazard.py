from typing import Dict, Tuple, List, Protocol
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


class StatusHazardDataFinder(DamageDataFinder):
    def __init__(self, battle_pokemon: BattlePokemon):
        super().__init__(battle_pokemon)
        self.statuses = ["tox", "psn", "brn"]
        self.hazards = ["Stealth Rock", "Spikes", "G-Max Steelsurge"]

    def get_damage_data(
        self, event: str, turn: Turn, battle: Battle = None
    ) -> Dict[str, str]:
        """
        Get the damage data from a status or hazard event.

        Parameters:
        -----------
        event: str
            The status or hazard event
        turn: Turn
            The turn the event occurred on.

        Returns:
        --------
        Dict[str, str]:
            The damage data from the status or hazard event.
        ---
        """
        damage_dict = {}

        damage_dict["Type"] = self._get_damage_source(event)
        source_name = self._get_source_name(event)

        dealer_pnum, dealer = self._get_dealer(event)
        damage_dict["Dealer"] = dealer
        damage_dict["Dealer_Player_Number"] = dealer_pnum

        receiver_pnum, receiver = self._get_receiver(event)
        damage_dict["Receiver"] = receiver
        damage_dict["Receiver_Player_Number"] = receiver_pnum

        damage_dict["Source_Name"] = source_name

        hp_change = self._get_hp_change(event, receiver)
        damage_dict["Damage"] = abs(hp_change)

        damage_dict["Turn"] = turn.number

        return damage_dict

    def _get_source_name(self, event: str) -> str:
        # in this circumstance, dealer and source name are the same
        _, source_name = self._get_dealer(event)
        return source_name

    def _get_dealer(self, event: str) -> Tuple[int, str]:
        """
        Example Events:
        ---------------
        |-damage|p2a: Ferrothorn|94/100|[from] Stealth Rock
        |-damage|p1a: Rillaboom|94/100 tox|[from] psn
        """
        # dealer will be based on the part after [from] except where tox is found

        # get the player number from the receiver
        receiver_num, _ = self._get_receiver(event)

        # the dealer will be based on the part after [from] except where tox is found
        dealer = event.split("[from] ")[1] if "tox" not in event else "tox"

        # the player number is assumed to be the opposite of the receiver
        return (2, dealer) if receiver_num == 1 else (1, dealer)

    def _get_damage_source(self, event: str) -> str:
        # we assume [from] is in all these events
        if not "[from] " in event:
            raise ValueError(f"Invalid event: {event}")
        # get the dealer once we have confirmed [from] is in the event
        _, dealer = self._get_dealer(event)
        if dealer in self.statuses:
            return "Status"
        elif dealer in self.hazards:
            return "Hazard"
        else:
            raise ValueError(f"Invalid event: {event}")
