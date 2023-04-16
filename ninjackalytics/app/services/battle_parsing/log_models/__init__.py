import os
import sys

file_path = os.path.dirname(os.path.realpath(__file__))
app_path = file_path.split("ninjackalytics")[0]
app_path = app_path + "ninjackalytics"
sys.path.insert(1, app_path)

from app.services.battle_parsing.log_models.turn import Turn
from app.services.battle_parsing.log_models.line import Line
from app.services.battle_parsing.log_models.response import Response
