from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from flask import session
from ninjackalytics.database.models import (
    SubscriptionTiers,
    DiscountCodes,
    User,
    UserSubscriptions,
)
from ninjackalytics.database import get_sessionlocal
from .navbar import navbar

dash.register_page(__name__, path="/upgrade_account")


def layout():
    # Check if user is logged in
    if "username" in session:
        # User is logged in, fetch subscription tiers and display options
        db_session = get_sessionlocal()
        subscription_tiers = db_session.query(SubscriptionTiers).all()
        db_session.close()

        tier_names2values = {
            tier.tier: f" - ${round(tier.annual_cost/12, 2)}/month (if annual, otherwise ${tier.monthly_cost}/month)"
            for tier in subscription_tiers
        }

        tier_types = ["Annual", "Monthly"]

        return html.Div(
            [
                dcc.Store(id="tier-2-price-store", data=tier_names2values),
                dcc.Store(id="cost-differential-store"),
                navbar(),
                dbc.Container(
                    [
                        # ----- choose subscription information -----
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Label(
                                            "Select a Subscription Tier",
                                            style={"color": "white"},
                                        ),
                                        dcc.Dropdown(
                                            id="subscription-tier-dropdown",
                                            options=list(tier_names2values.keys()),
                                            className="mb-3",
                                        ),
                                    ],
                                    width=4,
                                ),
                                # ------- Price display -------
                                dbc.Col(
                                    html.Div(
                                        id="tier-price",
                                        className="text-white d-flex align-items-center",
                                        style={"height": "38px"},
                                    ),
                                    width=4,
                                    className="d-flex justify-content-start",
                                ),
                            ],
                            className="align-items-center",
                        ),
                        # ----- Annual or Monthly input -----
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Label(
                                            "Select Annual or Monthly",
                                            style={"color": "white"},
                                        ),
                                        dcc.Dropdown(
                                            id="subscription-type-dropdown",
                                            options=tier_types,
                                            className="mb-3",
                                        ),
                                    ],
                                    width=4,
                                ),
                            ]
                        ),
                        # ----- Promo code input -----
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Label(
                                            "Enter Promo Code", style={"color": "white"}
                                        ),
                                        dbc.Input(
                                            id="promo-code-input",
                                            placeholder="Promo Code",
                                            className="mb-3",
                                        ),
                                    ],
                                    width=4,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            "Apply",
                                            id="apply-promo-button",
                                            color="primary",
                                        ),
                                    ],
                                    width=4,
                                ),
                            ],
                            className="align-items-center",
                        ),
                        html.Div(id="promo-code-feedback", className="text-white mt-2"),
                        # ----- Show Total cost -----
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Button(
                                        "Upgrade",
                                        id="upgrade-button",
                                        className="btn btn-success",
                                    ),
                                    width=4,
                                ),
                            ],
                            className="align-items-center",
                        ),
                        html.Div(id="total-cost", className="text-white mt-2"),
                        html.Div(id="upgrade-feedback", className="text-white mt-2"),
                    ],
                    fluid=True,
                    style={
                        "background-image": "url('/assets/Background.jpg')",
                        "background-size": "cover",
                        "background-repeat": "no-repeat",
                        "height": "100vh",
                        "z-index": "0",
                    },
                ),
            ]
        )
    else:
        # User is not logged in, prompt to log in
        return dbc.Container(
            [
                navbar(),
                html.H1(
                    "Please Log In to Upgrade Your Account", className="text-white"
                ),
                dbc.Button(
                    "Log In", href="/account", color="primary", className="mt-2"
                ),
            ],
            style={
                "background-image": "url('/assets/Background.jpg')",
                "background-size": "cover",
                "background-repeat": "no-repeat",
                "height": "100vh",
                "z-index": "0",
            },
            fluid=True,
        )


@callback(
    Output("tier-price", "children"),
    Input("subscription-tier-dropdown", "value"),
    State("tier-2-price-store", "data"),
    prevent_initial_call=True,
)
def update_tier_price(tier_name, tier_names2values):
    if tier_name:
        return f"{tier_names2values[tier_name]}"


