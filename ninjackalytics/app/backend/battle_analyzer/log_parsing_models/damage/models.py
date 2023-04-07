import re
from typing import Dict, List, Tuple, Protocol, Optional
from abc import ABC, abstractmethod

# TODO: update methods that return non-pokemon dealers by adding a method to search upwards
# in a battle log for the pokemon who used the move that has resulted in the damage event


class Turn(Protocol):
    number: int
    text: str


class Battle(Protocol):
    def get_turns(self) -> List[Turn]:
        ...


class BattlePokemon(Protocol):
    def get_pnum_and_name(self) -> Tuple[int, str]:
        ...

    def update_hp_for_pokemon(self, raw_name: str, new_hp: float) -> None:
        ...

    def get_pokemon_hp_change(self, raw_name: str) -> float:
        ...

    def get_pokemon_current_hp(self, raw_name: str) -> float:
        ...


class DamageData:
    def __init__(self, battle: Battle, battle_pokemon: BattlePokemon):
        self.move_data_finder = MoveDataFinder(battle, battle_pokemon)
        self.passive_data_finder = PassiveDataFinder(battle, battle_pokemon)
        self.item_ability_data_finder = ItemAbilityDataFinder(battle, battle_pokemon)
        self.status_hazard_data_finder = StatusHazardDataFinder(battle, battle_pokemon)

    def _get_damage_source(self, event: str) -> str:
        """
        Get the source of the damage event.

        Parameters:
        -----------
        event: str
            The damage event.

        Returns:
        --------
        str:
            The source of the damage event.
        ---
        """
        for source, pattern in self.source_patterns.items():
            if re.search(pattern, event):
                return source

        return "move" if not "[from]" in event else "passive"

    def _get_mon_pnum_and_name(self, raw_name: str) -> Tuple[int, str]:
        """
        Get the player number and name of the Pokemon.

        Parameters:
        -----------
        raw_name: str
            The raw name of the Pokemon.

        Returns:
        --------
        Tuple[int, str]:
            The player number and name of the Pokemon.
        ---
        """
        return self.battle_pokemon.get_pnum_and_name(raw_name)

    def _get_receiver_raw_name(self, event: str) -> str:
        """
        Get the raw name of the Pokemon receiving the damage.

        e.x.
        ============================
        |move|p1a: May Day Parade|Sucker Punch|p2a: AMagicalFox
              ^^^^^^^^^^^^^^^^^^^ (dealer)
        ...
        |-damage|p2a: AMagicalFox|0 fnt <-- expected event
                 ^^^^^^^^^^^^^^^^ (receiver)
        ============================
        Parameters:
        -----------
        event: str
            The damage event.

        Returns:
        --------
        str:
            The raw name of the Pokemon receiving the damage.
        ---
        NOTE: This logic is currently the same as _get_dealer_raw_name but separated for rigor
        """
        return event.split("|")[2]

    def _get_dealer_raw_name(self, event: str) -> str:
        """
        Get the raw name of the Pokemon dealing the damage.

        e.x.
        ============================
        |move|p1a: May Day Parade|Sucker Punch|p2a: AMagicalFox <-- expected event
              ^^^^^^^^^^^^^^^^^^^ (dealer)
        ...
        |-damage|p2a: AMagicalFox|0 fnt
                 ^^^^^^^^^^^^^^^^ (receiver)
        ============================

        Parameters:
        -----------
        event: str
            The damage event.

        Returns:
        --------
        str:
            The raw name of the Pokemon dealing the damage.
        ---
        """
        return event.split("|")[2]


class DamageDataFinder(ABC):
    def __init__(self, battle_pokemon: BattlePokemon):
        self.battle_pokemon = battle_pokemon

    @abstractmethod
    def get_damage_data(self, event: str, turn: Turn) -> Dict[str, str]:
        ...

    @abstractmethod
    def _get_source_name(self, event: str) -> str:
        ...

    def _get_receiver(self, event: str) -> Tuple[int, str]:
        receiver_raw_name = event.split("|")[2]
        return self.battle_pokemon.get_pnum_and_name(receiver_raw_name)

    def _get_hp_change(self, event: str, receiver: str) -> float:
        """
        Example events:
        ---------------
        |-damage|p2a: Zapdos|57/100.
        |-damage|p2a: BrainCell|372/424|[from] item: Life Orb
        ---
        """
        old_hp = self.battle_pokemon.get_pokemon_current_hp(receiver)
        # determine new hp in terms of %
        new_raw_hp = event.split("|")[3].split("/")
        # have to split on space for some statuses : |-damage|p1a: Rillaboom|94/100 tox|[from] psn
        new_hp = float(new_raw_hp[0]) / float(new_raw_hp[1].split(" ")[0]) * 100

        self.battle_pokemon.update_hp_for_pokemon(receiver, new_hp)
        return self.battle_pokemon.get_pokemon_hp_change(receiver)


