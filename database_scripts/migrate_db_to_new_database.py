import os
import sys

# Append Ninjackalytics/ninjackalytics folder to sys path
ninjackalytics_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ninjackalytics_path)

from sqlalchemy.orm import make_transient
from sqlalchemy.exc import IntegrityError
from ninjackalytics.database.config import OldProductionConfig, NewProductionConfig
from tqdm import tqdm
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from ninjackalytics.database.database import get_sessionlocal
from ninjackalytics.database.models import *
from ninjackalytics.services.database_interactors.table_accessor import TableAccessor

