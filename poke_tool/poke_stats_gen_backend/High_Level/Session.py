from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import db_uri

engine = create_engine(db_uri)
Session = sessionmaker(engine)
