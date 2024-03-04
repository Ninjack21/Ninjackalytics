from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from ninjackalytics.database import Base
from itsdangerous import URLSafeTimedSerializer as Serializer
from sqlalchemy import UniqueConstraint


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(length=255), nullable=False, unique=True)
    hashed_password = Column(String(length=255), nullable=False)
    email = Column(String(length=255), nullable=False, unique=True)
    role = Column(Integer, ForeignKey("roles.id"), nullable=False)

    def get_reset_token(self, secret_key):
        # Now accepts secret_key as an argument
        s = Serializer(secret_key)
        return s.dumps({"user_id": self.id})

    @staticmethod
    def verify_reset_token(token, secret_key, db_session, expires_sec=1800):
        s = Serializer(secret_key)
        try:
            user_id = s.loads(token, max_age=expires_sec)["user_id"]
        except:
            return None
        return db_session.query(User).get(user_id)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', subscription_tier='{self.subscription_tier}')>"


class Roles(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    role = Column(String(length=50), nullable=False)
    description = Column(String(length=255), nullable=False)

    def __repr__(self):
        return f"<Roles(role='{self.role}', description='{self.description}')>"


class Pages(Base):
    __tablename__ = "pages"
    id = Column(Integer, primary_key=True)
    page_name = Column(String(length=50), nullable=False)
    page_description = Column(String(length=255), nullable=False)

    def __repr__(self):
        return f"<Pages(page_name='{self.page_name}', page_description='{self.page_description}')>"


class RolePages(Base):
    __tablename__ = "role_pages"
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)

    def __repr__(self):
        return f"<RolePages(role_id='{self.role_id}', page_name='{self.page_name}', page_description='{self.page_description}')>"


class SubscriptionTiers(Base):
    __tablename__ = "subscription_tiers"
    id = Column(Integer, primary_key=True)
    # NOTE: following the paypal naming convention here
    # i.e. the tier (basic / premium)
    product = Column(String(length=50), nullable=False)
    # i.e. the plan (annual / monthly)
    plan = Column(String(length=50), nullable=False)

    __table_args__ = (UniqueConstraint("product", "plan", name="uq_product_plan"),)


class UserSubscriptions(Base):
    __tablename__ = "user_subscriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    paypal_subscription_id = Column(String(length=255), nullable=False, unique=True)
    subscription_tier_id = Column(
        Integer, ForeignKey("subscription_tiers.id"), nullable=False
    )
    active = Column(Boolean, nullable=False, default=True)


class SubscriptionPages(Base):
    __tablename__ = "subscription_pages"
    id = Column(Integer, primary_key=True)
    sub_tier_id = Column(Integer, ForeignKey("subscription_tiers.id"), nullable=False)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)


class PromoCodeLinks(Base):
    __tablename__ = "promo_code_links"
    id = Column(Integer, primary_key=True)
    promo_code = Column(String(length=255), nullable=False, unique=True)
    paypal_link = Column(String(length=255), nullable=False, unique=True)
    paypal_button_code = Column(String(length=5000), nullable=False, unique=True)
    advertiser = Column(String(length=255), nullable=False)
    paypal_plan_id = Column(String(length=255), nullable=False, unique=True)
    subscription_tier_id = Column(
        Integer, ForeignKey("subscription_tiers.id"), nullable=False
    )
