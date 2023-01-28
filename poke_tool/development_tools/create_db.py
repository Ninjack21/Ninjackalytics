from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import sys
import os

parent_path = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(1, parent_path)

from config import db_uri

engine = create_engine(db_uri)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()

Base.metadata.create_all(bind=engine)
print("db created")
