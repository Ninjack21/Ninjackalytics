from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
from .battle_display import BattleData

app = Dash("Battle_Stats_Viewer")
