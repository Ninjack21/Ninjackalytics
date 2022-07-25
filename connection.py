import psycopg2 as pps
import config

def connection():
    """
    this function checks the config file to determine what state we want to work in right now
    """
    state = config.state
    if state == 'production':
        host = 'ec2-52-72-56-59.compute-1.amazonaws.com'
        database = 'd1vgs7fthk106f'
        user = 'hkevcdgapzwbgq'
        password = 'e4f06a129ac6687738bfb3140272e45c405746bda075681a05595a186ae84013'
    elif state == 'dev':
        host = 'ec2-34-233-115-14.compute-1.amazonaws.com'
        database = 'dd1vv602smkivi'
        user = 'nmuwkhjotaaskw'
        password = '72d96dbc99aca32c929d466f77925a6141cfee480317847a16f4a5dc35e765d7'

    elif state == 'localhost':
        host = 'localhost'
        database = 'Ninjackalytics'
        user = 'postgres'
        password = 'Bja00Qx6pOnsikoOju10'
    else: 
        return ('did not enter valid state')

    conn = pps.connect(host = host, database = database, user = user, password = password)
    return (conn)