import pandas as pd
from contextlib import contextmanager

from ninjackalytics.database import SessionLocal
from ninjackalytics.database.models.battles import errors


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class ErrorDataRetriever:
    """
    A class used to retrieve error data from a database.

    ...

    Attributes
    ----------
    session : sqlalchemy.orm.session.Session
        a session object to interact with the database

    Methods
    -------
    get_errors() -> pd.DataFrame:
        Retrieves all errors from the database.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the ErrorDataRetriever object.
        """
        pass

    def get_errors(self) -> pd.DataFrame:
        """
        Retrieves all errors from the database.

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame containing all errors.
        """
        with session_scope() as session:
            errors_query = session.query(errors).all()
            df = pd.DataFrame.from_records(
                [error.__dict__ for error in errors_query],
                columns=[column.name for column in errors.__table__.columns],
            )
            return df
