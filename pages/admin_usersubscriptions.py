import dash
from dash import html, dcc, callback, Output, Input, State, no_update, dash_table
from dash.exceptions import PreventUpdate
from flask import session
import dash_bootstrap_components as dbc
from ninjackalytics.database.models import UserSubscriptions, SubscriptionTiers, User
from ninjackalytics.database import get_sessionlocal
from .navbar import navbar
from .page_utilities.session_functions import (
    validate_access_get_alternate_div_if_invalid,
)

dash.register_page(__name__, path="/admin_usersubscriptions")


def layout():
    access, div = validate_access_get_alternate_div_if_invalid(
        session, f"/{str(__file__).split('/')[-1][:-3]}"
    )
    if not access:
        return div
    db_session = get_sessionlocal()
    user_subscriptions_data = (
        db_session.query(
            UserSubscriptions,
            User.username,
            SubscriptionTiers.tier,
        )
        .join(User, UserSubscriptions.user_id == User.id)
        .join(
            SubscriptionTiers,
            UserSubscriptions.subscription_tier_id == SubscriptionTiers.id,
        )
        .all()
    )
    db_session.close()

    data = [
        {
            "id": user_subscription.id,
            "user_id": user_id,
            "subscription_tier": sub_tier,
            "subscription_type": subscription_type,
            "subscription_start_date": subscription_start_date,
            "renewal_date": renewal_date,
            "cancelled": cancelled,
            "code_used": code_used,
        }
        for (
            user_subscription,
            user_id,
            sub_tier,
            subscription_type,
            subscription_start_date,
            renewal_date,
            cancelled,
            code_used,
        ) in user_subscriptions_data
    ]

    columns = [
        {"name": "ID", "id": "id", "editable": False},
        {"name": "User ID", "id": "user_id", "editable": True},
        {"name": "Subscription Tier", "id": "subscription_tier", "editable": True},
        {"name": "Subscription Type", "id": "subscription_type", "editable": True},
        {
            "name": "Subscription Start Date",
            "id": "subscription_start_date",
            "editable": True,
        },
        {"name": "Renewal Date", "id": "renewal_date", "editable": True},
        {"name": "Cancelled", "id": "cancelled", "editable": True},
        {"name": "Code Used", "id": "code_used", "editable": True},
    ]

    return dbc.Container(
        [
            navbar(),
            html.H1("Manage User Subscriptions", style={"color": "white"}),
            dcc.Store(id="user-subscriptions-table-store", data=data),
            # -----------------Add New User Subscription Section-----------------
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="user-id-input",
                            placeholder="Enter User ID",
                            className="mb-3",
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        dbc.Input(
                            id="subscription-tier-id-input",
                            placeholder="Enter Subscription Tier ID",
                            className="mb-3",
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        dbc.Input(
                            id="subscription-type-input",
                            placeholder="Enter Subscription Type",
                            className="mb-3",
                        ),
                        width=4,
                    ),
                ]
            ),
            dbc.Button(
                "Create New User Subscription",
                id="create-user-subscription-button",
                color="primary",
                className="mb-3",
            ),
            html.Div(
                id="create-user-subscription-feedback",
                style={"color": "white"},
            ),
            html.Div(
                [
                    dbc.Input(
                        id="filter-input",
                        placeholder="Enter filters",
                        type="text",
                        className="mb-3",
                    ),
                    dbc.Button(
                        "Apply Filters",
                        id="apply-filters-button",
                        color="primary",
                        className="mb-3",
                    ),
                ],
                className="d-flex justify-content-center",
            ),
            # -------------User Subscriptions Table-------------
            dash_table.DataTable(
                id="user-subscriptions-table",
                columns=columns,
                data=data,
                editable=True,
                row_deletable=True,
                style_table={"overflowX": "auto"},
                style_header={
                    "backgroundColor": "rgb(30, 30, 30)",
                    "color": "white",
                    "fontWeight": "bold",
                },
                style_cell={
                    "backgroundColor": "rgb(50, 50, 50)",
                    "color": "white",
                    "borderColor": "gray",
                },
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": "rgb(60, 60, 60)"}
                ],
            ),
            dbc.Button(
                "Update User Subscriptions",
                id="update-user-subscriptions-button",
                color="primary",
                className="mb-3",
            ),
            html.Div(
                id="update-user-subscriptions-feedback",
                style={"color": "white"},
            ),
        ],
        fluid=True,
        style={
            "background-image": "url('/assets/Background.jpg')",
            "background-size": "cover",
            "background-repeat": "no-repeat",
            "height": "100vh",
            "z-index": "0",
        },
    )


