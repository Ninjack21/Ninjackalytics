from ninjackalytics.database.models import (
    User,
    Roles,
    Pages,
    SubscriptionTiers,
    RolePages,
    SubscriptionPages,
    UserSubscriptions,
)
from ninjackalytics.database.database import get_sessionlocal
from dash import html, dcc
import dash_bootstrap_components as dbc


def get_role_name(role_id):
    with get_sessionlocal() as db_session:
        role = db_session.query(Roles).filter_by(id=role_id).first()
        return role.role if role else None


def get_subscription_tier_name(subscription_tier_id):
    with get_sessionlocal() as db_session:
        subscription_tier = (
            db_session.query(SubscriptionTiers)
            .filter_by(id=subscription_tier_id)
            .first()
        )
        return subscription_tier.tier_name if subscription_tier else None


def user_has_access(path_name, username=None):
    path_name = path_name.replace("/", "")
    # Start database session
    db_session = get_sessionlocal()

    if not username:
        # if not logged in, role is "User" and subscription tier is "Free"
        role_id = db_session.query(Roles).filter_by(role="User").first().id
        subscription_tier_id = (
            db_session.query(SubscriptionTiers).filter_by(product="Free").first().id
        )
    else:
        # get the user's role and subscription tier
        user = db_session.query(User).filter_by(username=username).first()
        role_id = user.role
        user_subscription = (
            db_session.query(UserSubscriptions).filter_by(user_id=user.id).first()
        )
        # if the user_id is not found in the UserSubscriptions table, then they are a free user
        if not user_subscription:
            subscription_tier_id = (
                db_session.query(SubscriptionTiers).filter_by(product="Free").first().id
            )
        else:
            # verify that the UserSubscription is active
            if not user_subscription.active:
                # free tier if the user's subscription is not active
                subscription_tier_id = (
                    db_session.query(SubscriptionTiers)
                    .filter_by(product="Free")
                    .first()
                    .id
                )
            else:
                subscription_tier_id = user_subscription.subscription_tier_id

    role_name = get_role_name(role_id)
    if role_name != "User":
        pages_access = get_role_id_access(role_id)

    else:
        pages_access = get_subsription_tier_id_access(subscription_tier_id)

    # append the root page since all users have access to this
    pages_access.append("")

    db_session.close()
    if path_name in pages_access:
        return True
    else:
        return False


def get_role_id_access(role_id):
    # Start database session
    db_session = get_sessionlocal()

    pages = db_session.query(RolePages).filter_by(role_id=role_id).all()
    page_ids = [page.page_id for page in pages]
    page_names = db_session.query(Pages.page_name).filter(Pages.id.in_(page_ids)).all()
    page_names = [name[0] for name in page_names]

    db_session.close()

    return page_names


def get_subsription_tier_id_access(subscription_tier_id):
    # Start database session
    db_session = get_sessionlocal()

    pages = (
        db_session.query(SubscriptionPages)
        .filter_by(sub_tier_id=subscription_tier_id)
        .all()
    )
    page_ids = [page.page_id for page in pages]
    page_names = db_session.query(Pages.page_name).filter(Pages.id.in_(page_ids)).all()
    page_names = [name[0] for name in page_names]

    db_session.close()

    return page_names


def determine_access_error_type(role_id, path_name):
    if "admin" in path_name:
        return "role"
    elif role_id:
        role_name = get_role_name(role_id)
        if role_name != "User":
            return "role"
        else:
            return "subscription_tier"
    else:
        return "generic"


def get_security_return(session, pathname: str, username):
    # Check if user has access to the current page
    if not user_has_access(pathname, username):
        return False
    else:
        return True


def validate_access_get_alternate_div_if_invalid(session, pathname: str, username):
    role_id = session.get("role_id")
    # Check if user has access to the current page
    if not user_has_access(pathname, username):
        error_type = determine_access_error_type(role_id, pathname)
        return False, get_error_layout(error_type)
    else:
        return True, None


def get_error_layout(error_type: str):
    base_style = {
        "color": "white",
        "textAlign": "center",
        "marginTop": "20vh",
    }

    if error_type == "role":
        return html.Div(
            [
                html.H3(
                    "Access Denied",
                    style={"color": "#FF6347"},  # Tomato color for emphasis
                ),
                html.P(
                    "You do not have access to this page. Please contact your administrator.",
                    style=base_style,
                ),
            ],
            style={
                "background-image": "url('/assets/Background.jpg')",
                "background-size": "cover",
                "background-repeat": "no-repeat",
                "height": "100vh",
                "z-index": "0",
            },
        )
    elif error_type == "subscription_tier":
        return html.Div(
            [
                html.H3(
                    "Subscription Upgrade Required",
                    style={"color": "#FF6347"},  # Tomato color for emphasis
                ),
                html.P(
                    "You do not have access to this page. Please upgrade your subscription.",
                    style=base_style,
                ),
                dcc.Link(
                    "Upgrade Subscription",
                    href="/upgrade_account",
                ),
            ],
            style={
                "background-image": "url('/assets/Background.jpg')",
                "background-size": "cover",
                "background-repeat": "no-repeat",
                "height": "100vh",
                "z-index": "0",
            },
        )
    else:
        return html.Div(
            [
                html.H3(
                    "Access Denied",
                    style={"color": "#FF6347"},  # Tomato color for emphasis
                ),
                html.P("You do not have access to this page.", style=base_style),
            ],
            style={
                "background-image": "url('/assets/Background.jpg')",
                "background-size": "cover",
                "background-repeat": "no-repeat",
                "height": "100vh",
                "z-index": "0",
            },
        )