class DealerSourceFinder:
    def __init__(self, battle_pokemon: BattlePokemon):
        self.battle_pokemon = battle_pokemon
        self.move_patterns = {
            "normal": re.compile(
                r"\|move\|(?P<dealer>.*)\|(?P<source>.*)\|(?P<receiver>.*)"
            ),
            "delayed": re.compile(
                r"\|move\|(?P<dealer>.*)\|(?P<source>.*)\|(?P<receiver>.*)\n\|-start"
            ),
            "spread": re.compile(
                r"\|move\|(?P<dealer>[p][1-2][a-d]: .*)\|(?P<source>.*)\|(?P<primary_receiver>.*)\|\[spread\]"
            ),
            "anim": re.compile(
                r"\|-anim\|(\|move\||)(?P<dealer>.*)\|(?P<source>.*)\|(?P<receiver>.*)"
            ),
        }
        self.move_type_methods = {
            "normal": self._get_normal_dealer_and_source,
            "delayed": self._get_delayed_dealer_and_source,
            "spread": self._get_spread_dealer_and_source,
            "anim": self._get_animated_dealer_and_source,
        }

    def get_dealer_and_source(
        self, event: str, turn: Turn, battle: Battle
    ) -> Tuple[Tuple[int, str], str]:
        # look for the most recent move type indicator in the turn lines right before the event
        previous_turn_lines = reversed(list(turn.text.split(event)[0].splitlines()))
        move_type = next(
            (self._get_move_type(line) for line in previous_turn_lines), None
        )

        if move_type not in self.move_type_methods:
            raise ValueError(f"Unable to determine move type for event: {event}")

        return self.move_type_methods[move_type](event, turn, battle)

    def _get_move_type(self, line: str) -> str:
        if line.startswith("|move|") and "[spread]" in line:
            return "spread"
        elif line.startswith("|move|"):
            return "normal"
        elif line.startswith("|-anim|"):
            return "anim"
        elif line.startswith("|-end|"):
            return "delayed"

    def _get_normal_dealer_and_source(
        self, event: str, turn: Turn, battle: Battle = None
    ) -> Tuple[Tuple[int, str], str]:
        """
        Example Event:
        --------------
        |-damage|p1a: Cuss-Tran|67/100

        Example Turn:
        --------------
        |move|p2a: Blissey|Seismic Toss|p1a: Cuss-Tran
        |-damage|p1a: Cuss-Tran|67/100
        """
        pre_event_text = turn.text.split(event)[0]
        matches = reversed(
            list(re.finditer(self.move_patterns["normal"], pre_event_text))
        )
        receiver_raw = self._get_receiver_raw_from_event(event)
        match = self._get_match(matches, receiver_raw)
        if match:
            dealer = self.battle_pokemon.get_pnum_and_name(match.group("dealer"))
            source = match.group("source")
            return dealer, source
        raise ValueError(f"Could not find dealer for event: {event}")

    def _get_delayed_dealer_and_source(
        self, event: str, turn: Turn, battle: Battle
    ) -> Tuple[Tuple[int, str], str]:
        """
        delayed:
        --------
        |turn|14
        ...
        |move|p2a: Slowking|Future Sight|p1a: Ninetales <-- DEALER AND SOURCE
        |-start|p2a: Slowking|move: Future Sight
        ...
        |turn|15
        ...
        |turn|16
        ...
        |-end|p1a: Ninetales|move: Future Sight
        |-damage|p1a: Ninetales|44/100 <-- EXAMPLE EVENT
        ...
        |turn|17

        Notes:
        ------
        - The delayed move is the move that is delayed by a move such as Future Sight
        - The original target of the move may not be the receiver of the damage.
        """
        # find source name (indicated by -end)
        end_pattern = re.compile(r"-end\|(?P<receiver>.*)\|move: (?P<source>.*)\n")
        end_event = next(
            (
                e
                for e in re.finditer(end_pattern, turn.text)
                if e.group("receiver") == self._get_receiver_raw_from_event(event)
            ),
            None,
        )
        if not end_event:
            raise ValueError(f"Could not find |-end| indicator for event: {event}")
        source_name = end_event.group("source")

        # find dealer name (indicated by -start) where source name is the same
        start_events = [
            event
            for turn in reversed(battle.get_turns())
            for event in re.finditer(self.move_patterns["delayed"], turn.text)
            if event.group("source") == source_name
        ]
        start_event = next(iter(start_events), None)
        if not start_event:
            raise ValueError(f"Could not find |-start| indicator for event: {event}")
        dealer = self.battle_pokemon.get_pnum_and_name(start_event.group("dealer"))

        return dealer, source_name

    def _get_animated_dealer_and_source(
        self, event: str, turn: Turn, battle: Battle = None
    ) -> Tuple[Tuple[int, str], str]:
        """
        Example Event:
        --------------
        |-damage|p2b: Incineroar|31/100

        Example Turn:
        --------------
        |-anim||move|p1b: Dragapult|Dragon Darts|p2a: Pelipper
        |-damage|p2a: Pelipper|65/100
        |-anim|p1b: Dragapult|Dragon Darts|p2b: Incineroar
        |-damage|p2b: Incineroar|31/100
        """
        pre_event_text = turn.text.split(event)[0]
        matches = reversed(
            list(re.finditer(self.move_patterns["anim"], pre_event_text))
        )
        receiver_raw = self._get_receiver_raw_from_event(event)
        match = self._get_match(matches, receiver_raw)
        if match:
            dealer = self.battle_pokemon.get_pnum_and_name(match.group("dealer"))
            source = match.group("source")
            return dealer, source
        raise ValueError(f"Could not find dealer for event: {event}")

    def _get_spread_dealer_and_source(
        self, event: str, turn: Turn, battle: Battle = None
    ) -> Tuple[Tuple[int, str], str]:
        """
        Example Event:
        --------------
        |-damage|p1a: Indeedee|15/100

        Example Turn:
        --------------
        |move|p2a: Regidrago|Dragon Energy|p1b: Regieleki|[spread] p1a,p1b
        |-damage|p1a: Indeedee|15/100
        |-damage|p1b: Regieleki|0 fnt

        NOTE:
        -----
        The spread move hits all enemies and thus we can't rely on the receiver of this damage event, thus
        *we assume that by this point the move must be a spread move and that move must be the source of
        the current damage event*
        """
        pre_event_text = turn.text.split(event)[0]
        matches = reversed(
            list(re.finditer(self.move_patterns["spread"], pre_event_text))
        )
        # spread moves hit all enemies and thus we can't rely on the receiver of this damage event
        match = next((m for m in matches), None)

        if match:
            dealer = self.battle_pokemon.get_pnum_and_name(match.group("dealer"))
            source = match.group("source")
            return dealer, source
        raise ValueError(f"Could not find dealer for event: {event}")

    def _get_match(self, matches, receiver_raw_name):
        return next(
            (m for m in matches if m.group("receiver") == receiver_raw_name),
            None,
        )

    def _get_receiver_raw_from_event(self, event: str) -> str:
        return event.split("|")[2]

    # TODO: build out ReceiverFinder and create unit tests
    # TODO: finally, implement ReceiverFinder to see if passes tests


class ReceiverFinder:
    def __init__(self, battle_pokemon: BattlePokemon):
        self.battle_pokemon = battle_pokemon

    def get_receiver(self, event: str) -> Tuple[int, str]:
        receiver_raw_name = event.split("|")[2]
        return self.battle_pokemon.get_pnum_and_name(receiver_raw_name)


class MoveDataFinder(DamageDataFinder):
    def __init__(self, battle_pokemon: BattlePokemon):
        super().__init__(battle_pokemon)

        self.dealer_finder = MoveDealerFinder(battle_pokemon)
        self.receiver_finder = MoveReceiverFinder(battle_pokemon)

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


class ItemOrAbilityDataFinder(DamageDataFinder):
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

        hp_change = self._get_hp_change(event, receiver)
        damage_dict["Damage"] = abs(hp_change)

        damage_dict["Type"] = self._get_damage_source(event)
        damage_dict["Turn"] = turn.number

        return damage_dict

    def _get_source_name(self, event: str) -> str:
        # should see at least 5 elements when split by "|" for an item or ability event
        if len(event.split("|")) != 5:
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


class StatusOrHazardDataFinder(DamageDataFinder):
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
