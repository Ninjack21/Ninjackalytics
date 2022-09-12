
#remember that as soon as you've updated the database you want to change the config variable
def update_db(engine):
    print('update db currently just deletes all tables in the database')
    tables = engine.table_names()

    for table in tables:
        sql = 'DROP TABLE IF EXISTS ' + str(table) + ' CASCADE'
        print(sql)
        result = engine.execute(sql)


    
