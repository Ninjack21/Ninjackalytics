from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import DevelopmentConfig, TestingConfig, ProductionConfig
import os

# Get the right config based on the environment
env = os.getenv('FLASK_ENV')
if env == 'development':
    config = DevelopmentConfig
elif env == 'testing':
    config = TestingConfig
elif env == 'production':
    config = ProductionConfig
else:
    raise ValueError("Unknown environment, set FLASK_ENV environment variable to either 'development', 'testing', or 'production'")

engine = create_engine(config.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
