import dash
from dash import html, dcc, callback, Output, Input, State, no_update, dash_table
from dash.exceptions import PreventUpdate
from flask import session
import dash_bootstrap_components as dbc
from ninjackalytics.database.models import SubscriptionPages, Pages, SubscriptionTiers
from ninjackalytics.database import get_sessionlocal
from .navbar import navbar
from ninjackalytics.database.models import SubscriptionPages
from .page_utilities.session_functions import (
    validate_access_get_alternate_div_if_invalid,
)

dash.register_page(__name__, path="/admin_subscriptionpages")


def layout():
    access, div = validate_access_get_alternate_div_if_invalid(
        session, f"/{str(__file__).split('/')[-1][:-3]}", session.get("username")
    )
    if not access:
        return div
    db_session = get_sessionlocal()
    subscription_pages_data = (
        db_session.query(
            SubscriptionPages,
            SubscriptionTiers.product,
            SubscriptionTiers.plan,
            Pages.page_name,
        )
        .join(SubscriptionTiers, SubscriptionPages.sub_tier_id == SubscriptionTiers.id)
        .join(Pages, SubscriptionPages.page_id == Pages.id)
        .all()
    )
    db_session.close()

    data = [
        {
            "id": subscription_page.id,
            "product": product,
            "plan": plan,
            "page": page,
        }
        for subscription_page, product, plan, page in subscription_pages_data
    ]

    columns = [
        {"name": "ID", "id": "id", "editable": False},
        {"name": "Product", "id": "product", "editable": True},
        {"name": "Plan", "id": "plan", "editable": True},
        {"name": "Page", "id": "page", "editable": True},
    ]

    return dbc.Container(
        [
            navbar(),
            html.H1("Manage Subscription Pages", style={"color": "white"}),
            dcc.Store(id="subscription-pages-table-store", data=data),
            # -----------------Add New Subscription Page Section-----------------
            dbc.Row(
                [
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
                            id="page-id-input",
                            placeholder="Enter Page ID",
                            className="mb-3",
                        ),
                        width=4,
                    ),
                ]
            ),
            dbc.Button(
                "Create New Subscription Page",
                id="create-subscription-page-button",
                color="primary",
                className="mb-3",
            ),
            html.Div(id="create-subscription-page-feedback", style={"color": "white"}),
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
            # -------------Subscription Pages Table-------------
            dash_table.DataTable(
                id="subscription-pages-table",
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
                "Update Subscription Pages",
                id="update-subscription-pages-button",
                color="primary",
                className="mb-3",
            ),
            html.Div(id="update-subscription-pages-feedback", style={"color": "white"}),
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
    Output("subscription-pages-table", "data"),
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
    subscription_pages_data = (
        session.query(
            SubscriptionPages,
            SubscriptionTiers.product,
            SubscriptionTiers.plan,
            Pages.page_name,
        )
        .join(SubscriptionTiers, SubscriptionPages.sub_tier_id == SubscriptionTiers.id)
        .join(Pages, SubscriptionPages.page_id == Pages.id)
        .all()
    )
    session.close()

    data = [
        {
            "id": subscription_page.id,
            "product": product,
            "plan": plan,
            "page": page,
        }
        for subscription_page, product, plan, page in subscription_pages_data
    ]

    return data


@callback(
    Output("create-subscription-page-feedback", "children"),
    Input("create-subscription-page-button", "n_clicks"),
    [State("subscription-tier-id-input", "value"), State("page-id-input", "value")],
    prevent_initial_call=True,
)
def create_new_subscription_page(n_clicks, sub_tier_id, page_id):
    if n_clicks is None or not sub_tier_id or not page_id:
        return no_update

    session = get_sessionlocal()
    sub_tier = session.query(SubscriptionTiers).filter_by(id=sub_tier_id).first()
    page = session.query(Pages).filter_by(id=page_id).first()

    if not sub_tier or not page:
        session.close()
        return "Invalid subscription tier or page ID."

    new_subscription_page = SubscriptionPages(sub_tier_id=sub_tier_id, page_id=page_id)
    session.add(new_subscription_page)
    try:
        session.commit()
        feedback = "New subscription page created successfully."
    except Exception as e:
        session.rollback()
        feedback = f"Failed to create new subscription page. Error: {e}"
    session.close()
    return feedback


@callback(
    Output("update-subscription-pages-feedback", "children"),
    Input("update-subscription-pages-button", "n_clicks"),
    [
        State("subscription-pages-table", "data"),
        State("subscription-pages-table-store", "data"),
    ],
    prevent_initial_call=True,
)
def update_subscription_pages(n_clicks, current_table_data, initial_table_data):
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
            session.query(SubscriptionPages).filter(
                SubscriptionPages.id == deleted_id
            ).delete()

        # Handle updates and additions
        for row in current_table_data:
            sub_tier = (
                session.query(SubscriptionTiers)
                .filter_by(product=row["product"], plan=row["plan"])
                .first()
            )
            page = session.query(Pages).filter_by(page_name=row["page"]).first()
            # Check if row exists and is not marked for deletion
            if row["id"] in current_ids - deleted_ids:
                session.query(SubscriptionPages).filter(
                    SubscriptionPages.id == row["id"]
                ).update(
                    {
                        SubscriptionPages.sub_tier_id: sub_tier.id,
                        SubscriptionPages.page_id: page.id,
                    }
                )

        session.commit()
        feedback = "Subscription pages updated successfully."
    except Exception as e:
        session.rollback()
        feedback = f"Failed to update subscription pages. Error: {e}"
    finally:
        session.close()

    return feedback
