from typing import Dict, Tuple, List


from ninjackalytics.services.battle_parsing.hp_event_handling.damage_models.sub_modules.d_type_specific_models import (
    DamageDataFinder,
)
from ninjackalytics.services.battle_parsing.hp_event_handling.damage_models.sub_modules import (
    ReceiverFinder,
    DealerSourceFinder,
)

# =================== IMPORT PROTOCOLS ===================
from ninjackalytics.protocols.battle_parsing.battle_initialization.protocols import (
    Battle,
    BattlePokemon,
    Turn,
)


# =================== DEFINE MODEL ===================


class MoveDataFinder(DamageDataFinder):
    def __init__(self, battle_pokemon: BattlePokemon):
        super().__init__(battle_pokemon)

        self.dealer_finder = DealerSourceFinder(battle_pokemon)
        self.receiver_finder = ReceiverFinder(battle_pokemon)

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
            The damage data from the move event with the following keys:
            - Type: The type of damage event. In this case, "move".
            - Dealer: The name of the pokemon that dealt the damage.
            - Dealer_Player_Number: The player number of the pokemon that dealt the damage.
            - Source_Name: The name of the move that dealt the damage.
            - Receiver: The name of the pokemon that received the damage.
            - Receiver_Player_Number: The player number of the pokemon that received the damage.
            - Damage: The amount of damage dealt.
            - Turn: The turn the damage was dealt.
        ---
        """
        damage_dict = {}

        damage_dict["Type"] = self._get_damage_type(event)

        (dealer_num, dealer_name), source = self.dealer_finder.get_dealer_and_source(
            event, turn, battle
        )
        damage_dict["Dealer"] = dealer_name
        damage_dict["Dealer_Player_Number"] = dealer_num
        damage_dict["Source_Name"] = source

        receiver_pnum, receiver = self.receiver_finder.get_receiver(event)
        damage_dict["Receiver"] = receiver
        damage_dict["Receiver_Player_Number"] = receiver_pnum

        # _get_hp_change expects a raw name, not the already parsed name
        receiver_raw = event.split("|")[2]
        hp_change = self._get_hp_change(event, receiver_raw)
        damage_dict["Damage"] = abs(hp_change)

        damage_dict["Turn"] = turn.number

        return damage_dict

    def _get_source_name(self, event: str) -> str:
        """
        pass since DealerSourceFinder already handles this.
        ---
        """
        print(
            "not needed for MoveDataFinder due to DealerSourceFinder already handling"
        )

    def _get_damage_type(self, event: str) -> str:
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
            return "Move"
