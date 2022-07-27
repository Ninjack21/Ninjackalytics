import psycopg2 as pps
from flask_sqlalchemy import SQLAlchemy
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





# ---------------------- SQLALCHEMY requires a primary key for all tables - if we restructure in future to that then we can explore this option again











# import app

# app = app.app


# db = SQLAlchemy(app)

# #create the models

# class battle_info(db.Model):
#     Battle_ID = db.Column(db.Text, nullable=False)
#     Date_Submitted = db.Column(db.Date, nullable=False)
#     Format = db.Column(db.Text, nullable=False)
#     Player = db.Column(db.Text, nullable=False)
#     Team = db.Column(db.Integer, db.ForeignKey("team.team_id"), nullable=False)
#     Rank = db.Column(db.Integer, nullable=False)
#     Private = db.Column(db.Boolean, nullable=False)
#     Winner = db.Column(db.Text, nullable=False)

#     # def __repr__(self):
#     #     return '<battle_info %r>' % self.Battle_ID

# class actions(db.Model):
#     Battle_ID = db.Column(db.Text, nullable=False)
#     Turn = db.Column(db.Integer, nullable=False)
#     Player = db.Column(db.Text, nullable=False)
#     Action = db.Column(db.Text, nullable=False)

#     def __repr__(self):
#         return '<action %r>' % self.Action

# class damage(db.Model):
#     Battle_ID = db.Column(db.Text, nullable=False)
#     Turn = db.Column(db.Integer, nullable=False)
#     Dealer = db.Column(db.Text, nullable=False)
#     Name = db.Column(db.Text, nullable=False)
#     Receiver = db.Column(db.Text, nullable=False)
#     Damage = db.Column(db.Numeric(5,2), nullable=False)
#     Type = db.Column(db.Text, nullable=False)

#     def __repr__(self):
#         return '<damage %r>' % self.Damage

# class healing(db.Model):
#     Battle_ID = db.Column(db.Text, nullable=False)
#     Turn = db.Column(db.Integer, nullable=False)
#     Name = db.Column(db.Text, nullable=False)
#     Receiver = db.Column(db.Text, nullable=False)
#     Recovery = db.Column(db.Numeric(5,2), nullable=False)
#     Type = db.Column(db.Text, nullable=False)

#     def __repr__(self):
#         return '<healing %r>' % self.Recovery

# class switch(db.Model):
#     Battle_ID = db.Column(db.Text, nullable=False)
#     Turn = db.Column(db.Integer, nullable=False)
#     Player = db.Column(db.Text, nullable=False)
#     Pokemon_Enter = db.Column(db.Text, nullable=False)
#     Source = db.Column(db.Text, nullable=False)

#     def __repr__(self):
#         return '<switch %r>' % self.Pokemon_Enter

# class team(db.Model):
#     team_id = db.Column(db.integer, primary_key=True)
#     Pokemon1 = db.Column(db.Text, nullable=False)
#     Pokemon2 = db.Column(db.Text)
#     Pokemon3 = db.Column(db.Text)
#     Pokemon4 = db.Column(db.Text)
#     Pokemon5 = db.Column(db.Text)
#     Pokemon6 = db.Column(db.Text)

#     def __repr__(self):
#         return '<team %r>' % self.id

# class unique_battle_ids(db.Model):
#     Battle_ID = db.Column(db.Text, primary_key=True)

#     def __repr__(self):
#         return '<unique_battle_id %r>' % self.Battle_ID

# class errors(db.Model):
#     Battle_ID = db.Column(db.Text, primary_key=True)
#     Date = db.Column(db.Date, server_default=utcnow())
#     Func_Name = db.Column(db.Text)
#     Current_Step = db.Column(db.Text)
#     Parameters = db.Column(db.Text)
#     Error_Message = db.Column(db.Text)

#     def __repr__(self):
#         return '<errors %r>' % self.Current_Step



