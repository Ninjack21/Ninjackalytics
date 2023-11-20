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

if env != "remote-production":
    engine = create_engine(
        config.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base = declarative_base()

else:
    tunnel = sshtunnel.SSHTunnelForwarder(
        (RemoteProductionConfig.SSH_HOST),
        ssh_username=RemoteProductionConfig.SSH_USERNAME,
        ssh_password=RemoteProductionConfig.SSH_PASSWORD,
        remote_bind_address=RemoteProductionConfig.REMOTE_BIND_ADDRESS,
    )
    tunnel.start()
    # Create the SQLAlchemy engine
    engine = create_engine(
        f"mysql+mysqldb://{RemoteProductionConfig.DB_USERNAME}"
        + f":{RemoteProductionConfig.DB_PASSWORD}@127.0.0.1:{tunnel.local_bind_port}"
        + f"{tunnel.local_bind_port}/{RemoteProductionConfig.DB_NAME}"
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def close_tunnel():
    tunnel.stop()
