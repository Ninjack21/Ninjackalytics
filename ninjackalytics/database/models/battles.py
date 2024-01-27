from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Boolean,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from ninjackalytics.database import Base


# Define a base model for other database tables to inherit
class BattleDbBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)


class teams(BattleDbBase):
    __tablename__ = "teams"
    Pok1 = Column(String(length=70), nullable=False)
    Pok2 = Column(String(length=70))
    Pok3 = Column(String(length=70))
    Pok4 = Column(String(length=70))
    Pok5 = Column(String(length=70))
    Pok6 = Column(String(length=70))

    Battles_as_P1 = relationship(
        "battle_info",
        cascade="all, delete",
        backref="team_as_P1",
        ForeignKey=["batte_info.P1_team"],
    )
    Battles_as_P2 = relationship(
        "battle_info",
        cascade="all, delete",
        backref="team_as_P2",
        ForeignKey=["batte_info.P2_team"],
    )

    def __repr__(self):
        return "<Team: %r>" % [getattr(self, f"Pok{i}") for i in range(1, 7)]


class battle_info(BattleDbBase):
    __tablename__ = "battle_info"
    Battle_ID = Column(String(length=255), unique=True)
    Date_Submitted = Column(DateTime, default=datetime.utcnow, index=True)
    Format = Column(String(length=255), nullable=False, index=True)
    P1 = Column(String(length=255), nullable=False, index=True)
    P1_team = Column(Integer, ForeignKey(teams.id), nullable=False)
    P2 = Column(String(length=255), nullable=False, index=True)
    P2_team = Column(Integer, ForeignKey(teams.id), nullable=False)
    Rank = Column(Integer)
    Winner = Column(String(length=255), nullable=False)

    # Define relationships
    actions = relationship("actions", cascade="all, delete", backref="battle_info")
    damages = relationship("damages", cascade="all, delete", backref="battle_info")
    healing = relationship("healing", cascade="all, delete", backref="battle_info")
    pivots = relationship("pivots", cascade="all, delete", backref="battle_info")

    def __repr__(self):
        return "<Battle ID: %r>" % self.Battle_ID


class actions(BattleDbBase):
    __tablename__ = "actions"
    Battle_ID = Column(Integer, ForeignKey("battle_info.id", ondelete="CASCADE"))
    Player_Number = Column(Integer, nullable=False)
    Turn = Column(Integer, nullable=True)
    Action = Column(String(length=255), nullable=False)

    def __repr__(self):
        return "<Action: %r>" % self.Action


class damages(BattleDbBase):
    __tablename__ = "damages"
    Battle_ID = Column(
        Integer, ForeignKey("battle_info.id", ondelete="CASCADE"), index=True
    )
    Damage = Column(Numeric(5, 2), nullable=False)
    Dealer = Column(String(length=255), nullable=False)
    Dealer_Player_Number = Column(Integer, nullable=False)
    Source_Name = Column(String(length=255), nullable=True)
    Receiver = Column(String(length=255), nullable=False)
    Receiver_Player_Number = Column(Integer, nullable=False)
    Turn = Column(Integer, nullable=False)
    Type = Column(String(length=255), nullable=False)

    def __repr__(self):
        return "<Damage: %r>" % self.Source_Name


class healing(BattleDbBase):
    __tablename__ = "healing"
    Battle_ID = Column(
        Integer, ForeignKey("battle_info.id", ondelete="CASCADE"), index=True
    )
    Healing = Column(Numeric(5, 2), nullable=False)
    Receiver = Column(String(length=255), nullable=False)
    Receiver_Player_Number = Column(Integer, nullable=False)
    Source_Name = Column(String(length=255), nullable=True)
    Turn = Column(Integer, nullable=False)
    Type = Column(String(length=255), nullable=False)

    def __repr__(self):
        return "<Healing: %r>" % self.Source_Name


class pivots(BattleDbBase):
    __tablename__ = "pivots"
    Battle_ID = Column(
        Integer, ForeignKey("battle_info.id", ondelete="CASCADE"), index=True
    )
    Pokemon_Enter = Column(String(length=255), nullable=False)
    Player_Number = Column(Integer, nullable=False)
    Source_Name = Column(String(length=255), nullable=True)
    Turn = Column(Integer, nullable=False)

    def __repr__(self):
        return "<Turn: %r>" % self.Pokemon_Enter


class errors(BattleDbBase):
    __tablename__ = "errors"
    Battle_URL = Column(String(length=255), nullable=False, unique=True)
    Date_Submitted = Column(DateTime, default=datetime.utcnow)
    Error_Message = Column(String(length=255), nullable=True)
    Traceback = Column(String(length=255), nullable=True)
    Function = Column(String(length=255), nullable=True)

    def __repr__(self):
        return "<Error: %r>" % self.Error_Message
