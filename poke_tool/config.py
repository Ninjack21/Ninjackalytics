#enable the development environment
DEBUG = True

#do we need to update our database?
db_design = 'update'

#define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

#define the database we are working with based on what mode we are in
if DEBUG == True:
    state = 'dev'
else: 
    state = 'production'

#now that we've defined the state, connect to the correct database
if state == 'Production':
    dialect = 'postgresql'
    username = 'hkevcdgapzwbgq'
    password = 'e4f06a129ac6687738bfb3140272e45c405746bda075681a05595a186ae84013'
    host = 'ec2-52-72-56-59.compute-1.amazonaws.com'
    database = 'd1vgs7fthk106f'
    db_uri = dialect + '://' + username + ':' + password + '@' + host + '/' + database + '.db'
    SQLALCHEMY_DATABASE_URI = db_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
elif state == 'dev':
    dialect = 'postgresql'
    username = 'postgres'
    password = 'Bja00Qx6pOnsikoOju10'
    host = r'localhost:5432'
    database = 'Ninjackalytics'
    db_uri = dialect + '://' + username + ':' + password + '@' + host + '/' + database + '.db'
    SQLALCHEMY_DATABASE_URI = db_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "fI236Kwf1uFA"

# Secret key for signing cookies
SECRET_KEY = "N2R0w98Vaiqz"