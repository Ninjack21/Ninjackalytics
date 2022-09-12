from sqlalchemy import Column, Integer, Text, DateTime, Boolean, ForeignKey, Numeric, Text
from datetime import datetime
from database import Base

# Define a base model for other database tables to inherit
class Base(Base):

    __abstract__  = True

    id            = Column(Integer, primary_key=True)
    date_created  = Column(DateTime,  default=datetime.utcnow)
    date_modified = Column(DateTime,  default=datetime.utcnow, onupdate=datetime.utcnow)


class tiers(Base):

    __tablename__ = 'tiers'

    name = Column(Text, nullable=False)
    monthly_cost = Column(Numeric(5,2), nullable=False)
    annual_cost = Column(Numeric(5,2), nullable=False)

    #new instance instantiation procedure
    def __init__(self, name, monthcost, annualcost):
        self.name = name
        self.monthly_cost = monthcost
        self.annual_cost = annualcost
    
    def __repr__(self):
        return '<Tier %r>' % (self.name)

class users(Base):

    __tablename__ = 'auth_user'

    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    password = Column(Text, nullable=False)
    role = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False)
    tier = Column(Integer, ForeignKey(tiers.id), nullable=False)

    #new instance instantiation procedure
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
    
    def __repr__(self):
        return '<User %r>' % (self.name)