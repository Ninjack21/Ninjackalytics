from flask import session
import dash
from dash import html, dcc, callback, Output, Input, State, no_update, dash_table
import dash_bootstrap_components as dbc
from ninjackalytics.database.models import RolePages, Pages, Roles
from ninjackalytics.database import get_sessionlocal
from .navbar import navbar
from .page_utilities.session_functions import (
    validate_access_get_alternate_div_if_invalid,
)

dash.register_page(__name__, path="/admin_rolepages")


def layout():
    access, div = validate_access_get_alternate_div_if_invalid(
        session, f"/{str(__file__).split('/')[-1][:-3]}"
    )
    if not access:
        return div
    db_session = get_sessionlocal()
    role_pages_data = (
        db_session.query(RolePages, Roles.role, Pages.page_name)
        .join(Roles, RolePages.role_id == Roles.id)
        .join(Pages, RolePages.page_id == Pages.id)
        .all()
    )
    db_session.close()

    data = [
        {
            "id": role_page.id,
            "role": role,
            "page": page,
        }
        for role_page, role, page in role_pages_data
    ]

    columns = [
        {"name": "ID", "id": "id", "editable": False},
        {"name": "Role", "id": "role", "editable": True},
        {"name": "Page", "id": "page", "editable": True},
    ]

    return dbc.Container(
        [
            navbar(),
            dcc.Store(id="role-pages-table-store", data=data),
            html.H1("Manage Role Pages", style={"color": "white"}),
            # -----------------Add New Role Page Section-----------------
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="role-id-input",
                            placeholder="Enter Role ID",
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
                    dbc.Col(
                        dbc.Textarea(
                            id="page-description-input",
                            placeholder="Enter Page Description",
                            className="mb-3",
                        ),
                        width=4,
                    ),
                ]
            ),
            dbc.Button(
                "Create New Role Page",
                id="create-role-page-button",
                color="primary",
                className="mb-3",
            ),
            html.Div(id="create-role-page-feedback", style={"color": "white"}),
            # -------------Role Pages Table-------------
            dash_table.DataTable(
                id="role-pages-table",
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
                "Update Role Pages",
                id="update-role-pages-button",
                color="primary",
                className="mb-3",
            ),
            html.Div(id="update-role-pages-feedback", style={"color": "white"}),
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
    Output("create-role-page-feedback", "children"),
    Input("create-role-page-button", "n_clicks"),
    [State("role-name-dropdown", "value"), State("page-name-dropdown", "value")],
    prevent_initial_call=True,
)
def create_new_role_page(n_clicks, role_name, page_name):
    if n_clicks is None or not role_name or not page_name:
        return no_update

    session = get_sessionlocal()
    role_id = session.query(Roles.id).filter_by(role=role_name).scalar()
    page_id = session.query(Pages.id).filter_by(page_name=page_name).scalar()

    if role_id is None or page_id is None:
        session.close()
        return "Invalid role or page name."

    new_role_page = RolePages(role_id=role_id, page_id=page_id)
    session.add(new_role_page)
    try:
        session.commit()
        feedback = "New role page created successfully."
    except Exception as e:
        session.rollback()
        feedback = f"Failed to create new role page. Error: {e}"
    session.close()
    return feedback


@callback(
    Output("update-role-pages-feedback", "children"),
    Input("update-role-pages-button", "n_clicks"),
    [
        State("role-pages-table", "data"),
        State("role-pages-table-store", "data"),
    ],
    prevent_initial_call=True,
)
def update_role_pages(n_clicks, current_table_data, initial_table_data):
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
            session.query(RolePages).filter(RolePages.id == deleted_id).delete()

        # Handle updates and additions
        for row in current_table_data:
            role_id = session.query(Roles.id).filter(Roles.role == row["role"]).scalar()
            page_id = (
                session.query(Pages.id).filter(Pages.page_name == row["page"]).scalar()
            )
            # Check if row exists and is not marked for deletion
            if row["id"] in current_ids - deleted_ids:
                session.query(RolePages).filter(RolePages.id == row["id"]).update(
                    {RolePages.role_id: role_id, RolePages.page_id: page_id}
                )

        session.commit()
        feedback = "Role pages updated successfully."
    except Exception as e:
        session.rollback()
        feedback = f"Failed to update role pages. Error: {e}"
    finally:
        session.close()

    return feedback
