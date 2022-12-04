# %%
import sys

sys.path.insert(0, r"C:\Remote VS Code Folder\Ninjackalytics")
sys.path.insert(
    0, r"C:\Remote VS Code Folder\Ninjackalytics\poke_tool\Auto_Pull_Replays"
)
sys.path.insert(
    0, r"C:\Remote VS Code Folder\Ninjackalytics\poke_tool\poke_stats_gen_backend"
)
sys.path.insert(
    0,
    r"C:\Remote VS Code Folder\Ninjackalytics\poke_tool\poke_stats_gen_backend\Errors",
)
sys.path.insert(
    0,
    r"C:\Remote VS Code Folder\Ninjackalytics\poke_tool\poke_user_interface",
)

from Auto_Puller import auto_runner
import pandas

# %%
auto_runner()
# %%
import sys

sys.path.insert(0, r"C:\Remote VS Code Folder\Ninjackalytics")
sys.path.insert(
    0, r"C:\Remote VS Code Folder\Ninjackalytics\poke_tool\Auto_Pull_Replays"
)
sys.path.insert(
    0, r"C:\Remote VS Code Folder\Ninjackalytics\poke_tool\poke_stats_gen_backend"
)
sys.path.insert(
    0,
    r"C:\Remote VS Code Folder\Ninjackalytics\poke_tool\poke_stats_gen_backend\Errors",
)
sys.path.insert(
    0,
    r"C:\Remote VS Code Folder\Ninjackalytics\poke_tool\poke_user_interface",
)
from Get_Battle_Data import BattleData

bid = r"gen6ou-1711595554"
Battle = BattleData(bid)
display(Battle.get_aggregate_data())
#%%
