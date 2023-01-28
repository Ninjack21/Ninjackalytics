from sqlalchemy import create_engine
from sqlalchemy import inspect

import sys
import os

parent_path = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(1, parent_path)

from config import db_uri


engine = create_engine(db_uri)
inspector = inspect(engine)

table_names = inspector.get_table_names()

print("delete all tables")
for table in table_names:
    sql = "DROP TABLE IF EXISTS " + str(table) + " CASCADE"
    result = engine.execute(sql)
print("all tables deleted")

import create_db
