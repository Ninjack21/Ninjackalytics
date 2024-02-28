from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from ninjackalytics.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(length=255), nullable=False, unique=True)
    hashed_password = Column(String(length=255), nullable=False)
    email = Column(String(length=255), nullable=False, unique=True)
    subscription_tier = Column(String(length=50), nullable=False)
    subscription_type = Column(String(length=50), nullable=True)  # annual or monthly
    renewal_date = Column(Date, nullable=True)
    code_used = Column(String(length=50), nullable=True)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', subscription_tier='{self.subscription_tier}')>"


class SubscriptionTiers(Base):
    __tablename__ = "subscription_tiers"
    id = Column(Integer, primary_key=True)
    tier = Column(String(length=50), nullable=False)
    annual_cost = Column(Integer, nullable=False)
    monthly_cost = Column(Integer, nullable=False)
    description = Column(String(length=255), nullable=False)


class SubscriptionPages(Base):
    __tablename__ = "subscription_pages"
    id = Column(Integer, primary_key=True)
    sub_tier_id = Column(Integer, ForeignKey("subscription_tiers.id"), nullable=False)
    page_name = Column(String(length=50), nullable=False)
    page_description = Column(String(length=255), nullable=False)


class UserSubscription(Base):
    __tablename__ = "user_subscription"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(
        Integer, ForeignKey("subscription_tiers.id"), nullable=False
    )
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    active = Column(Integer, nullable=False)

    user = relationship("User", backref="user_subscription")
    subscription = relationship("SubscriptionTiers", backref="user_subscription")

    def __repr__(self):
        return f"<UserSubscription(user_id='{self.user_id}', subscription_id='{self.subscription_id}', start_date='{self.start_date}', end_date='{self.end_date}', active='{self.active}')>"
