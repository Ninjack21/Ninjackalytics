from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SqlEnum, DateTime
from sqlalchemy.sql import func
from .database import Base


class MembershipStatus(Enum):
    FREE = "free"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    membership_status = Column(SqlEnum(MembershipStatus), default=MembershipStatus.FREE)
    membership_expiration = Column(DateTime, default=func.now())
