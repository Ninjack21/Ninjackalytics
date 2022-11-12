from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import db_uri

engine = create_engine(db_uri)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import poke_stats_gen_backend.models
    import auth.models

    Base.metadata.create_all(bind=engine)


def update_db():
    import poke_stats_gen_backend.models
    import auth.models

    print("update db currently just deletes all tables in the database")
    tables = engine.table_names()

    for table in tables:
        sql = "DROP TABLE IF EXISTS " + str(table) + " CASCADE"
        print(sql)
        result = engine.execute(sql)

    print("now that we deleted everything - recreate it")
    init_db()