@callback(
    Output("total-cost", "children"),
    [
        Input("subscription-tier-dropdown", "value"),
        Input("subscription-type-dropdown", "value"),
        Input("apply-promo-button", "n_clicks"),
        Input("cost-differential-store", "data"),
    ],
    prevent_initial_call=True,
)
def calculate_total_cost(tier_name, subscription_type, n_clicks, cost_differential):

    if tier_name is None or subscription_type is None:
        return "Please select a subscription tier and type."

    if n_clicks is None:
        with get_sessionlocal() as db_session:
            base_cost = get_base_tier_cost(tier_name, subscription_type, db_session)

        if subscription_type == "Annual":
            monthly_cost = round(base_cost / 12, 2)
            total_cost_return = (
                f"Monthly Cost: ${monthly_cost:.2f} | Total Cost: ${base_cost:.2f}"
            )
        else:
            monthly_cost = base_cost
            total_cost_return = f"Monthly Cost: ${monthly_cost:.2f}"

    else:
        if cost_differential:
            monthly_cost = round(cost_differential / 12, 2)
            total_cost_return = f"Monthly Cost: ${monthly_cost:.2f} | Total Cost: ${cost_differential:.2f}"
        else:
            with get_sessionlocal() as db_session:
                base_cost = get_base_tier_cost(tier_name, subscription_type, db_session)

            if subscription_type == "Annual":
                monthly_cost = round(base_cost / 12, 2)
                total_cost_return = (
                    f"Monthly Cost: ${monthly_cost:.2f} | Total Cost: ${base_cost:.2f}"
                )
            else:
                monthly_cost = base_cost
                total_cost_return = f"Monthly Cost: ${monthly_cost:.2f}"

    return total_cost_return


@callback(
    Output("promo-code-feedback", "children"),
    Output("cost-differential-store", "data"),
    [Input("apply-promo-button", "n_clicks")],
    [State("promo-code-input", "value")],
    [Input("subscription-tier-dropdown", "value")],
    [Input("subscription-type-dropdown", "value")],
    prevent_initial_call=True,
)
def apply_promo_code(
    n_clicks, promo_code, selected_tier_name, selected_subscription_type
):
    new_cost = None
    if (
        n_clicks is None
        or promo_code is None
        or selected_tier_name is None
        or selected_subscription_type is None
    ):
        promo_code_feedback = ""

    elif selected_tier_name == "Free":
        promo_code_feedback = "Promo codes are not valid for the Free tier."

    elif selected_subscription_type == "Monthly":
        promo_code_feedback = "Promo codes are only valid for annual subscriptions."

    else:
        # first check if a valid promo code
        with get_sessionlocal() as db_session:
            valid_code = check_if_valid_promo_code(promo_code, db_session)
            if valid_code:
                already_used = check_if_user_has_already_used_promo_code(
                    session.get("username"), promo_code, db_session
                )
                if already_used:
                    promo_code_feedback = "You have already used this promo code."
                else:
                    upgrading = check_if_upgrading_subscription(
                        session.get("username"),
                        selected_tier_name,
                        selected_subscription_type,
                        db_session,
                    )
                    if upgrading:
                        new_cost = apply_promo_code(
                            session.get("username"),
                            promo_code,
                            selected_tier_name,
                            db_session,
                        )
                        promo_code_feedback = (
                            f"Promo code applied! Your total cost is now ${new_cost}."
                        )
                    else:
                        promo_code_feedback = "You are already at or above this tier. Promo code not applied."

            else:
                promo_code_feedback = "Invalid promo code. Please try again."

    return promo_code_feedback, new_cost


# Callback for upgrading (stub)
@callback(
    Output("upgrade-feedback", "children"),
    Input("upgrade-button", "n_clicks"),
    State("subscription-tier-dropdown", "value"),
    State("subscription-type-dropdown", "value"),
    prevent_initial_call=True,
)
def upgrade_subscription(n_clicks, selected_tier, selected_sub_type):
    if n_clicks and selected_tier:
        with get_sessionlocal() as db_session:
            if check_if_upgrading_subscription(
                session.get("username"), selected_tier, selected_sub_type, db_session
            ):
                if process_and_verify_payment():
                    update_user_subscription(
                        session.get("username"),
                        selected_tier,
                        selected_sub_type,
                        db_session,
                    )
                    return "Upgrade successful! Thank you and I hope you enjoy the new features!"
                else:
                    return "Payment failed. Please try again."
            else:
                return "You are already at or above this tier. No upgrade necessary."


# ------------------- helper functions for handling promo codes and subscription checking -------------------
def check_if_valid_promo_code(promo_code, db_session):
    discount_code = db_session.query(DiscountCodes).filter_by(code=promo_code).first()
    if discount_code:
        return True
    else:
        return False


