from flask import session
import dash_bootstrap_components as dbc
from ninjackalytics.database import get_sessionlocal
from ninjackalytics.database.models import Roles
from .page_utilities.session_functions import get_role_name


def navbar():
    # Check if 'role_id' is in session and get the role name
    role_name = get_role_name(session.get("role_id")) if "role_id" in session else None

    # Base links available to all users
    base_children = [
        dbc.NavItem(dbc.NavLink("Team Builder", href="/team_analysis")),
        dbc.NavItem(dbc.NavLink("Meta Analysis", href="/meta_analysis")),
        dbc.NavItem(dbc.NavLink("Pre Battle Analysis", href="/pre_battle_analysis")),
        dbc.NavItem(dbc.NavLink("Player Scout", href="/player_scout")),
    ]

    # Links available only to admins
    admin_children = [
        dbc.NavItem(dbc.NavLink("Admin", href="/admin_home")),
    ]

    # Links for non-authenticated users
    guest_children = [
        dbc.NavItem(dbc.NavLink("Register", href="/register")),
        dbc.NavItem(dbc.NavLink("Login", href="/login")),
    ]

    # Construct the final list of children based on the user's role
    if role_name == "Admin":
        children = base_children + guest_children + admin_children
    elif "user_id" in session:  # Authenticated user but not admin
        children = base_children + guest_children
    else:  # Guest user
        children = base_children + guest_children

    navbar = dbc.NavbarSimple(
        children=children,
        brand="Ninjackalytics",
        brand_href="/",
        color="dark",
        dark=True,
        fluid=True,
        className="navbar",
    )

    return navbar
