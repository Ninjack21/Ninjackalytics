from sqlalchemy_utils import database_exists, create_database

def startup_db_check(db, db_uri, db_design, engine):
    #first, check if the database needs to be created
    if not database_exists(db_uri):
        create_database(db_uri)
    
    #now check if the database needs to be updated
    if db_design == 'update':
        from update_db import update_db
        update_db(engine)
        #return a true or false to tell the app if it should try creating all of the tables or if they already exist just leave it
        updated = True
    else:
        updated = False
    
    #if we did update then import the database models and create them
    if updated == True:
        print('prepare to import poke_tool')
        import poke_tool.db
        print('now create all')
        db.create_all()