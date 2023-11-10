from typing import Dict, Tuple, List, Protocol
import re

# =================== IMPORT PROTOCOLS ===================
from ninjackalytics.protocols.battle_parsing.battle_initialization.protocols import (
    Battle,
    BattlePokemon,
    Turn,
)


# =================== DEFINE MODEL ===================


class DealerSourceFinder:
    def __init__(self, battle_pokemon: BattlePokemon):
        self.battle_pokemon = battle_pokemon
        self.move_patterns = {
            "normal": re.compile(
                r"\|move\|(?P<dealer>[^|]*)\|(?P<source>[^|]*)\|(?P<receiver>[^\|\n]*)"
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
            "curse": re.compile(
                r"\|move\|(?P<self_dealer>.*)\|(?P<source>.*)\|(?P<receiver>.*)\n\|-start"
            ),
        }
        self.move_type_methods = {
            "normal": self._get_normal_dealer_and_source,
            "delayed": self._get_delayed_dealer_and_source,
            "spread": self._get_spread_dealer_and_source,
            "anim": self._get_animated_dealer_and_source,
            "curse": self._get_ghost_curse_dealer_and_source,
        }

    def get_dealer_and_source(
        self, event: str, turn: Turn, battle: Battle
    ) -> Tuple[Tuple[int, str], str]:
        # look for the most recent move type indicator in the turn lines right before the event
        previous_turn_lines = reversed(list(turn.text.split(event)[0].splitlines()))
        move_type = next(
            (
                move_type
                for line in previous_turn_lines
                if (move_type := self._get_move_type(line)) is not None
            ),
            None,
        )

        if move_type not in self.move_type_methods:
            raise ValueError(f"Unable to determine move type for event: {event}")

        return self.move_type_methods[move_type](event, turn, battle)

    def _get_move_type(self, line: str) -> str:
        if line.startswith("|move|") and "[spread]" in line:
            return "spread"
        # using a custom solution for a single move until find more examples to generalize from
        elif line.startswith("|move|") and line.split("|")[3] == "Curse":
            return "curse"
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
        pre_event_text = self._get_pre_event_text(event=event, turn=turn)
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
        pre_event_text = self._get_pre_event_text(event=event, turn=turn)
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
        pre_event_text = self._get_pre_event_text(event=event, turn=turn)
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

    def _get_ghost_curse_dealer_and_source(
        self, event: str, turn: Turn, battle: Battle = None
    ) -> Tuple[Tuple[int, str], str]:
        """
        Example Event:
        --------------
        |-damage|p1a: Dragapult|0 fnt

        Example Turn:
        --------------
        |turn|7
        |
        |t:|1699522673
        |move|p1a: Dragapult|Curse|p2a: Ursaluna
        |-start|p2a: Ursaluna|Curse|[of] p1a: Dragapult
        |-damage|p1a: Dragapult|0 fnt
        """
        pre_event_text = self._get_pre_event_text(event=event, turn=turn)
        matches = reversed(
            list(re.finditer(self.move_patterns["curse"], pre_event_text))
        )
        receiver_raw = self._get_receiver_raw_from_event(event)
        # ghost curse is tricky as the receiver may be the dealer depending on how the damage is line is formed
        match = next(
            (
                m
                for m in matches
                if m.group("self_dealer")
                == receiver_raw  # if event was inflicted by self
                or m.group("receiver")
                == receiver_raw  # if event was inflicted by another
            ),
            None,
        )

        if match:
            dealer = self.battle_pokemon.get_pnum_and_name(match.group("self_dealer"))
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

    def _get_pre_event_text(self, event: str, turn: Turn) -> str:
        """
        because it is possible for the same turn to see the same event string multiple times we need to find a way
        to try to ensure the pre_event_text shows the correct set of information. The example that revealed this
        is below:

        |turn|9
        |...
        |-damage|p2a: Mimikyu|91/100|[from] item: Life Orb
        ...
        |move|p1a: Incineroar|Knock Off|p2a: Mimikyu
        |-activate|p2a: Mimikyu|ability: Disguise
        |-damage|p2a: Mimikyu|91/100
        ...

        Parameters
        ----------
        event : str
            the event string we want to try to exactly match within pre_event_text
        turn : Turn
            the turn string we are going to look through for the exact event

        Returns
        -------
        pre_event_text : str
            the text that came before the event string was found in the turn text
        """

        pre_event_text = ""
        for line in turn.text.splitlines():
            if line == event:
                break
            pre_event_text += line + "\n"
        return pre_event_text
