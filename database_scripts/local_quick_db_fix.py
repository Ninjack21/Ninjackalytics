import os
import sys

# Append Ninjackalytics/ninjackalytics folder to sys path
ninjackalytics_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ninjackalytics_path)


from ninjackalytics.database.database import Base, get_engine
from ninjackalytics.database.models import (
    User,
    SubscriptionPages,
    SubscriptionTiers,
    Roles,
    RolePages,
    Pages,
    AdvertiserLinks,
    UserSubscriptions,
)


def recreate_tables():
    engine = get_engine()
    Base.metadata.bind = engine
    # Drop only the tables we're focused on
    Base.metadata.drop_all(
        engine,
        tables=[
            User.__table__,
            SubscriptionTiers.__table__,
            SubscriptionPages.__table__,
            Roles.__table__,
            RolePages.__table__,
            Pages.__table__,
            AdvertiserLinks.__table__,
            UserSubscriptions.__table__,
        ],
    )

    # Recreate those tables
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            SubscriptionTiers.__table__,
            SubscriptionPages.__table__,
            Roles.__table__,
            RolePages.__table__,
            Pages.__table__,
            AdvertiserLinks.__table__,
            UserSubscriptions.__table__,
        ],
    )


if __name__ == "__main__":
    recreate_tables()
    print("Tables dropped and recreated successfully.")
