import functools

from flask import Blueprint, render_template, request, session, url_for
from battle_display import BattleData

bp = Blueprint("/", __name__)


@bp.route("/submit", methods=("POST"))
def submit_battle():
    if request.method == "POST":

        battle_url = request.form["url"]
        battle_id = battle_url.split("pokemonshowdown.com/")[1]

        RequestedData = BattleData(battle_id=battle_id)
