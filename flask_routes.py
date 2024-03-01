from flask import render_template, session, redirect, url_for, request
from ninjackalytics.database.database import get_sessionlocal
from ninjackalytics.database.models.users import SubscriptionTiers, User
from flask_mail import Message
from pages.config import SECRET_KEY
from werkzeug.security import generate_password_hash


def init_flask_routes(server, mail):

    @server.route("/upgrade_account", methods=["GET", "POST"])
    def upgrade_account():
        # Check if user is logged in
        if "username" in session:
            # User is logged in, fetch subscription tiers and display options
            db_session = get_sessionlocal()
            subscription_tiers = db_session.query(SubscriptionTiers).all()
            db_session.close()

            # Render a template that includes the PayPal button and subscription options
            return render_template(
                "upgrade_account.html", subscription_tiers=subscription_tiers
            )
        else:
            # User is not logged in, redirect to login page
            return redirect("/account")

    def send_reset_email(email, token):
        token_url = f"https://www.ninjackalytics.com/reset_password/{token}"
        subject = "Password Reset Request"
        sender = server.config["MAIL_DEFAULT_SENDER"]
        recipients = [email]
        body = f"""
    Hi,

    Please click on the link below to reset your password:

    {token_url}

    If you did not request a password reset, please ignore this email.

    Thanks,
    Ninjackalytics Team
    """
        msg = Message(subject, sender=sender, recipients=recipients, body=body)
        mail.send(msg)

    @server.route("/request_password_reset", methods=["GET", "POST"])
    def request_password_reset_form():
        if request.method == "POST":
            email = request.form["email"]
            with get_sessionlocal() as db_session:
                user = db_session.query(User).filter_by(email=email).first()
                if user:
                    # Assuming you have already defined `send_reset_email`
                    token = user.get_reset_token(SECRET_KEY)
                    send_reset_email(user.email, token)
                    return "If an account with that email exists, a reset email has been sent."
            return "Error: Email not sent. Please try again."

        # HTML form for GET request
        return """
        <html>
            <body>
                <h2>Reset Password</h2>
                <form action="/request_password_reset" method="post">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email">
                    <input type="submit" value="Request Reset Link">
                </form>
            </body>
        </html>
        """

    @server.route("/reset_password/<token>", methods=["GET", "POST"])
    def reset_password(token):
        if request.method == "POST":
            password = request.form["password"]
            password2 = request.form["password2"]
            if password != password2:
                return "Passwords do not match."
            with get_sessionlocal() as db_session:
                user = User.verify_reset_token(token, SECRET_KEY, db_session)
                if user is None:
                    return "This is an invalid or expired token."
                user.hashed_password = generate_password_hash(password)
                db_session.commit()
                return "Your password has been updated. Please log in with your new password. <a href='/'>Return to Home Page</a>"

        # HTML form for GET request
        return """
        <html>
            <body>
                <h2>Enter New Password</h2>
                <form action="" method="post">
                    <input type="hidden" name="token" value="{token}">
                    <label for="password">New Password:</label>
                    <input type="password" id="password" name="password" required>
                    <label for="password2">Confirm Password:</label>
                    <input type="password" id="password2" name="password2" required>
                    <input type="submit" value="Reset Password">
                </form>
                <p>
                    <a href="/">Return to Home Page</a>
                </p>
            </body>
        </html>
        """.format(
            token=token
        )
