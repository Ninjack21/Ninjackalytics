from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import DevelopmentConfig, TestingConfig, ProductionConfig
import os
import sqlite3
import click
from flask import current_app, g

# =================== Config and Connection ===================

# Get the right config based on the environment
env = os.getenv("FLASK_ENV")
if env == "development":
    config = DevelopmentConfig
elif env == "testing":
    config = TestingConfig
elif env == "production":
    config = ProductionConfig
else:
    raise ValueError(
        "Unknown environment, set FLASK_ENV environment variable to either 'development', 'testing', or 'production'"
    )

engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# =================== DB Interactions ===================


def get_db():
    if "db" not in g:
        g.db = SessionLocal()
    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    # Import all models here
    from app.models.users import User
    from app.models.battles import (
        teams,
        battle_info,
        actions,
        damages,
        healing,
        pivots,
        errors,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
