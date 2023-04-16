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


class PassiveDataFinder(DamageDataFinder):
    def __init__(self, battle_pokemon: BattlePokemon):
        super().__init__(battle_pokemon)

    def get_damage_data(
        self, event: str, turn: Turn, battle: Battle = None
    ) -> Dict[str, str]:
        """
        Get the damage data from a passive event.

        Parameters:
        -----------
        event: str
            The passive event
        turn: Turn
            The turn the event occurred on.

        Returns:
        --------
        Dict[str, str]:
            The damage data from the passive event.

        Example Event:
        --------------
        |-damage|p1a: Druddigon|88/100|[from] Leech Seed|[of] p2a: Ferrothorn
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
        # the source name will be the part after [from]
        return event.split("[from] ")[1].split("|")[0]

    def _get_dealer(self, event: str) -> Tuple[int, str]:
        """
        Example Event:
        --------------
        |-damage|p1a: Druddigon|88/100|[from] Leech Seed|[of] p2a: Ferrothorn
        """
        # dealer will look for an [of] in the event, otherwise, will be based on [from ] and receiver
        if "[of] " in event:
            dealer_raw_name = event.split("[of] ")[1]
            pnum, dealer_name = self.battle_pokemon.get_pnum_and_name(dealer_raw_name)
            return pnum, dealer_name
        else:
            # NOTE: I am unnable to think of a real example of this - here for rigor
            # get the player number from the receiver
            receiver_num, _ = self._get_receiver(event)

            # the dealer will be based on the part after [from]
            dealer = event.split("[from] ")[1]

            # the player number is assumed to be the opposite of the receiver
            return (2, dealer) if receiver_num == 1 else (1, dealer)

    def _get_damage_source(self, event: str) -> str:
        # this is a catch all type source - it is the last to be assigned and assumes [from] is in the event
        if not "[from] " in event:
            raise ValueError(f"Invalid event: {event}")
        else:
            return "Passive"
