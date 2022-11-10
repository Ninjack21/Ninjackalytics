from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from poke_tool.config import db_uri

engine = create_engine(db_uri)
Session = sessionmaker(engine)
