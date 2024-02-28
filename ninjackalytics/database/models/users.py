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
    role = Column(Integer, ForeignKey("roles.id"), nullable=False)
    subscription_tier = Column(
        Integer, ForeignKey("subscription_tiers.id"), nullable=True
    )
    subscription_type = Column(String(length=50), nullable=True)  # annual or monthly
    subscription_start_date = Column(Date, nullable=True)
    renewal_date = Column(Date, nullable=True)
    code_used = Column(String(length=50), nullable=True)

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
    tier = Column(String(length=50), nullable=False)
    annual_cost = Column(Integer, nullable=False)
    monthly_cost = Column(Integer, nullable=False)
    description = Column(String(length=255), nullable=False)


# define the pages that are accessible via each subscription tier ID
class SubscriptionPages(Base):
    __tablename__ = "subscription_pages"
    id = Column(Integer, primary_key=True)
    sub_tier_id = Column(Integer, ForeignKey("subscription_tiers.id"), nullable=False)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)


class DiscountCodes(Base):
    __tablename__ = "discount_codes"
    id = Column(Integer, primary_key=True)
    code = Column(String(length=50), nullable=False, unique=True)
    discount = Column(Integer, nullable=False)
    advertiser = Column(String(length=255), nullable=False)

    def __repr__(self):
        return f"<DiscountCodes(code='{self.code}', discount='{self.discount}', advertiser='{self.advertiser}')>"
