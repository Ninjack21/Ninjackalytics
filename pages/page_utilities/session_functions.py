from ninjackalytics.database.models import User, Roles, SubscriptionTiers
from ninjackalytics.database.database import get_sessionlocal


def get_role_name(role_id):
    with get_sessionlocal() as db_session:
        role = db_session.query(Roles).filter_by(id=role_id).first()
        return role.role if role else None


def get_subscription_tier_name(subscription_tier_id):
    with get_sessionlocal() as db_session:
        subscription_tier = (
            db_session.query(SubscriptionTiers)
            .filter_by(id=subscription_tier_id)
            .first()
        )
        return subscription_tier.tier_name if subscription_tier else None
