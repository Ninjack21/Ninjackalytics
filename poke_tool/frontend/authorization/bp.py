from flask import (
    Blueprint, redirect, render_template, url_for, request, flash
)

bp = Blueprint('auth', __name__)