from ninjackalytics.services.database_interactors.table_accessor import TableAccessor
import pandas as pd
from typing import List


def get_viable_pokemon(
    format_pokemon: str, selected_ignore_mons: List[str], already_used_mons: List[str]
):
    unavailable_mons = [None]
    if already_used_mons:
        unavailable_mons += already_used_mons
    if selected_ignore_mons:
        unavailable_mons += selected_ignore_mons

    viable_mons = [mon for mon in format_pokemon if mon not in unavailable_mons]
    return viable_mons
