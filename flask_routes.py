from flask import render_template, session, redirect, url_for, request, jsonify
from ninjackalytics.database.database import get_sessionlocal
from ninjackalytics.database.models.users import (
    SubscriptionTiers,
    User,
    UserSubscriptions,
    PromoCodeLinks,
)
from flask_mail import Message
from pages.config import SECRET_KEY, CLIENT_ID, SECRET
from werkzeug.security import generate_password_hash
import requests
import paypalrestsdk
from flask_wtf.csrf import generate_csrf
import logging

logging.basicConfig(filename="app.log", level=logging.DEBUG)


def init_flask_routes(server, mail):

    @server.route("/upgrade_account_flask", methods=["GET", "POST"])
    def upgrade_account():
        if "username" in session:
            username = session["username"]
            # Assuming you're fetching `subscription_tiers` from your database as before
            db_session = get_sessionlocal()
            subscription_tiers = db_session.query(SubscriptionTiers).all()
            db_session.close()
            # Pass `username` along with `subscription_tiers` to the template
            return render_template(
                "upgrade_account.html",
                username=username,
                subscription_tiers=subscription_tiers,
            )
        else:
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

    @server.route("/handle_subscription", methods=["POST"])
    def handle_subscription():
        try:
            logging.debug("route called.")
            # Verify CSRF token
            token_sent = request.headers.get("X-CSRF-Token")
            token_stored = session.get("csrf_token")

            if not token_sent or token_sent != token_stored:
                return jsonify({"error": "CSRF token mismatch"}), 403

            # Verify user is logged in
            if "username" not in session:
                return jsonify({"error": "Unauthorized"}), 401

            print("beginning to handle subscriptions")
            data = request.json
            subscription_id = data.get("subscriptionID")
            plan_id = data.get("planID")
            username = data.get("username")

            # verify subscription with PayPal
            if not verify_subscription(subscription_id):
                print("Invalid subscription")
                return jsonify({"error": "Invalid subscription"}), 400

            if session.get("username") != username:
                print("Username mismatch")
                return jsonify({"error": "Username mismatch"}), 400

            print("we about to hit success!")
            return update_user_subscription(username, plan_id, subscription_id)
        except Exception as e:
            logging.error(f"Error: {e}")
            return jsonify({"error": "An error occurred"}), 500

    @server.route("/get_csrf_token")
    def get_csrf_token():
        token = generate_csrf()
        session["csrf_token"] = token
        return jsonify({"csrf_token": token})


# ------------------- Backend DB Functions -------------------
def update_user_subscription(username, paypal_plan_id, paypal_subscription_id):
    with get_sessionlocal() as db_session:
        user = db_session.query(User).filter_by(username=username).first()
        promocodelink = (
            db_session.query(PromoCodeLinks)
            .filter_by(paypal_plan_id=paypal_plan_id)
            .first()
        )
        if promocodelink:
            sub_tier_id = promocodelink.subscription_tier_id
        else:
            return (
                jsonify(
                    {
                        "error": "subscription not found in database - email ninjack.pokemon@gmail.com about this"
                    }
                ),
                400,
            )

        user_subscription = (
            db_session.query(UserSubscriptions).filter_by(user_id=user.id).first()
        )
        if user_subscription:
            user_subscription.subscription_tier_id = sub_tier_id
            user_subscription.active = True
            user_subscription.paypal_subscription_id = paypal_subscription_id
        else:
            new_user_subscription = UserSubscriptions(
                user_id=user.id,
                paypal_subscription_id=paypal_subscription_id,
                subscription_tier_id=sub_tier_id,
                active=True,
            )
            db_session.add(new_user_subscription)
        db_session.commit()

    return jsonify({"success": True})


# ------------------- PayPal SDK Functions -------------------
def get_paypal_access_token(client_id, secret):
    auth_response = requests.post(
        "https://api.sandbox.paypal.com/v1/oauth2/token",
        auth=(client_id, secret),
        headers={"Accept": "application/json"},
        data={"grant_type": "client_credentials"},
    )
    if auth_response.status_code == 200:
        return auth_response.json()["access_token"]
    else:
        return None


# NOTE: update this function and figure out how to properly utilize the API
def get_subscription_details(subscription_id):
    try:
        subscription = paypalrestsdk.Subscription.find(subscription_id)
        print(f"succesfully found subscription: {subscription.id}")
        return subscription
    except paypalrestsdk.ResourceNotFound:
        print(f"subscription not found: {subscription_id}")
        return None


def verify_subscription(subscription_id):
    subscription = get_subscription_details(subscription_id)
    if subscription is None:
        print("Subscription not found.")
        return False

    else:
        return True
