
#remember that as soon as you've updated the database you want to change the config variable
def update_db(engine):
    tables = engine.table_names()
    print(tables)

    for table in tables:
        if table == 'battle_info':
            pass
        else:
            sql = 'DROP TABLE IF EXISTS ' + str(table)
            print(sql)
            result = engine.execute(sql)

    sql = 'DROP TABLE IF EXISTS battle_info'
    print(sql)
    result = engine.execute(sql)