def check_if_upgrading_subscription(
    username, selected_tier, selected_sub_type, db_session
):
    if selected_tier == "Free":
        return False
    user = db_session.query(User).filter_by(username=username).first()
    user_subscription = (
        db_session.query(UserSubscriptions).filter_by(user_id=user.id).first()
    )
    if user_subscription:
        # compare annual cost of selected tier to current subscription
        if user_subscription.active:
            current_tier = user_subscription.subscription_tier_id
            current_tier_annual = (
                db_session.query(SubscriptionTiers)
                .filter_by(id=current_tier)
                .first()
                .annual_cost
            )
            selected_tier_annual = (
                db_session.query(SubscriptionTiers)
                .filter_by(tier=selected_tier)
                .first()
                .annual_cost
            )
            # is the new plan more expensive?
            if selected_tier_annual > current_tier_annual:
                return True
            # is the new plan an annual, but cheaper, subscription, consider this an upgrade as well
            elif (
                selected_tier_annual < current_tier_annual
                and selected_sub_type == "Annual"
                and user_subscription.subscription_type == "Monthly"
            ):
                return True
            # perhaps the new selected_tier_annual is not cheaper than the current but the plan is going from
            # monthly to annual, again, this is an upgrade
            elif (
                user_subscription.subscription_type == "Monthly"
                and selected_sub_type == "Annual"
            ):
                return True
            # finally, if none of the above are true, this is not an upgrade to the account
            else:
                return False
        else:
            return True

    return True


def check_if_user_has_already_used_promo_code(username, promo_code, db_session):
    user = db_session.query(User).filter_by(username=username).first()
    user_subscription = (
        db_session.query(UserSubscriptions).filter_by(user_id=user.id).first()
    )
    if user_subscription:
        if user_subscription.code_used == promo_code:
            return True

    return False


def apply_promo_code(username, promo_code, selected_tier, db_session):
    cost_differntial = calulate_upgrade_cost_differential(
        username, selected_tier, db_session
    )
    promo = db_session.query(DiscountCodes).filter_by(code=promo_code).first()
    discount = promo.discount
    new_cost = round(cost_differntial * (1 - discount), 2)
    return new_cost


def calulate_upgrade_cost_differential(username, selected_tier, db_session):
    user = db_session.query(User).filter_by(username=username).first()
    user_subscription = (
        db_session.query(UserSubscriptions).filter_by(user_id=user.id).first()
    )
    selected_tier_annual = (
        db_session.query(SubscriptionTiers)
        .filter_by(tier=selected_tier)
        .first()
        .annual_cost
    )
    if user_subscription:
        current_tier = user_subscription.subscription_tier_id
        current_tier_annual = (
            db_session.query(SubscriptionTiers)
            .filter_by(id=current_tier)
            .first()
            .annual_cost
        )

        # if current plan is annual, factor in time remaining before renewal date
        if user_subscription.subscription_type == "Annual":
            days_remaining = (
                user_subscription.renewal_date - datetime.utcnow().date()
            ).days
            cost_differential = round(
                (selected_tier_annual - current_tier_annual) * (days_remaining / 365), 2
            )
        # if current plan is monthly, just return the annual cost of the selected tier
        else:
            cost_differential = selected_tier_annual

    # if currently not on a plan then just return the annual cost of the selected tier
    else:
        cost_differential = selected_tier_annual
    return cost_differential


def get_base_tier_cost(tier_name, sub_type, db_session):
    tier = db_session.query(SubscriptionTiers).filter_by(tier=tier_name).first()
    if sub_type == "Annual":
        return tier.annual_cost
    else:
        return tier.monthly_cost


# ------------------- helper functions for managing payment, confirmations, and database updating -------------------
def process_and_verify_payment():
    # Here you would handle the logic for processing a payment
    # This might involve calling a payment gateway API
    # For now, let's just return a placeholder response
    return True


def update_user_subscription(username, selected_tier, selected_tier_type, db_session):
    user = db_session.query(User).filter_by(username=username).first()
    user_subscription = (
        db_session.query(UserSubscriptions).filter_by(user_id=user.id).first()
    )
    selected_tier_id = (
        db_session.query(SubscriptionTiers).filter_by(tier=selected_tier).first().id
    )
    if user_subscription:
        user_subscription.subscription_tier_id = selected_tier_id
        user_subscription.subscription_type = selected_tier_type
        if selected_tier_type == "Annual":
            user_subscription.renewal_date = datetime.utcnow().date() + relativedelta(
                years=1
            )
        else:
            user_subscription.renewal_date = datetime.utcnow().date() + relativedelta(
                months=1
            )
        user_subscription.active = True
    else:
        new_subscription = UserSubscriptions(
            user_id=user.id,
            subscription_tier_id=selected_tier_id,
            subscription_type=selected_tier_type,
            subscription_start_date=datetime.utcnow().date(),
            renewal_date=(
                datetime.utcnow().date() + relativedelta(years=1)
                if selected_tier_type == "Annual"
                else datetime.utcnow().date() + relativedelta(months=1)
            ),
            active=True,
        )
        db_session.add(new_subscription)
    db_session.commit()
    return True
