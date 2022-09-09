from sqlalchemy_utils import database_exists, create_database

def check_if_need_create_db(db_uri):

    #check to see if the database exists and if it doesn't, create it
    print('prepare to check database existence')
    if not database_exists(db_uri):
        print('trying to create database')
        create_database(db_uri)
        print('database succesfully created')

def check_if_need_update_db(db_design, engine, db_uri):
    #if the database design is to be updated - run the one time custom update_db script
    #don't forget to change the db_design variable in config immediately after you do this, though
    print('check if need update db design')
    if db_design == 'update':
        print('need to update design')
        import update_db
        update_db.update_db(engine)
        print('updated design')
        #return a true or false to tell the app if it should try creating all of the tables or if they already exist just leave it
        return(True)
    else:
        return(False)


    