import os
import sys

# Append Ninjackalytics/ninjackalytics folder to sys path
ninjackalytics_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ninjackalytics_path)

from config import SECRET, CLIENT_ID
import requests
from ninjackalytics.database.database import get_sessionlocal
from ninjackalytics.database.models.users import UserSubscriptions

flask_env = os.environ.get("FLASK_ENV")
if flask_env:
    if "production" in flask_env.lower():
        PAYPAL_API_URL = "https://api.paypal.com"
    else:
        PAYPAL_API_URL = "https://api.sandbox.paypal.com"
else:
    PAYPAL_API_URL = "https://api.sandbox.paypal.com"

SUBSCRIPTION_URL = f"{PAYPAL_API_URL}/v1/billing/subscriptions"


def get_paypal_access_token(client_id, secret):
    auth_response = requests.post(
        f"{PAYPAL_API_URL}/v1/oauth2/token",
        auth=(client_id, secret),
        headers={"Accept": "application/json"},
        data={"grant_type": "client_credentials"},
    )
    if auth_response.status_code == 200:
        return auth_response.json()["access_token"]
    else:
        return None


def check_subscription_status(subscription_id, access_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(f"{SUBSCRIPTION_URL}/{subscription_id}", headers=headers)
    if response.status_code == 200:
        subscription_status = response.json().get("status")
        print(subscription_status)
        return (
            subscription_status == "ACTIVE"
            or subscription_status == "APPROVED"
            or subscription_status == "CANCELLED"
        )
    else:
        print(f"Failed to fetch subscription status for {subscription_id}")
        return False


def update_subscription_statuses():
    access_token = get_paypal_access_token(CLIENT_ID, SECRET)
    if access_token:
        with get_sessionlocal() as db:
            try:
                subscriptions = db.query(UserSubscriptions).all()
                for subscription in subscriptions:
                    print(f"Checking subscription for user {subscription.user_id}")
                    paypal_active = check_subscription_status(
                        subscription.paypal_subscription_id, access_token
                    )
                    print(f"Paypal active: {paypal_active}")
                    # if the paypal_active is not the same as the db, update the db
                    if subscription.active != paypal_active:
                        subscription.active = paypal_active
                        db.commit()
                        print(
                            f"Updated subscription {subscription.id} to {'active' if paypal_active else 'inactive'}"
                        )

            except Exception as e:
                print(f"Error updating subscription statuses: {e}")
    else:
        print("No access token available, cannot update subscription statuses.")


if __name__ == "__main__":
    update_subscription_statuses()
