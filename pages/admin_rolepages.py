import dash
from dash import html, dcc, callback, Output, Input, State, no_update, dash_table
import dash_bootstrap_components as dbc
from ninjackalytics.database.models import RolePages, Pages, Roles
from ninjackalytics.database import get_sessionlocal
from .navbar import navbar

dash.register_page(__name__, path="/admin_rolepages")


def layout():
    session = get_sessionlocal()
    role_pages_data = session.query(RolePages).join(Pages).all()
    session.close()

    data = [
        {
            "id": role_page.id,
            "role_id": role_page.role_id,
            "page_id": role_page.page_id,
        }
        for role_page in role_pages_data
    ]

    columns = [
        {"name": "ID", "id": "id", "editable": False},
        {"name": "Role ID", "id": "role_id", "editable": True},
        {"name": "Page ID", "id": "page_id", "editable": True},
    ]

    return dbc.Container(
        [
            navbar(),
            html.H1("Manage Role Pages", style={"color": "white"}),
            # Add New Role Page Section
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
            # Role Pages Table
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
    [
        State("role-id-input", "value"),
        State("page-id-input", "value"),
        State("page-description-input", "value"),
    ],
    prevent_initial_call=True,
)
def create_new_role_page(n_clicks, role_id, page_id, page_description):
    if n_clicks is None or not role_id or not page_id or not page_description:
        return no_update

    # Insert new role page into the database
    with get_sessionlocal() as session:
        new_role_page = RolePages(
            role_id=role_id,
            page_id=page_id,
        )
        session.add(new_role_page)
        try:
            session.commit()
            return "New role page created successfully."
        except Exception as e:
            session.rollback()
            return f"Failed to create new role page. Error: {e}"


@callback(
    Output("update-role-pages-feedback", "children"),
    Input("update-role-pages-button", "n_clicks"),
    State("role-pages-table", "data"),
    prevent_initial_call=True,
)
def update_role_pages(n_clicks, table_data):
    if n_clicks is None:
        return no_update

    with get_sessionlocal() as session:
        try:
            for row in table_data:
                session.query(RolePages).filter(RolePages.id == row["id"]).update(
                    {
                        RolePages.role_id: row["role_id"],
                        RolePages.page_id: row["page_id"],
                    }
                )
            session.commit()
            feedback = "Role pages updated successfully."
        except Exception as e:
            session.rollback()
            feedback = f"Failed to update role pages. Error: {e}"

    return feedback
