state = 'dev'
db_design = 'update'

if state == 'Production':
    dialect = 'postgresql'
    username = 'hkevcdgapzwbgq'
    password = 'e4f06a129ac6687738bfb3140272e45c405746bda075681a05595a186ae84013'
    host = 'ec2-52-72-56-59.compute-1.amazonaws.com'
    database = 'd1vgs7fthk106f'
    db_uri = dialect + '://' + username + ':' + password + '@' + host + '/' + database + '.db'
elif state == 'dev':
    dialect = 'postgresql'
    username = 'postgres'
    password = 'Bja00Qx6pOnsikoOju10'
    host = r'localhost:5432'
    database = 'Ninjackalytics'
    db_uri = dialect + '://' + username + ':' + password + '@' + host + '/' + database + '.db'
    print(db_uri)
else:
    print('state is not produciton or dev so not sure what state to run in')
