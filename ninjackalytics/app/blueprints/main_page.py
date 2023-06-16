from flask import Blueprint, render_template, flash, g, redirect, request, url_for
from app.database import get_db
from werkzeug.exceptions import abort
from app.blueprints.auth import login_required
from app.database import get_db
from app.services.battle_parsing import Battle, BattlePokemon, BattleParser
from app.services.database_interactors.battle_data_uploader import BattleDataUploader
from app.models.battles import battle_info


bp = Blueprint("main_page", __name__, url_prefix="/")


@bp.route("/", methods=["GET", "POST"])
def index():
    # if a post is made on the main page, run the battle and re-route to a dash app
    if request.method == "POST":
        url = request.form["url"]
        db = get_db()
        error = None

        if not url:
            error = "URL is required."

        if error is None:
            try:
                # analyze the battle
                battle = Battle(url)
                battle_pokemon = BattlePokemon(battle)
                battle_parser = BattleParser(battle, battle_pokemon)
                battle_parser.analyze_battle()
                uploader = BattleDataUploader()
                uploader.upload_battle(battle_parser)

                return redirect(
                    url_for("main_page.battle", battle_id=uploader.battle_id)
                )

            except Exception as e:
                error = f"An error occurred while parsing the battle: {e}"

        # if we got an error, flash it and return to the main page
        flash(error)
        return render_template("main_page/index.html")

    else:
        return render_template("main_page/index.html")


@bp.route("/battle/<string:battle_id>")
def battle(battle_id):
    # first, get the associated database id
    db = get_db()
    db_id = (
        db.query(battle_info.id)
        .filter_by(battle_info.Battle_ID == uploader.battle_id)
        .first()[0]
    )
    render_template("main_page/index.html")

    # TODO: need to then route to a dash application
    # for now, simply render a page that says "battle uploaded successfully"
