from flask import session
import dash
from dash import html, callback, Output, Input, State, no_update, dash_table, dcc
import dash_bootstrap_components as dbc
from ninjackalytics.database.models import Roles, PromoCodeLinks
from ninjackalytics.database import get_sessionlocal
from .navbar import navbar
from .page_utilities.session_functions import (
    validate_access_get_alternate_div_if_invalid,
)

dash.register_page(__name__, path="/admin_promocodelinks")


def layout():
    access, div = validate_access_get_alternate_div_if_invalid(
        session, f"/{str(__file__).split('/')[-1][:-3]}", session.get("username")
    )
    if not access:
        return div
    db_session = get_sessionlocal()
    roles_data = db_session.query(Roles).all()
    db_session.close()

    data = [
        {
            "id": promo_code_link.id,
            "promo_code": promo_code_link.promo_code,
            "paypal_link": promo_code_link.paypal_link,
            "advertiser": promo_code_link.advertiser,
            "subscription_tier_id": promo_code_link.subscription_tier_id,
        }
        for promo_code_link in db_session.query(PromoCodeLinks).all()
    ]

    columns = [
        {"name": "ID", "id": "id", "editable": False},
        {"name": "Promo Code", "id": "promo_code", "editable": True},
        {"name": "Paypal Link", "id": "paypal_link", "editable": True},
        {"name": "Advertiser", "id": "advertiser", "editable": True},
        {
            "name": "Subscription Tier ID",
            "id": "subscription_tier_id",
            "editable": True,
        },
    ]
    return dbc.Container(
        [
            navbar(),
            dcc.Store(id="promo-code-links-table-store", data=data),
            html.H1("Manage Promo Code Links", style={"color": "white"}),
            # ------- Add New Promo Code Link Section -------
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="promo-code-input",
                            placeholder="Enter Promo Code",
                            className="mb-3",
                        ),
                        width={"size": 6, "offset": 3},
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="paypal-link-input",
                            placeholder="Enter Paypal Link",
                            className="mb-3",
                        ),
                        width={"size": 6, "offset": 3},
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="advertiser-input",
                            placeholder="Enter Advertiser",
                            className="mb-3",
                        ),
                        width={"size": 6, "offset": 3},
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="subscription-tier-id-input",
                            placeholder="Enter Subscription Tier ID",
                            className="mb-3",
                        ),
                        width={"size": 6, "offset": 3},
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Create New Promo Code Link",
                            id="create-promo-code-link-button",
                            color="primary",
                            className="mb-3",
                        ),
                        width={"size": 6, "offset": 3},
                    )
                ]
            ),
            html.Div(id="create-promo-code-link-feedback", style={"color": "white"}),
            # ------- Promo Code Links Table -------
            dash_table.DataTable(
                id="promo-code-links-table",
                columns=columns,
                data=data,
                editable=True,
                row_deletable=True,  # Optional: if you want to allow deleting rows
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
                "Update Promo Code Links",
                id="update-promo-code-links-button",
                color="primary",
                className="mb-3",
            ),
            html.Div(id="update-promo-code-links-feedback", style={"color": "white"}),
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
    Output("create-promo-code-link-feedback", "children"),
    Input("create-promo-code-link-button", "n_clicks"),
    [
        State("promo-code-input", "value"),
        State("paypal-link-input", "value"),
        State("advertiser-input", "value"),
        State("subscription-tier-id-input", "value"),
    ],
    prevent_initial_call=True,
)
def create_new_promo_code_link(
    n_clicks, promo_code, paypal_link, advertiser, subscription_tier_id
):
    if (
        n_clicks is None
        or promo_code is None
        or paypal_link is None
        or advertiser is None
        or subscription_tier_id is None
    ):
        return no_update

    # Insert new promo code link into the database
    with get_sessionlocal() as session:
        new_promo_code_link = PromoCodeLinks(
            promo_code=promo_code,
            paypal_link=paypal_link,
            advertiser=advertiser,
            subscription_tier_id=subscription_tier_id,
        )
        session.add(new_promo_code_link)
        try:
            session.commit()
            return "New promo code link created successfully."
        except Exception as e:
            session.rollback()
            return f"Failed to create new promo code link. Error: {e}"


@callback(
    Output("update-promo-code-links-feedback", "children"),
    Input("update-promo-code-links-button", "n_clicks"),
    State("promo-code-links-table", "data"),
    State("promo-code-links-table-store", "data"),
    prevent_initial_call=True,
)
def update_promo_code_links(n_clicks, table_data, stored_data):
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
                session.query(PromoCodeLinks).filter(
                    PromoCodeLinks.id == deleted_id
                ).delete()

            # Handle updates and additions
            for row in table_data:
                if row["id"] in current_ids - deleted_ids:
                    session.query(PromoCodeLinks).filter(
                        PromoCodeLinks.id == row["id"]
                    ).update(
                        {
                            PromoCodeLinks.promo_code: row["promo_code"],
                            PromoCodeLinks.paypal_link: row["paypal_link"],
                            PromoCodeLinks.advertiser: row["advertiser"],
                            PromoCodeLinks.subscription_tier_id: row[
                                "subscription_tier_id"
                            ],
                        }
                    )
                else:
                    new_promo_code_link = PromoCodeLinks(
                        promo_code=row["promo_code"],
                        paypal_link=row["paypal_link"],
                        advertiser=row["advertiser"],
                        subscription_tier_id=row["subscription_tier_id"],
                    )
                    session.add(new_promo_code_link)

            session.commit()
            feedback = "Promo code links updated successfully."
        except Exception as e:
            session.rollback()
            feedback = f"Failed to update promo code links. Error: {e}"

    return feedback
