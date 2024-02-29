import os
import sys

# Append Ninjackalytics/ninjackalytics folder to sys path
ninjackalytics_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ninjackalytics_path)

from ninjackalytics.database.database import get_sessionlocal
from ninjackalytics.database.models import User, Roles


def make_ninjack_admin():
    # Initialize database session
    session = get_sessionlocal()

    # Check if the Admin role already exists in the database
    admin_role = session.query(Roles).filter_by(role="Admin").first()

    if not admin_role:
        raise Exception("The Admin role does not exist in the database.")

    # find ninjack user and update their role to Admin
    ninjack_user = session.query(User).filter_by(username="ninjack").first()
    if not ninjack_user:
        raise Exception("The ninjack user does not exist in the database.")

    ninjack_user.role = admin_role.id
    session.commit()
    session.close()
    print("The ninjack user has been updated to Admin.")


if __name__ == "__main__":
    make_ninjack_admin()
