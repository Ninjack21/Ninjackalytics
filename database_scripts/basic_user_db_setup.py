import os
import sys

current_script_path = os.path.abspath(__file__)
parent_directory = os.path.dirname(os.path.dirname(current_script_path))
sys.path.append(parent_directory)

from ninjackalytics.database.database import get_sessionlocal
from ninjackalytics.database.models import (
    Pages,
    Roles,
    SubscriptionTiers,
    SubscriptionPages,
    RolePages,
)


def create_basic_roles():
    # Initialize database session
    session = get_sessionlocal()

    # List of basic roles
    basic_roles = ["Admin", "Content_Creator", "User"]

    # Check if the roles already exist in the database
    for role in basic_roles:
        existing_role = session.query(Roles).filter_by(role=role).first()
        if not existing_role:
            # Create a new Roles entry
            new_role = Roles(role=role, description="")
            session.add(new_role)
            print(f"Added new role: {role}")

    # Commit changes to the database
    session.commit()
    print("All new roles have been added to the database.")
    session.close()


def create_basic_subscription_tiers():

    session = get_sessionlocal()

    basic_tiers = [
        {"tier": "Free", "annual_cost": 0, "monthly_cost": 0, "description": ""},
        {"tier": "Basic", "annual_cost": 120, "monthly_cost": 15, "description": ""},
        {"tier": "Premium", "annual_cost": 240, "monthly_cost": 30, "description": ""},
    ]

    # Check if the subscription tiers already exist in the database
    for tier in basic_tiers:
        existing_tier = (
            session.query(SubscriptionTiers).filter_by(tier=tier["tier"]).first()
        )
        if not existing_tier:
            # Create a new SubscriptionTiers entry
            new_tier = SubscriptionTiers(**tier)
            session.add(new_tier)
            print(f"Added new subscription tier: {tier['tier']}")

    # Commit changes to the database
    session.commit()
    print("All new subscription tiers have been added to the database.")
    session.close()


def initialize_page_entries():
    pages_directory = os.path.join(parent_directory, "pages")

    # Initialize database session
    session = get_sessionlocal()

    # List all Python files in the 'pages' directory
    for file_name in os.listdir(pages_directory):
        if (
            file_name.endswith(".py")
            and file_name != "__init__.py"
            and "config" not in file_name
            and "navbar" not in file_name
        ):
            # Remove '.py' to get the page name
            page_name = file_name[:-3]

            # Check if the page already exists in the database
            existing_page = session.query(Pages).filter_by(page_name=page_name).first()
            if not existing_page:
                # Create a new Pages entry
                new_page = Pages(page_name=page_name, page_description="")
                session.add(new_page)
                print(f"Added new page: {page_name}")

    # Commit changes to the database
    session.commit()
    print("All new pages have been added to the database.")
    session.close()


def create_role_pages_entries():

    session = get_sessionlocal()

    # Get all roles and pages from the database
    roles = session.query(Roles).all()
    pages = session.query(Pages).all()

    # for elevated roles, will assign all pages they should have access to
    # will have security features in app first check for role based access but if role == "User"
    # then will default to checking for subscription based access
    for role in roles:
        if role.role == "Admin":
            for page in pages:
                existing_role_page = (
                    session.query(RolePages)
                    .filter_by(role_id=role.id, page_id=page.id)
                    .first()
                )
                if not existing_role_page:
                    new_role_page = RolePages(role_id=role.id, page_id=page.id)
                    session.add(new_role_page)
                    print(f"Added new RolePages entry: {role.role} - {page.page_name}")
        elif role.role == "Content_Creator":
            for page in pages:
                if "admin" not in page.page_name:
                    existing_role_page = (
                        session.query(RolePages)
                        .filter_by(role_id=role.id, page_id=page.id)
                        .first()
                    )
                    if not existing_role_page:
                        new_role_page = RolePages(role_id=role.id, page_id=page.id)
                        session.add(new_role_page)
                        print(
                            f"Added new RolePages entry: {role.role} - {page.page_name}"
                        )

    # Commit changes to the database
    session.commit()
    print("All new RolePages entries have been added to the database.")
    session.close()


def create_subscription_pages_entries():
    session = get_sessionlocal()

    # Get all subscription tiers and pages from the database
    tiers = session.query(SubscriptionTiers).all()
    pages = session.query(Pages).all()

    for tier in tiers:
        if tier.tier == "Free":
            for page in pages:
                # free does not have access to admin, basic, or premium prefix'd pages
                if (
                    "admin" not in page.page_name
                    and "basic" not in page.page_name
                    and "premium" not in page.page_name
                ):
                    existing_subscription_page = (
                        session.query(SubscriptionPages)
                        .filter_by(sub_tier_id=tier.id, page_id=page.id)
                        .first()
                    )
                    if not existing_subscription_page:
                        new_subscription_page = SubscriptionPages(
                            sub_tier_id=tier.id, page_id=page.id
                        )
                        session.add(new_subscription_page)
                        print(
                            f"Added new SubscriptionPages entry: {tier.tier} - {page.page_name}"
                        )

        elif tier.tier == "Basic":
            for page in pages:
                # basic does not have access to admin or premium prefix'd pages
                if "admin" not in page.page_name and "premium" not in page.page_name:
                    existing_subscription_page = (
                        session.query(SubscriptionPages)
                        .filter_by(sub_tier_id=tier.id, page_id=page.id)
                        .first()
                    )
                    if not existing_subscription_page:
                        new_subscription_page = SubscriptionPages(
                            sub_tier_id=tier.id, page_id=page.id
                        )
                        session.add(new_subscription_page)
                        print(
                            f"Added new SubscriptionPages entry: {tier.tier} - {page.page_name}"
                        )
        elif tier.tier == "Premium":
            for page in pages:
                # premium does not have access to admin prefix'd pages
                if "admin" not in page.page_name:
                    existing_subscription_page = (
                        session.query(SubscriptionPages)
                        .filter_by(sub_tier_id=tier.id, page_id=page.id)
                        .first()
                    )
                    if not existing_subscription_page:
                        new_subscription_page = SubscriptionPages(
                            sub_tier_id=tier.id, page_id=page.id
                        )
                        session.add(new_subscription_page)
                        print(
                            f"Added new SubscriptionPages entry: {tier.tier} - {page.page_name}"
                        )

    # Commit changes to the database
    session.commit()
    print("All new SubscriptionPages entries have been added to the database.")
    session.close()


if __name__ == "__main__":
    create_basic_roles()
    create_basic_subscription_tiers()
    initialize_page_entries()
    create_role_pages_entries()
    create_subscription_pages_entries()
