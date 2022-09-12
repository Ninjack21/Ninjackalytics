from sqlalchemy import Column, Integer, Text, DateTime, Boolean, ForeignKey, Numeric
from datetime import datetime
from database import Base

# Define a base model for other database tables to inherit
class Base(Base):

    __abstract__  = True
    id = Column(Integer, primary_key=True)

#create a model database
class battle_info(Base):
    __tablename__ = 'battle_info'
    Battle_ID = Column(Text, unique=True)
    Date_Submitted = Column(DateTime, default=datetime.utcnow)
    Format = Column(Text, nullable=False)
    P1 = Column(Text, nullable=False)
    P1_rank = Column(Integer, nullable=True)
    P1_private = Column(Boolean, nullable=False)
    P2 = Column(Text, nullable=False)
    P2_rank = Column(Integer, nullable=True)
    P2_private = Column(Boolean, nullable=False)
    Winner = Column(Text, nullable=False)

    def __repr__(self):
        return ('<Battle ID: %r>' % self.Battle_ID)

class teams(Base):
    __tablename__ = 'teams'
    Pok1 = Column(Text, nullable=False)
    Pok2 = Column(Text)
    Pok3 = Column(Text)
    Pok4 = Column(Text)
    Pok5 = Column(Text)
    Pok6 = Column(Text)
    

    def __repr__(self):
        return ('<Team: %r>' % self.id)

class actions(Base):
    __tablename__ = 'actions'
    Battle_ID = Column(Text, ForeignKey(battle_info.Battle_ID))
    Player_Name = Column(Text, nullable=False)
    Turn = Column(Integer, nullable=True)
    Action = Column(Text, nullable=False)

    def __repr__(self):
        return ('<Action: %r>' % self.Action)

class damages(Base):
    __tablename__ = 'damages'
    Battle_ID = Column(Text, ForeignKey(battle_info.Battle_ID))
    Damage = Column(Numeric(5,2), nullable=False)
    Dealer = Column(Text, nullable=False)
    Source_Name = Column(Text, nullable=True)
    Receiver = Column(Text, nullable=False)
    Turn = Column(Integer, nullable=False)
    Type = Column(Text, nullable=False)

    def __repr__(self):
        return ('<Damage: %r>' % self.Source_Name)

class healing(Base):
    __tablename__ = 'healing'
    Battle_ID = Column(Text, ForeignKey(battle_info.Battle_ID))
    Healing = Column(Numeric(5,2), nullable=False)
    Receiver = Column(Text, nullable=False)
    Source_Name = Column(Text, nullable=True)
    Turn = Column(Integer, nullable=False)
    Type = Column(Text, nullable=False)

    def __repr__(self):
        return ('<Healing: %r>' % self.Source_Name)
    
class pivots(Base):
    __tablename__ = 'pivots'
    Battle_ID = Column(Text, ForeignKey(battle_info.Battle_ID))
    Player_Name = Column(Text, nullable=False)
    Pokemon_Enter = Column(Text, nullable=False)
    Source_Name = Column(Text, nullable=True)
    Turn = Column(Integer, nullable=False)

    def __repr__(self):
        return ('<Turn: %r>' % self.Pokemon_Enter)
    
class errors(Base):
    __tablename__ = 'errors'
    Battle_ID = Column(Text, nullable=False)
    Date_Submitted = Column(DateTime, default=datetime.utcnow)
    Current_Step = Column(Text, nullable=False)
    Error_Message = Column(Text, nullable=True)
    Turn = Column(Integer, nullable=False)

    def __repr__(self):
        return ('<Error: %r>' % self.Error_Message)