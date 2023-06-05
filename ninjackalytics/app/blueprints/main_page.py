from flask import Blueprint, render_template, flash, g, redirect, request, url_for
from app.database import get_db
from werkzeug.exceptions import abort
from app.blueprints.auth import login_required
from app.database import get_db

bp = Blueprint("main_page", __name__, url_prefix="/")


@bp.route("/")
def index():
    return render_template("main_page/index.html")
