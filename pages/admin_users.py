import dash
from dash import html, callback, Output, Input, State, no_update, dash_table
import dash_bootstrap_components as dbc
from ninjackalytics.database.models import User
from ninjackalytics.database import get_sessionlocal
from .navbar import navbar

dash.register_page(__name__, path="/admin_user")


def layout():
    session = get_sessionlocal()
    users_data = session.query(User).all()
    session.close()

    data = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "subscription_tier": user.subscription_tier,
            "subscription_type": user.subscription_type,
            "renewal_date": user.renewal_date,
            "code_used": user.code_used,
        }
        for user in users_data
    ]

    columns = [
        {"name": "ID", "id": "id", "editable": False},
        {"name": "Username", "id": "username", "editable": True},
        {"name": "Email", "id": "email", "editable": True},
        {"name": "Role", "id": "role", "editable": True},
        {"name": "Subscription Tier", "id": "subscription_tier", "editable": True},
        {"name": "Subscription Type", "id": "subscription_type", "editable": True},
        {"name": "Renewal Date", "id": "renewal_date", "editable": True},
        {"name": "Code Used", "id": "code_used", "editable": True},
    ]
    return dbc.Container(
        [
            navbar(),
            html.H1("Manage User", style={"color": "white"}),
            # ------- Add New User Section -------
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="username-input",
                            placeholder="Enter Username",
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
                            id="email-input",
                            placeholder="Enter Email",
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
                            id="role-input",
                            placeholder="Enter Role",
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
                            id="subscription-tier-input",
                            placeholder="Enter Subscription Tier",
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
                            id="subscription-type-input",
                            placeholder="Enter Subscription Type",
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
                            id="renewal-date-input",
                            placeholder="Enter Renewal Date",
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
                            id="code-used-input",
                            placeholder="Enter Code Used",
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
                            "Create New User",
                            id="create-user-button",
                            color="primary",
                            className="mb-3",
                        ),
                        width={"size": 6, "offset": 3},
                    )
                ]
            ),
            html.Div(id="create-user-feedback", style={"color": "white"}),
            # ------- User Table -------
            dash_table.DataTable(
                id="users-table",
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
                "Update User",
                id="update-users-button",
                color="primary",
                className="mb-3",
            ),
            html.Div(id="update-users-feedback", style={"color": "white"}),
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
    Output("create-user-feedback", "children"),
    Input("create-user-button", "n_clicks"),
    [
        State("username-input", "value"),
        State("email-input", "value"),
        State("role-input", "value"),
        State("subscription-tier-input", "value"),
        State("subscription-type-input", "value"),
        State("renewal-date-input", "value"),
        State("code-used-input", "value"),
    ],
    prevent_initial_call=True,
)
def create_new_user(
    n_clicks,
    username,
    email,
    role,
    subscription_tier,
    subscription_type,
    renewal_date,
    code_used,
):
    if n_clicks is None or username is None or email is None or role is None:
        return no_update

    # Insert new user into the database
    with get_sessionlocal() as session:
        new_user = User(
            username=username,
            email=email,
            role=role,
            subscription_tier=subscription_tier,
            subscription_type=subscription_type,
            renewal_date=renewal_date,
            code_used=code_used,
        )
        session.add(new_user)
        try:
            session.commit()
            return "New user created successfully."
        except Exception as e:
            session.rollback()
            return f"Failed to create new user. Error: {e}"


@callback(
    Output("update-users-feedback", "children"),
    Input("update-users-button", "n_clicks"),
    State("users-table", "data"),
    prevent_initial_call=True,
)
def update_roles(n_clicks, table_data):
    if n_clicks is None:
        return no_update

    with get_sessionlocal() as session:
        try:
            for row in table_data:
                session.query(User).filter(User.id == row["id"]).update(
                    {User.role: row["role"], User.description: row["description"]}
                )
            session.commit()
            feedback = "User updated successfully."
        except Exception as e:
            session.rollback()
            feedback = f"Failed to update roles. Error: {e}"

    return feedback
