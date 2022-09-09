from sqlalchemy import create_engine

def connection(db_uri):
    print('create engine')
    engine = create_engine(db_uri)
    print('now get connection')
    with engine.connect() as connection:
        return(connection)

def create_engine(db_uri):
    engine = create_engine(db_uri)
    return(engine)