import dash
from dash import html, dcc, callback, Output, Input, State
from flask_mail import Message
from extensions import mail
import dash_bootstrap_components as dbc
from .navbar import navbar


dash.register_page(__name__, path="/contact")


def layout():
    return dbc.Container(
        [
            navbar(),
            dbc.Row(
                [dbc.Col(html.H1("Contact Us"), width=12, style={"color": "white"})]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Input(id="name-input", type="text", placeholder="Name"),
                        width=4,
                    ),
                    dbc.Col(
                        dcc.Input(id="email-input", type="email", placeholder="Email"),
                        width=4,
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Input(
                            id="subject-input", type="text", placeholder="Subject"
                        ),
                        width=4,
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Textarea(
                            id="message-input",
                            placeholder="Your message",
                            style={"width": "100%", "height": "150px"},
                        ),
                        width=8,
                    )
                ]
            ),
            dbc.Row(
                [dbc.Col(html.Button("Send", id="send-button", n_clicks=0), width=8)]
            ),
            dcc.Loading(html.Div(id="contact-form-feedback", style={"color": "white"})),
        ],
        style={
            "background-image": "url('/assets/Background.jpg')",
            "background-size": "cover",
            "background-repeat": "no-repeat",
            "height": "100vh",
            "z-index": "0",
        },
        fluid=True,
    )


@callback(
    Output("contact-form-feedback", "children"),
    Input("send-button", "n_clicks"),
    State("name-input", "value"),
    State("email-input", "value"),
    State("subject-input", "value"),
    State("message-input", "value"),
    prevent_initial_call=True,
)
def send_contact_form(n_clicks, name, email, subject, message):
    if n_clicks > 0:
        if not name or not email or not subject or not message:
            return "Please fill out all fields."
        if not "@" in email or not "." in email:
            return "Please enter a valid email address."
        # Construct the email message
        msg = Message(
            subject,
            recipients=["ninjackalytics.application@gmail.com"],
        )
        msg.body = f"Name: {name}\nEmail: {email}\n\n{message}"
        # Send the email
        mail.send(msg)
        return "Your message has been sent successfully!"
    return ""
