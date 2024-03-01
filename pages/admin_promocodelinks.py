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
                PromoCodeLinks.paypal_link,
                PromoCodeLinks.paypal_button_code,
                PromoCodeLinks.advertiser,
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
            "paypal_link": link.paypal_link,
            "paypal_button_code": link.paypal_button_code,
            "advertiser": link.advertiser,
            "product": link.product,
            "plan": link.plan,
        }
        for link in promo_code_links
    ]

    columns = [
        {"name": "ID", "id": "id", "editable": False},
        {"name": "Promo Code", "id": "promo_code", "editable": True},
        {"name": "Paypal Link", "id": "paypal_link", "editable": True},
        {"name": "Paypal Button Code", "id": "paypal_button_code", "editable": True},
        {"name": "Advertiser", "id": "advertiser", "editable": True},
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
                            id="paypal-button-code-input",
                            placeholder="Enter Paypal Button Code",
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
                            id="paypal-sub-id-input",
                            placeholder="Enter Paypal Sub ID",
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
                            id="product-input",
                            placeholder="Enter Product (e.g., Basic, Premium)",
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
                            id="plan-input",
                            placeholder="Enter Plan (e.g., Annual, Monthly)",
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
        State("paypal-link-input", "value"),
        State("paypal-button-code-input", "value"),
        State("advertiser-input", "value"),
        State("paypal-sub-id-input", "value"),
        State("product-input", "value"),
        State("plan-input", "value"),
    ],
    prevent_initial_call=True,
)
def create_new_promo_code_link(
    n_clicks,
    promo_code,
    paypal_link,
    paypal_button_code,
    advertiser,
    paypal_sub_id,
    product,
    plan,
):
    if any(
        v is None
        for v in [
            n_clicks,
            promo_code,
            paypal_link,
            paypal_button_code,
            advertiser,
            paypal_sub_id,
            product,
            plan,
        ]
    ):
        return no_update

    with get_sessionlocal() as session:
        # Find the subscription tier by product and plan
        subscription_tier = (
            session.query(SubscriptionTiers)
            .filter_by(product=product, plan=plan)
            .first()
        )
        if subscription_tier is None:
            return "Subscription tier not found. Please check the product and plan."

        new_promo_code_link = PromoCodeLinks(
            promo_code=promo_code,
            paypal_link=paypal_link,
            paypal_button_code=paypal_button_code,
            advertiser=advertiser,
            paypal_sub_id=paypal_sub_id,
            subscription_tier_id=subscription_tier.id,  # Use the found tier's ID
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

    with get_sessionlocal() as session:
        try:
            # Handle updates and additions
            for row in table_data:
                # Fetch the corresponding SubscriptionTier based on product and plan
                subscription_tier = (
                    session.query(SubscriptionTiers)
                    .filter_by(product=row["product"], plan=row["plan"])
                    .first()
                )

                if not subscription_tier:
                    continue  # Or handle the error as you see fit

                if "id" in row and row["id"]:  # Existing PromoCodeLink
                    session.query(PromoCodeLinks).filter(
                        PromoCodeLinks.id == row["id"]
                    ).update(
                        {
                            PromoCodeLinks.promo_code: row["promo_code"],
                            PromoCodeLinks.paypal_link: row["paypal_link"],
                            PromoCodeLinks.paypal_button_code: row[
                                "paypal_button_code"
                            ],
                            PromoCodeLinks.advertiser: row["advertiser"],
                            PromoCodeLinks.subscription_tier_id: subscription_tier.id,
                        }
                    )
                else:  # New PromoCodeLink
                    new_promo_code_link = PromoCodeLinks(
                        promo_code=row["promo_code"],
                        paypal_link=row["paypal_link"],
                        paypal_button_code=row["paypal_button_code"],
                        advertiser=row["advertiser"],
                        subscription_tier_id=subscription_tier.id,
                    )
                    session.add(new_promo_code_link)

            session.commit()
            feedback = "Promo code links updated successfully."
        except Exception as e:
            session.rollback()
            feedback = f"Failed to update promo code links. Error: {e}"

    return feedback
