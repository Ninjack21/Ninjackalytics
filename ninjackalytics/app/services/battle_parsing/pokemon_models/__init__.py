import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.pokemon_models.pokemon import Pokemon
from app.services.battle_parsing.pokemon_models.team import Team
from app.services.battle_parsing.pokemon_models.pokemon_finder import PokemonFinder
