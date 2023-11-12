from sqlalchemy import Column, Integer, Text, DateTime, Boolean, ForeignKey, Numeric
from datetime import datetime
from ninjackalytics.database import Base


# Define a base model for other database tables to inherit
class BattleDbBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)


class pokemonmetadata(BattleDbBase):
    __tablename__ = "pokemonmetadata"
    Format = Column(Text, nullable=False)
    Pokemon = Column(Text, nullable=False)
    Winrate = Column(Numeric(5, 2), nullable=False)
    SampleSize = Column(Integer, nullable=False)

    def __repr__(self):
        return "<metadata: %r>"
