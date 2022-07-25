from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import sys
import config


def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='30zO8qGf2oLLH1&d@aE!',
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = config.db_uri
        
    if config.state == 'localhost': 
        from . import core
    else: 
        import core
    app.register_blueprint(core.bp)
    

    return app

app = create_app()

db = SQLAlchemy(app)

app.logger.setLevel(logging.INFO)
app.logger.addHandler(logging.StreamHandler(sys.stdout))

#create the models

class battle_info(db.Model):
    Battle_ID = db.Column(db.Text, nullable=False)
    Date_Submitted = db.Column(db.Date, nullable=False)
    Format = db.Column(db.Text, ForeignKey("team.team_id"), nullable=False)
    Player = db.Column(db.Text, nullable=False)
    Team = db.Column(db.Integer, nullable=False)
    Rank = db.Column(db.Integer, nullable=False)
    Private = db.Column(db.Boolean, nullable=False)
    Winner = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<battle_info %r>' % self.Battle_ID

class actions(db.Model):
    Battle_ID = db.Column(db.Text, nullable=False)
    Turn = db.Column(db.Integer, nullable=False)
    Player = db.Column(db.Text, nullable=False)
    Action = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<action %r>' % self.Action

class damage(db.Model):
    Battle_ID = db.Column(db.Text, nullable=False)
    Turn = db.Column(db.Integer, nullable=False)
    Dealer = db.Column(db.Text, nullable=False)
    Name = db.Column(db.Text, nullable=False)
    Receiver = db.Column(db.Text, nullable=False)
    Damage = db.Column(db.Numeric(5,2), nullable=False)
    Type = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<damage %r>' % self.Damage

class healing(db.Model):
    Battle_ID = db.Column(db.Text, nullable=False)
    Turn = db.Column(db.Integer, nullable=False)
    Name = db.Column(db.Text, nullable=False)
    Receiver = db.Column(db.Text, nullable=False)
    Recovery = db.Column(db.Numeric(5,2), nullable=False)
    Type = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<healing %r>' % self.Recovery

class switch(db.Model):
    Battle_ID = db.Column(db.Text, nullable=False)
    Turn = db.Column(db.Integer, nullable=False)
    Player = db.Column(db.Text, nullable=False)
    Pokemon_Enter = db.Column(db.Text, nullable=False)
    Source = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<switch %r>' % self.Pokemon_Enter

class team(db.Model):
    team_id = db.Column(db.integer, primary_key=True)
    Pokemon1 = db.Column(db.Text, nullable=False)
    Pokemon2 = db.Column(db.Text)
    Pokemon3 = db.Column(db.Text)
    Pokemon4 = db.Column(db.Text)
    Pokemon5 = db.Column(db.Text)
    Pokemon6 = db.Column(db.Text)

    def __repr__(self):
        return '<team %r>' % self.id

class unique_battle_ids(db.Model):
    Battle_ID = db.Column(db.Text, primary_key=True)

    def __repr__(self):
        return '<unique_battle_id %r>' % self.Battle_ID

class errors(db.Model):
    Battle_ID = db.Column(db.Text, primary_key=True)
    Date = db.Column(db.Date, server_default=utcnow())
    Func_Name = db.Column(db.Text)
    Current_Step = db.Column(db.Text)
    Parameters = db.Column(db.Text)
    Error_Message = db.Column(db.Text)

    def __repr__(self):
        return '<errors %r>' % self.Current_Step