import os
import sys

# Append Ninjackalytics/ninjackalytics folder to sys path
ninjackalytics_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ninjackalytics_path)

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm


def get_showdown_mon_images():
    # Define the URLs of the pages containing the .gif files
    urls = [
        "https://play.pokemonshowdown.com/sprites/ani/",
        "https://play.pokemonshowdown.com/sprites/dex/",
    ]

    # Define a list to keep track of the downloaded files
    downloaded_files = []

    # Loop through each URL
    for url in urls:
        # Send a GET request to the URL and get the page content
        response = requests.get(url)
        content = response.content

        # Parse the page content using beautifulsoup4
        soup = BeautifulSoup(content, "html.parser")

        # Find all the a tags that contain .gif or .png in their href attribute
        img_links = soup.find_all(
            "a",
            href=lambda href: href and href.endswith(".gif") or href.endswith(".png"),
        )

        # For each a tag, extract the href attribute value and download the file using requests
        for link in tqdm(img_links):
            href = link["href"]
            full_url = urljoin(url, href)
            file_name = href.split("/")[-1]
            file_path = os.path.join(
                ninjackalytics_path, "assets", "showdown_sprites", file_name
            )
            if file_name not in downloaded_files:
                with open(file_path, "wb") as f:
                    f.write(requests.get(full_url).content)
                downloaded_files.append(file_name)


if __name__ == "__main__":
    get_showdown_mon_images()
