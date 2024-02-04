import os
import sys

# Append Ninjackalytics/ninjackalytics folder to sys path
ninjackalytics_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ninjackalytics_path)

from ninjackalytics.database.database import get_db_uri

import subprocess
import re


def dump_database():
    db_uri = get_db_uri()

    # Extract credentials from the URI
    pattern = r"mysql\+mysqldb:\/\/(?P<user>[^:]+):(?P<password>[^@]+)@(?P<host>[^:]+):(?P<port>[^\/]+)\/(?P<dbname>.+)"
    match = re.match(pattern, db_uri)
    if not match:
        raise ValueError("Could not parse database URI")

    credentials = match.groupdict()

    # Define the output path for your dump file
    output_file = f"{ninjackalytics_path}/{credentials['dbname']}_backup.sql"

    # Construct the mysqldump command
    dump_command = [
        "mysqldump",
        f"-u{credentials['user']}",
        f"-p{credentials['password']}",
        f"-h{credentials['host']}",
        f"--port={credentials['port']}",
        f"{credentials['dbname']}",
        f"> {output_file}",
    ]

    # Execute the command
    try:
        subprocess.run(" ".join(dump_command), shell=True, check=True)
        print(f"Database dump successful: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during database dump: {e}")


# Call the function to perform the dump
dump_database()
