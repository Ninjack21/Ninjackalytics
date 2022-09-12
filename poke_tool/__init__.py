from flask import Flask
import poke_tool.config as config
import os

def create_app(test_config=None, db_uri=config.db_uri, db_design = config.db_uri):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI = db_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

       # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from database import db_session

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app

# app = create_app()

# app.logger.setLevel(logging.INFO)
# app.logger.addHandler(logging.StreamHandler(sys.stdout))

# db = SQLAlchemy(app)

# #create a model database
# class battle_info(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     Battle_ID = db.Column(db.Text, unique=True)
#     Date_Submitted = db.Column(db.DateTime, default=datetime.utcnow)
#     Format = db.Column(db.Text, nullable=False)
#     P1 = db.Column(db.Text, nullable=False)
#     P1_rank = db.Column(db.Integer, nullable=True)
#     P1_private = db.Column(db.Boolean, nullable=False)
#     P2 = db.Column(db.Text, nullable=False)
#     P2_rank = db.Column(db.Integer, nullable=True)
#     P2_private = db.Column(db.Boolean, nullable=False)
#     Winner = db.Column(db.Text, nullable=False)

#     def __repr__(self):
#         return ('<Battle ID: %r>' % self.Battle_ID)

# class team(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     Pok1 = db.Column(db.Text, nullable=False)
#     Pok2 = db.Column(db.Text)
#     Pok3 = db.Column(db.Text)
#     Pok4 = db.Column(db.Text)
#     Pok5 = db.Column(db.Text)
#     Pok6 = db.Column(db.Text)
    

#     def __repr__(self):
#         return ('<Team: %r>' % self.id)

# class actions(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     Battle_ID = db.Column(db.Text, db.ForeignKey(battle_info.Battle_ID))
#     Player_Name = db.Column(db.Text, nullable=False)
#     Turn = db.Column(db.Integer, nullable=True)
#     Action = db.Column(db.Text, nullable=False)

#     def __repr__(self):
#         return ('<Action: %r>' % self.Action)

# class damages(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     Battle_ID = db.Column(db.Text, db.ForeignKey(battle_info.Battle_ID))
#     Damage = db.Column(db.Numeric(5,2), nullable=False)
#     Dealer = db.Column(db.Text, nullable=False)
#     Source_Name = db.Column(db.Text, nullable=True)
#     Receiver = db.Column(db.Text, nullable=False)
#     Turn = db.Column(db.Integer, nullable=False)
#     Type = db.Column(db.Text, nullable=False)

#     def __repr__(self):
#         return ('<Damage: %r>' % self.Source_Name)

# class healing(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     Battle_ID = db.Column(db.Text, db.ForeignKey(battle_info.Battle_ID))
#     Healing = db.Column(db.Numeric(5,2), nullable=False)
#     Receiver = db.Column(db.Text, nullable=False)
#     Source_Name = db.Column(db.Text, nullable=True)
#     Turn = db.Column(db.Integer, nullable=False)
#     Type = db.Column(db.Text, nullable=False)

#     def __repr__(self):
#         return ('<Healing: %r>' % self.Source_Name)
    
# class pivots(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     Battle_ID = db.Column(db.Text, db.ForeignKey(battle_info.Battle_ID))
#     Player_Name = db.Column(db.Text, nullable=False)
#     Pokemon_Enter = db.Column(db.Text, nullable=False)
#     Source_Name = db.Column(db.Text, nullable=True)
#     Turn = db.Column(db.Integer, nullable=False)

#     def __repr__(self):
#         return ('<Turn: %r>' % self.Pokemon_Enter)
    
# class errors(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     Battle_ID = db.Column(db.Text, nullable=False)
#     Date_Submitted = db.Column(db.DateTime, default=datetime.utcnow)
#     Current_Step = db.Column(db.Text, nullable=False)
#     Error_Message = db.Column(db.Text, nullable=True)
#     Turn = db.Column(db.Integer, nullable=False)

#     def __repr__(self):
#         return ('<Error: %r>' % self.Error_Message)

