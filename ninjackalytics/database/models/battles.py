from sqlalchemy import Column, Integer, Text, DateTime, Boolean, ForeignKey, Numeric
from datetime import datetime
from ninjackalytics.database import Base


# Define a base model for other database tables to inherit
class BattleDbBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)


class teams(BattleDbBase):
    __tablename__ = "teams"
    Pok1 = Column(Text, nullable=False)
    Pok2 = Column(Text)
    Pok3 = Column(Text)
    Pok4 = Column(Text)
    Pok5 = Column(Text)
    Pok6 = Column(Text)

    def __repr__(self):
        return "<Team: %r>" % self.id


class battle_info(BattleDbBase):
    __tablename__ = "battle_info"
    Battle_ID = Column(Text, unique=True)
    Date_Submitted = Column(DateTime, default=datetime.utcnow)
    Format = Column(Text, nullable=False)
    P1 = Column(Text, nullable=False)
    P1_team = Column(Integer, ForeignKey(teams.id), nullable=False)
    P2 = Column(Text, nullable=False)
    P2_team = Column(Integer, ForeignKey(teams.id), nullable=False)
    Rank = Column(Integer)
    Winner = Column(Text, nullable=False)

    def __repr__(self):
        return "<Battle ID: %r>" % self.Battle_ID


class actions(BattleDbBase):
    __tablename__ = "actions"
    Battle_ID = Column(Integer, ForeignKey(battle_info.id))
    Player_Number = Column(Integer, nullable=False)
    Turn = Column(Integer, nullable=True)
    Action = Column(Text, nullable=False)

    def __repr__(self):
        return "<Action: %r>" % self.Action


class damages(BattleDbBase):
    __tablename__ = "damages"
    Battle_ID = Column(Integer, ForeignKey(battle_info.id))
    Damage = Column(Numeric(5, 2), nullable=False)
    Dealer = Column(Text, nullable=False)
    Dealer_Player_Number = Column(Integer, nullable=False)
    Source_Name = Column(Text, nullable=True)
    Receiver = Column(Text, nullable=False)
    Receiver_Player_Number = Column(Integer, nullable=False)
    Turn = Column(Integer, nullable=False)
    Type = Column(Text, nullable=False)

    def __repr__(self):
        return "<Damage: %r>" % self.Source_Name


class healing(BattleDbBase):
    __tablename__ = "healing"
    Battle_ID = Column(Integer, ForeignKey(battle_info.id))
    Healing = Column(Numeric(5, 2), nullable=False)
    Receiver = Column(Text, nullable=False)
    Receiver_Player_Number = Column(Integer, nullable=False)
    Source_Name = Column(Text, nullable=True)
    Turn = Column(Integer, nullable=False)
    Type = Column(Text, nullable=False)

    def __repr__(self):
        return "<Healing: %r>" % self.Source_Name


class pivots(BattleDbBase):
    __tablename__ = "pivots"
    Battle_ID = Column(Integer, ForeignKey(battle_info.id))
    Pokemon_Enter = Column(Text, nullable=False)
    Player_Number = Column(Integer, nullable=False)
    Source_Name = Column(Text, nullable=True)
    Turn = Column(Integer, nullable=False)

    def __repr__(self):
        return "<Turn: %r>" % self.Pokemon_Enter


class errors(BattleDbBase):
    __tablename__ = "errors"
    Battle_URL = Column(Text, nullable=False, unique=True)
    Date_Submitted = Column(DateTime, default=datetime.utcnow)
    Error_Message = Column(Text, nullable=True)
    Traceback = Column(Text, nullable=True)
    Function = Column(Text, nullable=True)

    def __repr__(self):
        return "<Error: %r>" % self.Error_Message
