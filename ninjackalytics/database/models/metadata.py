from sqlalchemy import Column, Integer, Text, DateTime, Boolean, ForeignKey, Numeric
from datetime import datetime
from ninjackalytics.database import Base
from sqlalchemy import UniqueConstraint


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
    Popularity = Column(Numeric(5, 2), nullable=False)
    __table_args__ = (UniqueConstraint("Format", "Pokemon", name="_format_pokemon_uc"),)

    def __repr__(self):
        return "<metadata: %r>"
