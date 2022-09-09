print('load stuff')
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import logging
import sys
import config
from datetime import datetime
# print('try to load init_db')
import init_db as idb

db_uri = config.db_uri
idb.check_if_need_create_db(db_uri)

#now create the engine and check if need to update
engine = create_engine(db_uri)
db_design = config.db_design
recreate = idb.check_if_need_update_db(db_design, engine, db_uri)

def create_app():
    # create and configure the app
    print('try to create app')
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='30zO8qGf2oLLH1&d@aE!',
    )

    app.config['SQLALCHEMY_DATABASE_URI'] = config.db_uri
        
    # import core
    # app.register_blueprint(core.bp)

    return app

# #initialize the database by calling our special function which checks for updates as well
# import init_db as idb
# db_design = config.db_design
# print('trying to initialize the database')
# idb.initialize_database(db_design)

app = create_app()
print('succesfully created app')

app.logger.setLevel(logging.INFO)
app.logger.addHandler(logging.StreamHandler(sys.stdout))

db = SQLAlchemy(app)

#create a model database
class battle_info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Battle_ID = db.Column(db.Text, unique=True)
    Date_Submitted = db.Column(db.DateTime, default=datetime.utcnow)
    Format = db.Column(db.Text, nullable=False)
    P1 = db.Column(db.Text, nullable=False)
    P1_rank = db.Column(db.Integer, nullable=True)
    P1_private = db.Column(db.Boolean, nullable=False)
    P2 = db.Column(db.Text, nullable=False)
    P2_rank = db.Column(db.Integer, nullable=True)
    P2_private = db.Column(db.Boolean, nullable=False)
    Winner = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return ('<Battle ID: %r>' % self.Battle_ID)

class team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Pok1 = db.Column(db.Text, nullable=False)
    Pok2 = db.Column(db.Text)
    Pok3 = db.Column(db.Text)
    Pok4 = db.Column(db.Text)
    Pok5 = db.Column(db.Text)
    Pok6 = db.Column(db.Text)
    

    def __repr__(self):
        return ('<Team: %r>' % self.id)

class actions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Battle_ID = db.Column(db.Text, db.ForeignKey(battle_info.Battle_ID))
    Player_Name = db.Column(db.Text, nullable=False)
    Turn = db.Column(db.Integer, nullable=True)
    Action = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return ('<Action: %r>' % self.Action)

class damages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Battle_ID = db.Column(db.Text, db.ForeignKey(battle_info.Battle_ID))
    Damage = db.Column(db.Numeric(5,2), nullable=False)
    Dealer = db.Column(db.Text, nullable=False)
    Source_Name = db.Column(db.Text, nullable=True)
    Receiver = db.Column(db.Text, nullable=False)
    Turn = db.Column(db.Integer, nullable=False)
    Type = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return ('<Damage: %r>' % self.Source_Name)

class healing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Battle_ID = db.Column(db.Text, db.ForeignKey(battle_info.Battle_ID))
    Healing = db.Column(db.Numeric(5,2), nullable=False)
    Receiver = db.Column(db.Text, nullable=False)
    Source_Name = db.Column(db.Text, nullable=True)
    Turn = db.Column(db.Integer, nullable=False)
    Type = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return ('<Healing: %r>' % self.Source_Name)
    
class pivots(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Battle_ID = db.Column(db.Text, db.ForeignKey(battle_info.Battle_ID))
    Player_Name = db.Column(db.Text, nullable=False)
    Pokemon_Enter = db.Column(db.Text, nullable=False)
    Source_Name = db.Column(db.Text, nullable=True)
    Turn = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return ('<Turn: %r>' % self.Pokemon_Enter)
    
class errors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Battle_ID = db.Column(db.Text, nullable=False)
    Date_Submitted = db.Column(db.DateTime, default=datetime.utcnow)
    Current_Step = db.Column(db.Text, nullable=False)
    Error_Message = db.Column(db.Text, nullable=True)
    Turn = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return ('<Error: %r>' % self.Error_Message)

print('do we need to recreate?')
print(str(recreate))
if recreate == True:
    db.create_all()
    print('created all tables from model')