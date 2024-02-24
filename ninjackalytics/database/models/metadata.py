from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, Numeric, String
from datetime import datetime
from ninjackalytics.database import Base
from sqlalchemy import UniqueConstraint


# Define a base model for other database tables to inherit
class BattleDbBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)


class pokemonmetadata(BattleDbBase):
    __tablename__ = "pokemonmetadata"
    Format = Column(String(length=255), nullable=False, index=True)
    Pokemon = Column(String(length=255), nullable=False, index=True)
    Winrate = Column(Numeric(5, 2), nullable=False)
    SampleSize = Column(Integer, nullable=False, index=True)
    Popularity = Column(Numeric(5, 2), nullable=False, index=True)
    __table_args__ = (UniqueConstraint("Format", "Pokemon", name="_format_pokemon_uc"),)

    def __repr__(self):
        return "<metadata: %r>"


class pvpmetadata(BattleDbBase):
    # pvp = pokemon vs pokemon
    __tablename__ = "pvpmetadata"
    Format = Column(String(length=255), nullable=False, index=True)
    Pokemon1 = Column(String(length=255), nullable=False, index=True)
    Pokemon2 = Column(String(length=255), nullable=False, index=True)
    Winrate = Column(Numeric(5, 2), nullable=False)
    SampleSize = Column(Integer, nullable=False, index=True)
    __table_args__ = (
        UniqueConstraint(
            "Format", "Pokemon1", "Pokemon2", name="_format_pokemon1_pokemon2_uc"
        ),
    )

    def __repr__(self):
        return "<pvpmetadata: %r>"
