import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Define the URL of the page containing the .gif files
url = "https://play.pokemonshowdown.com/sprites/ani/"

# Send a GET request to the URL and get the page content
response = requests.get(url)
content = response.content

# Parse the page content using beautifulsoup4
soup = BeautifulSoup(content, "html.parser")

# Find all the a tags that contain .gif in their href attribute
gif_links = soup.find_all("a", href=lambda href: href and href.endswith(".gif"))

# For each a tag, extract the href attribute value and download the file using requests
for link in gif_links:
    href = link["href"]
    full_url = urljoin(url, href)
    file_name = href.split("/")[-1]
    file_path = os.path.join(os.getcwd(), "assets", "showdown_sprites", file_name)
    with open(file_path, "wb") as f:
        f.write(requests.get(full_url).content)
