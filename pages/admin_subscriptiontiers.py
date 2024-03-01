from flask import session
import dash
from dash import html, dcc, callback, Output, Input, State, no_update, dash_table
import dash_bootstrap_components as dbc
from ninjackalytics.database.models import SubscriptionTiers
from ninjackalytics.database import get_sessionlocal
from .navbar import navbar
from .page_utilities.session_functions import (
    validate_access_get_alternate_div_if_invalid,
)

dash.register_page(__name__, path="/admin_subscriptiontiers")


def layout():
    access, div = validate_access_get_alternate_div_if_invalid(
        session, f"/{str(__file__).split('/')[-1][:-3]}", session.get("username")
    )
    if not access:
        return div
    db_session = get_sessionlocal()
    subscription_tiers_data = db_session.query(SubscriptionTiers).all()
    db_session.close()

    data = [
        {
            "id": tier.id,
            "product": tier.product,
            "plan": tier.plan,
        }
        for tier in subscription_tiers_data
    ]

    columns = [
        {"name": "ID", "id": "id", "editable": False},
        {"name": "Product", "id": "product", "editable": True},
        {"name": "Plan", "id": "plan", "editable": True},
    ]

    return dbc.Container(
        [
            navbar(),
            dcc.Store(id="subscription-tiers-table-store", data=data),
            html.H1("Manage Subscription Tiers", style={"color": "white"}),
            # Add New Subscription Tier Section
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="tier-name-input",
                            placeholder="Enter Product Name",
                            className="mb-3",
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        dbc.Input(
                            id="tier-annual-cost-input",
                            placeholder="Enter Plan Name",
                            className="mb-3",
                        ),
                        width=4,
                    ),
                ]
            ),
            dbc.Button(
                "Create New Tier",
                id="create-tier-button",
                color="primary",
                className="mb-3",
            ),
            html.Div(id="create-tier-feedback", style={"color": "white"}),
            # Subscription Tiers Table
            dash_table.DataTable(
                id="subscription-tiers-table",
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
                "Update Subscription Tiers",
                id="update-subscription-tiers-button",
                color="primary",
                className="mb-3",
            ),
            html.Div(id="update-subscription-tiers-feedback", style={"color": "white"}),
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
    Output("create-tier-feedback", "children"),
    Input("create-tier-button", "n_clicks"),
    [
        State("tier-name-input", "value"),
        State("tier-annual-cost-input", "value"),
    ],
    prevent_initial_call=True,
)
def create_new_subscription_tier(n_clicks, product_name, plan_name):
    if n_clicks is None or not product_name or not plan_name:
        return no_update

    # Insert new subscription tier into the database
    with get_sessionlocal() as session:
        new_tier = SubscriptionTiers(
            product=product_name,
            plan=plan_name,
        )
        session.add(new_tier)
        try:
            session.commit()
            return "New subscription tier created successfully."
        except Exception as e:
            session.rollback()
            return f"Failed to create new subscription tier. Error: {e}"


@callback(
    Output("update-subscription-tiers-feedback", "children"),
    Input("update-subscription-tiers-button", "n_clicks"),
    State("subscription-tiers-table", "data"),
    State("subscription-tiers-table-store", "data"),
    prevent_initial_call=True,
)
def update_subscription_tiers(n_clicks, table_data, stored_data):
    if n_clicks is None:
        return no_update

    stored_ids = {row["id"] for row in stored_data}
    current_ids = {row["id"] for row in table_data}

    # Determine deleted rows
    deleted_ids = stored_ids - current_ids

    with get_sessionlocal() as session:
        try:
            # Handle deletions
            for deleted_id in deleted_ids:
                session.query(SubscriptionTiers).filter(
                    SubscriptionTiers.id == deleted_id
                ).delete()

            # Handle updates and additions
            for row in table_data:
                # Check if row exists and is not marked for deletion
                if row["id"] in current_ids - deleted_ids:
                    session.query(SubscriptionTiers).filter(
                        SubscriptionTiers.id == row["id"]
                    ).update(
                        {
                            SubscriptionTiers.product: row["product"],
                            SubscriptionTiers.plan: row["plan"],
                        }
                    )

            session.commit()
            feedback = "Subscription tiers updated successfully."
        except Exception as e:
            session.rollback()
            feedback = f"Failed to update subscription tiers. Error: {e}"

    return feedback
