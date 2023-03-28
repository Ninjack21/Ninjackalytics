import re
from typing import Dict, List, Protocol, Tuple


class Turn(Protocol):
    number: int
    text: str


class Battle(Protocol):
    def get_turns(self) -> List[Turn]:
        ...


class BattlePokemon(Protocol):
    def get_pnum_and_name(self) -> Tuple[int, str]:
        ...


class PivotData:
    def __init__(self, battle, battle_pokemon):
        self.battle = battle
        self.battle_pokemon = battle_pokemon

    def get_pivot_data(self) -> List[Dict[str, str]]:
        """
        Returns a list of dictionaries containing information about pivot events.

        Returns
        -------
        - pivot_data: List[Dict[str, str]]
            - Each dictionary contains the following keys:
                - "Pokemon_Enter": Name of the Pokemon entering the battle
                - "Player_Number": The player number controlling the Pokemon
                - "Source_Name": The source of the pivot action or the move causing the pivot
                - "Turn": Turn number when the pivot occurred

        Example Events
        --------------
        - |switch|p1a: Dragapult|Dragapult, M|28/100|[from] Teleport
        - |switch|p2a: Moustachio|Alakazam, M, shiny|252/252
        ---
        """
        turns = self.battle.get_turns()
        pivot_data = []

        for turn in turns:
            # Extract switch events from turn text
            switch_events = re.findall(r"\|switch\|[^|]+.*", turn.text)

            for event in switch_events:
                # Parse player number and Pokemon name from switch event
                (
                    player_number,
                    pokemon_name,
                ) = self.battle_pokemon.get_pnum_and_name(event.split("|")[2])

                # Determine the source of the pivot action
                source_name = self._get_source_name(event)

                pivot_data.append(
                    {
                        "Pokemon_Enter": pokemon_name,
                        "Player_Number": player_number,
                        "Source_Name": source_name,
                        "Turn": turn.number,
                    }
                )

        return pivot_data

    def _get_source_name(self, event: str) -> str:
        """
        Returns the source of the pivot action based on the given event string.
        If the event string contains a section with [from], the source name will
        be the text following [from]. Otherwise, the source name will be "action".
        """
        from_match = re.search(r"\[from\] ([^\]]+)", event)

        if from_match:
            return from_match.group(1)
        else:
            return "action"
