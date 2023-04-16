from typing import Dict, Tuple, List
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
from app.services.battle_parsing.damage_models import ReceiverFinder, DealerSourceFinder


# =================== DEFINE MODEL ===================


class MoveDataFinder(DamageDataFinder):
    def __init__(self, battle_pokemon: BattlePokemon):
        super().__init__(battle_pokemon)

        self.dealer_finder = DealerSourceFinder(battle_pokemon)
        self.receiver_finder = ReciverFinder(battle_pokemon)

    def get_damage_data(self, event: str, turn: Turn, battle: Battle) -> Dict[str, str]:
        """
        Get the damage data from a move event.
        NOTE: Move events do require the battle object as moves like future sight need to be
        back-searched for the dealer.

        Parameters:
        -----------
        event: str
            The move event
        turn: Turn
            The turn the event occurred on.

        Returns:
        --------
        Dict[str, str]:
            The damage data from the move event.
        ---
        """
        damage_dict = {}

        damage_dict["Type"] = self._get_damage_source(event)
        source_name = self._get_source_name(event)

        dealer_pnum, dealer = self.dealer_finder.get_dealer(event)
        damage_dict["Dealer"] = dealer
        damage_dict["Dealer_Player_Number"] = dealer_pnum

        receiver_pnum, receiver = self.receiver_finder.get_receiver(event)
        damage_dict["Receiver"] = receiver
        damage_dict["Receiver_Player_Number"] = receiver_pnum

        damage_dict["Source_Name"] = source_name

        hp_change = self._get_hp_change(event, receiver)
        damage_dict["Damage"] = abs(hp_change)

        damage_dict["Turn"] = turn.number

        return damage_dict

    def _get_damage_source(self, event: str) -> str:
        """
        Get the damage source from the event.

        Parameters:
        -----------
        event: str
            The damage event.

        Returns:
        --------
        str:
            The damage source.
        ---
        """
        # damage that comes from moves does not have [from] in the event
        if "[from]" in event:
            raise ValueError(f"Event {event} is not a move event.")
        else:
            return "move"

    def _get_source_name(self, event: str) -> str:
        pass
