import os
import sys

current_script_path = os.path.abspath(__file__)
parent_directory = os.path.dirname(os.path.dirname(current_script_path))
sys.path.append(parent_directory)

from ninjackalytics.database.database import get_sessionlocal
from ninjackalytics.database.models import Pages


def create_pages_entries():
    pages_directory = os.path.join(parent_directory, "pages")

    # Initialize database session
    session = get_sessionlocal()

    # List all Python files in the 'pages' directory
    for file_name in os.listdir(pages_directory):
        if file_name.endswith(".py") and file_name != "__init__.py":
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


if __name__ == "__main__":
    create_pages_entries()
