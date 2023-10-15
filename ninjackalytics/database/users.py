from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import CheckConstraint
from app.database import Base
from enum import Enum as PyEnum


class SubscriptionTier(PyEnum):
    Bronze = "Bronze"
    Silver = "Silver"
    Gold = "Gold"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.Bronze)
    subscription_expiration = Column(Date, nullable=True)
