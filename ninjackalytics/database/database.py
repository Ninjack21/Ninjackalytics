from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import (
    DevelopmentConfig,
    TestingConfig,
    ProductionConfig,
    RemoteProductionConfig,
)
import os
import sshtunnel

Base = declarative_base()


# Get the right config based on the environment
env = os.getenv("FLASK_ENV")
if env == "development":
    config = DevelopmentConfig
elif env == "testing":
    config = TestingConfig
elif env == "production":
    config = ProductionConfig
elif env == "remote-production":
    config = RemoteProductionConfig  # won't use
else:
    # if no env is set assume testing
    config = TestingConfig


def get_db_uri():
    if env != "remote-production":
        return config.SQLALCHEMY_DATABASE_URI
    else:
        tunnel = sshtunnel.SSHTunnelForwarder(
            (RemoteProductionConfig.SSH_HOST),
            ssh_username=RemoteProductionConfig.SSH_USERNAME,
            ssh_password=RemoteProductionConfig.SSH_PASSWORD,
            remote_bind_address=RemoteProductionConfig.REMOTE_BIND_ADDRESS,
        )
        tunnel.start()
        db_uri = (
            f"mysql+mysqldb://{RemoteProductionConfig.DB_USERNAME}"
            + f":{RemoteProductionConfig.DB_PASSWORD}@127.0.0.1:{tunnel.local_bind_port}"
            + f"/{RemoteProductionConfig.DB_NAME}"
        )

    return db_uri


def get_engine():
    db_uri = get_db_uri()
    engine = create_engine(db_uri)
    return engine


def get_sessionlocal():
    engine = get_engine()
    sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return sessionlocal()