@callback(
    Output("user-subscriptions-table", "data"),
    Input("apply-filters-button", "n_clicks"),
    State("filter-input", "value"),
    prevent_initial_call=True,
)
def apply_filters(n_clicks, filter_input):
    if not n_clicks:
        raise PreventUpdate

    filters = {}
    if filter_input:
        filter_pairs = filter_input.split(",")
        for pair in filter_pairs:
            key, value = pair.split("=")
            filters[key.strip()] = value.strip()

    session = get_sessionlocal()
    user_subscriptions_data = (
        session.query(
            UserSubscriptions,
            User.username,
            SubscriptionTiers.tier,
        )
        .join(User, UserSubscriptions.user_id == User.id)
        .join(
            SubscriptionTiers,
            UserSubscriptions.subscription_tier_id == SubscriptionTiers.id,
        )
        .all()
    )
    session.close()

    data = [
        {
            "id": user_subscription.id,
            "user_id": user_id,
            "subscription_tier": sub_tier,
            "subscription_type": subscription_type,
            "subscription_start_date": subscription_start_date,
            "renewal_date": renewal_date,
            "cancelled": cancelled,
            "code_used": code_used,
        }
        for (
            user_subscription,
            user_id,
            sub_tier,
            subscription_type,
            subscription_start_date,
            renewal_date,
            cancelled,
            code_used,
        ) in user_subscriptions_data
    ]

    return data


@callback(
    Output("create-user-subscription-feedback", "children"),
    Input("create-user-subscription-button", "n_clicks"),
    [
        State("user-id-input", "value"),
        State("subscription-tier-id-input", "value"),
        State("subscription-type-input", "value"),
    ],
    prevent_initial_call=True,
)
def create_new_user_subscription(
    n_clicks, user_id, subscription_tier_id, subscription_type
):
    if (
        n_clicks is None
        or not user_id
        or not subscription_tier_id
        or not subscription_type
    ):
        return no_update

    session = get_sessionlocal()
    user = session.query(User).filter_by(id=user_id).first()
    sub_tier = (
        session.query(SubscriptionTiers).filter_by(id=subscription_tier_id).first()
    )

    if not user or not sub_tier:
        session.close()
        return "Invalid user ID or subscription tier ID."

    new_user_subscription = UserSubscriptions(
        user_id=user_id,
        subscription_tier_id=subscription_tier_id,
        subscription_type=subscription_type,
    )
    session.add(new_user_subscription)
    try:
        session.commit()
        feedback = "New user subscription created successfully."
    except Exception as e:
        session.rollback()
        feedback = f"Failed to create new user subscription. Error: {e}"
    session.close()
    return feedback


@callback(
    Output("update-user-subscriptions-feedback", "children"),
    Input("update-user-subscriptions-button", "n_clicks"),
    [
        State("user-subscriptions-table", "data"),
        State("user-subscriptions-table-store", "data"),
    ],
    prevent_initial_call=True,
)
def update_user_subscriptions(n_clicks, current_table_data, initial_table_data):
    if n_clicks is None:
        return no_update

    initial_ids = {row["id"] for row in initial_table_data}
    current_ids = {row["id"] for row in current_table_data}

    # Determine deleted rows
    deleted_ids = initial_ids - current_ids

    session = get_sessionlocal()
    try:
        # Handle deletions
        for deleted_id in deleted_ids:
            session.query(UserSubscriptions).filter(
                UserSubscriptions.id == deleted_id
            ).delete()

        # Handle updates and additions
        for row in current_table_data:
            user_id = (
                session.query(User.id).filter(User.username == row["user_id"]).scalar()
            )
            sub_tier_id = (
                session.query(SubscriptionTiers.id)
                .filter(SubscriptionTiers.tier == row["subscription_tier"])
                .scalar()
            )
            # Check if row exists and is not marked for deletion
            if row["id"] in current_ids - deleted_ids:
                session.query(UserSubscriptions).filter(
                    UserSubscriptions.id == row["id"]
                ).update(
                    {
                        UserSubscriptions.user_id: user_id,
                        UserSubscriptions.subscription_tier_id: sub_tier_id,
                        UserSubscriptions.subscription_type: row["subscription_type"],
                        UserSubscriptions.subscription_start_date: row[
                            "subscription_start_date"
                        ],
                        UserSubscriptions.renewal_date: row["renewal_date"],
                        UserSubscriptions.cancelled: row["cancelled"],
                        UserSubscriptions.code_used: row["code_used"],
                    }
                )

        session.commit()
        feedback = "User subscriptions updated successfully."
    except Exception as e:
        session.rollback()
        feedback = f"Failed to update user subscriptions. Error: {e}"
    finally:
        session.close()

    return feedback
