import dash
from dash import html, callback, Output, Input, State, no_update, dash_table, dcc
from dash.exceptions import PreventUpdate
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
            "subscription_start_date": user.subscription_start_date,
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
        {
            "name": "Subscription Start Date",
            "id": "subscription_start_date",
            "editable": True,
        },
        {"name": "Renewal Date", "id": "renewal_date", "editable": True},
        {"name": "Code Used", "id": "code_used", "editable": True},
    ]
    return dbc.Container(
        [
            navbar(),
            dcc.Store(id="users-table-store", data=data),
            html.H1("Manage User", style={"color": "white"}),
            html.Div(
                [
                    dbc.Input(
                        id="filter-input",
                        placeholder="Enter filters (e.g., 'username=a_user_name,email=a_email')",
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
                page_action="native",
                page_size=20,
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
    Output("users-table", "data"),
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
    query = session.query(User)

    for key, value in filters.items():
        if hasattr(User, key):
            query = query.filter(getattr(User, key).like(f"%{value}%"))

    users_data = query.all()
    session.close()

    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "subscription_tier": user.subscription_tier,
            "subscription_type": user.subscription_type,
            "renewal_date": str(user.renewal_date),
            "code_used": user.code_used,
        }
        for user in users_data
    ]


@callback(
    Output("update-users-feedback", "children"),
    Input("update-users-button", "n_clicks"),
    State("users-table", "data"),
    State("users-table-store", "data"),
    prevent_initial_call=True,
)
def update_roles(n_clicks, table_data, stored_data):
    if n_clicks is None:
        return no_update

    initial_ids = {row["id"] for row in stored_data}
    current_ids = {row["id"] for row in table_data}

    # Determine deleted rows
    deleted_ids = initial_ids - current_ids

    with get_sessionlocal() as session:
        try:
            # Handle deletions
            for deleted_id in deleted_ids:
                session.query(User).filter(User.id == deleted_id).delete()

            # Handle updates and additions
            for row in table_data:
                # Check if row exists and is not marked for deletion
                if row["id"] in current_ids - deleted_ids:
                    session.query(User).filter(User.id == row["id"]).update(
                        {
                            User.username: row["username"],
                            User.email: row["email"],
                            User.role: row["role"],
                            User.subscription_tier: row["subscription_tier"],
                            User.subscription_type: row["subscription_type"],
                            User.subscription_start_date: row[
                                "subscription_start_date"
                            ],
                            User.renewal_date: row["renewal_date"],
                            User.code_used: row["code_used"],
                        }
                    )

            session.commit()
            feedback = "User updated successfully."
        except Exception as e:
            session.rollback()
            feedback = f"Failed to update roles. Error: {e}"

    return feedback
