import dash
from dash import html, callback, Output, Input, State, no_update, dash_table
import dash_bootstrap_components as dbc
from ninjackalytics.database.models import Roles
from ninjackalytics.database import get_sessionlocal
from .navbar import navbar

dash.register_page(__name__, path="/admin_roles")


def layout():
    session = get_sessionlocal()
    roles_data = session.query(Roles).all()
    session.close()

    data = [
        {"id": role.id, "role": role.role, "description": role.description}
        for role in roles_data
    ]

    columns = [
        {"name": "ID", "id": "id", "editable": False},
        {"name": "Role", "id": "role", "editable": True},
        {"name": "Description", "id": "description", "editable": True},
    ]
    return dbc.Container(
        [
            navbar(),
            html.H1("Manage Roles", style={"color": "white"}),
            # ------- Add New Role Section -------
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="role-name-input",
                            placeholder="Enter Role Name",
                            className="mb-3",
                        ),
                        width={"size": 6, "offset": 3},
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Textarea(
                            id="role-description-input",
                            placeholder="Enter Role Description",
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
                            "Create New Role",
                            id="create-role-button",
                            color="primary",
                            className="mb-3",
                        ),
                        width={"size": 6, "offset": 3},
                    )
                ]
            ),
            html.Div(id="create-role-feedback", style={"color": "white"}),
            # ------- Roles Table -------
            dash_table.DataTable(
                id="roles-table",
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
                "Update Roles",
                id="update-roles-button",
                color="primary",
                className="mb-3",
            ),
            html.Div(id="update-roles-feedback", style={"color": "white"}),
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
    Output("create-role-feedback", "children"),
    Input("create-role-button", "n_clicks"),
    [State("role-name-input", "value"), State("role-description-input", "value")],
    prevent_initial_call=True,
)
def create_new_role(n_clicks, role_name, role_description):
    if n_clicks is None or role_name is None or role_description is None:
        return no_update

    # Insert new role into the database
    with get_sessionlocal() as session:
        new_role = Roles(role=role_name, description=role_description)
        session.add(new_role)
        try:
            session.commit()
            return "New role created successfully."
        except Exception as e:
            session.rollback()
            return f"Failed to create new role. Error: {e}"


@callback(
    Output("update-roles-feedback", "children"),
    Input("update-roles-button", "n_clicks"),
    State("roles-table", "data"),
    prevent_initial_call=True,
)
def update_roles(n_clicks, table_data):
    if n_clicks is None:
        return no_update

    with get_sessionlocal() as session:
        try:
            for row in table_data:
                session.query(Roles).filter(Roles.id == row["id"]).update(
                    {Roles.role: row["role"], Roles.description: row["description"]}
                )
            session.commit()
            feedback = "Roles updated successfully."
        except Exception as e:
            session.rollback()
            feedback = f"Failed to update roles. Error: {e}"

    return feedback
