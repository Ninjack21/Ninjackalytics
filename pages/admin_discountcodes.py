from flask import session
import dash
from dash import html, dcc, callback, Output, Input, State, no_update, dash_table
import dash_bootstrap_components as dbc
from ninjackalytics.database.models import DiscountCodes
from ninjackalytics.database import get_sessionlocal
from .navbar import navbar
from .page_utilities.session_functions import (
    validate_access_get_alternate_div_if_invalid,
)

dash.register_page(__name__, path="/admin_discountcodes")


def layout():
    access, div = validate_access_get_alternate_div_if_invalid(
        session, f"/{str(__file__).split('/')[-1][:-3]}"
    )
    if not access:
        return div

    db_session = get_sessionlocal()
    discount_codes_data = db_session.query(DiscountCodes).all()
    db_session.close()

    data = [
        {
            "id": discount_code.id,
            "code": discount_code.code,
            "discount": discount_code.discount,
            "advertiser": discount_code.advertiser,
        }
        for discount_code in discount_codes_data
    ]

    columns = [
        {"name": "ID", "id": "id", "editable": False},
        {"name": "Code", "id": "code", "editable": True},
        {"name": "Discount", "id": "discount", "editable": True},
        {"name": "Advertiser", "id": "advertiser", "editable": True},
    ]

    return dbc.Container(
        [
            navbar(),
            dcc.Store(id="discount-codes-table-store", data=data),
            html.H1("Manage Discount Codes", style={"color": "white"}),
            # -----------------Add New Discount Code Section-----------------
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="code-input",
                            placeholder="Enter Code",
                            className="mb-3",
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        dbc.Input(
                            id="discount-input",
                            placeholder="Enter Discount",
                            className="mb-3",
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        dbc.Input(
                            id="advertiser-input",
                            placeholder="Enter Advertiser",
                            className="mb-3",
                        ),
                        width=4,
                    ),
                ]
            ),
            dbc.Button(
                "Create New Discount Code",
                id="create-discount-code-button",
                color="primary",
                className="mb-3",
            ),
            html.Div(id="create-discount-code-feedback", style={"color": "white"}),
            # -------------Discount Codes Table-------------
            dash_table.DataTable(
                id="discount-codes-table",
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
                "Update Discount Codes",
                id="update-discount-codes-button",
                color="primary",
                className="mb-3",
            ),
            html.Div(id="update-discount-codes-feedback", style={"color": "white"}),
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
    Output("create-discount-code-feedback", "children"),
    Input("create-discount-code-button", "n_clicks"),
    [
        State("code-input", "value"),
        State("discount-input", "value"),
        State("advertiser-input", "value"),
    ],
    prevent_initial_call=True,
)
def create_new_discount_code(n_clicks, code, discount, advertiser):
    if n_clicks is None or not code or not discount or not advertiser:
        return no_update

    session = get_sessionlocal()
    existing_discount_code = session.query(DiscountCodes).filter_by(code=code).first()

    if existing_discount_code:
        session.close()
        return "Discount code already exists."

    new_discount_code = DiscountCodes(
        code=code, discount=discount, advertiser=advertiser
    )
    session.add(new_discount_code)
    try:
        session.commit()
        feedback = "New discount code created successfully."
    except Exception as e:
        session.rollback()
        feedback = f"Failed to create new discount code. Error: {e}"
    session.close()
    return feedback


@callback(
    Output("update-discount-codes-feedback", "children"),
    Input("update-discount-codes-button", "n_clicks"),
    [
        State("discount-codes-table", "data"),
        State("discount-codes-table-store", "data"),
    ],
    prevent_initial_call=True,
)
def update_discount_codes(n_clicks, current_table_data, initial_table_data):
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
            session.query(DiscountCodes).filter(DiscountCodes.id == deleted_id).delete()

        # Handle updates and additions
        for row in current_table_data:
            discount_code = (
                session.query(DiscountCodes)
                .filter(DiscountCodes.id == row["id"])
                .first()
            )
            if discount_code:
                discount_code.code = row["code"]
                discount_code.discount = row["discount"]
                discount_code.advertiser = row["advertiser"]
            else:
                new_discount_code = DiscountCodes(
                    code=row["code"],
                    discount=row["discount"],
                    advertiser=row["advertiser"],
                )
                session.add(new_discount_code)

        session.commit()
        feedback = "Discount codes updated successfully."
    except Exception as e:
        session.rollback()
        feedback = f"Failed to update discount codes. Error: {e}"
    finally:
        session.close()

    return feedback
