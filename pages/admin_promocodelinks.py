from flask import session
import dash
from dash import html, callback, Output, Input, State, no_update, dash_table, dcc
import dash_bootstrap_components as dbc
from ninjackalytics.database.models import PromoCodeLinks, SubscriptionTiers
from ninjackalytics.database import get_sessionlocal
from .navbar import navbar
from .page_utilities.session_functions import (
    validate_access_get_alternate_div_if_invalid,
)

dash.register_page(__name__, path="/admin_promocodelinks")


def fetch_promo_code_links():
    with get_sessionlocal() as db_session:
        promo_code_links = (
            db_session.query(
                PromoCodeLinks.id,
                PromoCodeLinks.promo_code,
                PromoCodeLinks.advertiser,
                PromoCodeLinks.paypal_plan_id,
                SubscriptionTiers.product,
                SubscriptionTiers.plan,
            )
            .join(
                SubscriptionTiers,
                PromoCodeLinks.subscription_tier_id == SubscriptionTiers.id,
            )
            .all()
        )

    data = [
        {
            "id": link.id,
            "promo_code": link.promo_code,
            "advertiser": link.advertiser,
            "paypal_plan_id": link.paypal_plan_id,
            "product": link.product,
            "plan": link.plan,
        }
        for link in promo_code_links
    ]

    columns = [
        {"name": "ID", "id": "id", "editable": False},
        {"name": "Promo Code", "id": "promo_code", "editable": True},
        {"name": "Advertiser", "id": "advertiser", "editable": True},
        {"name": "Paypal Plan ID", "id": "paypal_plan_id", "editable": True},
        {"name": "Product", "id": "product", "editable": False},
        {"name": "Plan", "id": "plan", "editable": False},
    ]
    return data, columns


def layout():
    access, div = validate_access_get_alternate_div_if_invalid(
        session, f"/{str(__file__).split('/')[-1][:-3]}", session.get("username")
    )
    if not access:
        return div
    data, columns = fetch_promo_code_links()
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
                            id="paypal-plan-id-input",
                            placeholder="Enter Paypal Plan ID",
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
                            id="subscription-tier-product",
                            placeholder="Enter Product (Premium or Basic)",
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
                            id="subscription-tier-plan",
                            placeholder="Enter Plan (Annual or Monthly)",
                            className="mb-3",
                        ),
                        width={"size": 6, "offset": 3},
                    )
                ]
            ),
            dbc.Button(
                "Create Promo Code Link",
                id="create-promo-code-link-button",
                color="primary",
                className="mb-3",
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
                    "maxWidth": "150px",
                    "minWidth": "150px",
                    "width": "150px",
                    "whiteSpace": "nowrap",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
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
        State("advertiser-input", "value"),
        State("paypal-plan-id-input", "value"),
        State("subscription-tier-product", "value"),
        State("subscription-tier-plan", "value"),
    ],
    prevent_initial_call=True,
)
def create_new_promo_code_link(
    n_clicks,
    promo_code,
    advertiser,
    paypal_plan_id,
    subscription_tier_product,
    subscription_tier_plan,
):
    if any(
        v is None
        for v in [
            n_clicks,
            promo_code,
            advertiser,
            paypal_plan_id,
            subscription_tier_product,
            subscription_tier_plan,
        ]
    ):
        return no_update

    with get_sessionlocal() as db_session:
        # Find the subscription tier by ID
        subscription_tier = (
            db_session.query(SubscriptionTiers)
            .filter_by(product=subscription_tier_product, plan=subscription_tier_plan)
            .first()
        )
        if subscription_tier is None:
            return "Subscription tier not found. Please check the Product and Plan entered."

        new_promo_code_link = PromoCodeLinks(
            promo_code=promo_code,
            advertiser=advertiser,
            paypal_plan_id=paypal_plan_id,
            subscription_tier_id=subscription_tier.id,
        )
        db_session.add(new_promo_code_link)
        try:
            db_session.commit()
            return "New promo code link created successfully."
        except Exception as e:
            db_session.rollback()
            return f"Failed to create new promo code link. Error: {e}"


@callback(
    Output("update-promo-code-links-feedback", "children"),
    Output("promo-code-links-table-store", "data"),
    Input("update-promo-code-links-button", "n_clicks"),
    State("promo-code-links-table", "data"),
    State("promo-code-links-table-store", "data"),
    prevent_initial_call=True,
)
def update_promo_code_links(n_clicks, table_data, stored_data):
    if n_clicks is None:
        return no_update, no_update

    with get_sessionlocal() as db_session:
        try:
            stored_ids = [row["id"] for row in stored_data if "id" in row]
            table_ids = [row["id"] for row in table_data if "id" in row]
            deleted_ids = list(set(stored_ids) - set(table_ids))
            for deleted_id in deleted_ids:
                promo_code_link = (
                    db_session.query(PromoCodeLinks).filter_by(id=deleted_id).first()
                )
                if promo_code_link:
                    db_session.delete(promo_code_link)
            # Handle updates
            for row in table_data:
                if "id" in row and row["id"] not in deleted_ids:
                    promo_code_link = (
                        db_session.query(PromoCodeLinks).filter_by(id=row["id"]).first()
                    )
                    if promo_code_link:
                        promo_code_link.promo_code = row["promo_code"]
                        promo_code_link.advertiser = row["advertiser"]
                        promo_code_link.paypal_plan_id = row["paypal_plan_id"]

                        # Find the subscription tier by ID
                        subscription_tier = (
                            db_session.query(SubscriptionTiers)
                            .filter_by(product=row["product"], plan=row["plan"])
                            .first()
                        )
                        if subscription_tier is None:
                            return "Subscription tier not found. Please check the Product and Plan entered."
                        promo_code_link.subscription_tier_id = subscription_tier.id

            # Delete rows that are no longer present

            db_session.commit()
            feedback = "Promo code links updated successfully."
        except Exception as e:
            db_session.rollback()
            feedback = f"Failed to update promo code links. Error: {e}"

    return feedback, table_data
