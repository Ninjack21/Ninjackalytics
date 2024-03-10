from flask import session
import dash
from dash import html, dcc, callback, Output, Input, State, no_update, dash_table
import dash_bootstrap_components as dbc
from ninjackalytics.database.models import Pages
from ninjackalytics.database import get_sessionlocal
from .navbar import navbar
from .page_utilities.session_functions import (
    validate_access_get_alternate_div_if_invalid,
)

dash.register_page(__name__, path="/admin_pages")


def layout():
    access, div = validate_access_get_alternate_div_if_invalid(
        session, f"/{str(__file__).split('/')[-1][:-3]}", session.get("username")
    )
    if not access:
        return div
    db_session = get_sessionlocal()
    pages_data = db_session.query(Pages).all()
    db_session.close()

    data = [
        {
            "id": page.id,
            "page_name": page.page_name,
            "page_description": page.page_description,
        }
        for page in pages_data
    ]

    columns = [
        {"name": "ID", "id": "id", "editable": False},
        {"name": "Page Name", "id": "page_name", "editable": True},
        {"name": "Page Description", "id": "page_description", "editable": True},
    ]

    return dbc.Container(
        [
            navbar(),
            dcc.Store(id="pages-table-store", data=data),
            html.H1("Manage Pages", style={"color": "white"}),
            # Add New Page Section
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="page-name-input",
                            placeholder="Enter Page Name",
                            className="mb-3",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Textarea(
                            id="page-description-input",
                            placeholder="Enter Page Description",
                            className="mb-3",
                        ),
                        width=6,
                    ),
                ]
            ),
            dbc.Button(
                "Create New Page",
                id="create-page-button",
                color="primary",
                className="mb-3",
            ),
            html.Div(id="create-page-feedback", style={"color": "white"}),
            # Pages Table
            dash_table.DataTable(
                id="pages-table",
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
                "Update Pages",
                id="update-pages-button",
                color="primary",
                className="mb-3",
            ),
            html.Div(id="update-pages-feedback", style={"color": "white"}),
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
    Output("create-page-feedback", "children"),
    Input("create-page-button", "n_clicks"),
    [
        State("page-name-input", "value"),
        State("page-description-input", "value"),
    ],
    prevent_initial_call=True,
)
def create_new_page(n_clicks, page_name, page_description):
    if n_clicks is None or not page_name or not page_description:
        return no_update

    # Insert new page into the database
    with get_sessionlocal() as session:
        new_page = Pages(
            page_name=page_name,
            page_description=page_description,
        )
        session.add(new_page)
        try:
            session.commit()
            return "New page created successfully."
        except Exception as e:
            session.rollback()
            return f"Failed to create new page. Error: {e}"


@callback(
    Output("update-pages-feedback", "children"),
    Input("update-pages-button", "n_clicks"),
    State("pages-table", "data"),
    State("pages-table-store", "data"),
    prevent_initial_call=True,
)
def update_pages(n_clicks, table_data, table_store_data):
    if n_clicks is None:
        return no_update

    initial_ids = {row["id"] for row in table_store_data}
    current_ids = {row["id"] for row in table_data}

    # Determine deleted rows
    deleted_ids = initial_ids - current_ids

    with get_sessionlocal() as session:
        try:
            # Handle deletions
            for deleted_id in deleted_ids:
                session.query(Pages).filter(Pages.id == deleted_id).delete()

            # Handle updates and additions
            for row in table_data:
                # Check if row exists and is not marked for deletion
                if row["id"] in current_ids - deleted_ids:
                    session.query(Pages).filter(Pages.id == row["id"]).update(
                        {
                            Pages.page_name: row["page_name"],
                            Pages.page_description: row["page_description"],
                        }
                    )

            session.commit()
            feedback = "Pages updated successfully."
        except Exception as e:
            session.rollback()
            feedback = f"Failed to update pages. Error: {e}"

    return feedback
