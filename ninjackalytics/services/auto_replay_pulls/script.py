import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_battle_urls_selenium(format_string, pages=25):
    # Set Chrome options to run in headless mode
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)

    urls = []
    for page in range(1, pages + 1):
        full_url = f"https://replay.pokemonshowdown.com/?format={format_string}&page={page}&sort=rating"
        urls.append(full_url)

    battle_urls = []
    for url in urls:
        # Go to the URL
        driver.get(url)

        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )

        # Find all <a> tags in the HTML that contain a href attribute
        a_tags = driver.find_elements(By.TAG_NAME, "a")

        # Filter the <a> tags to only include those where the href attribute matches the form of the battle URLs
        battle_urls += [
            tag.get_attribute("href")
            for tag in a_tags
            if re.match(
                rf"https://replay.pokemonshowdown.com/{format_string}-\d+",
                tag.get_attribute("href"),
            )
        ]

    # Close the browser
    driver.quit()

    return battle_urls


def get_replay_urls(battle_format: str, pages: int = 24):
    # Define the base URL for the replay search API
    base_url = "https://replay.pokemonshowdown.com/search.json"

    # Define the search parameters for the API
    params = {"format": battle_format, "page": 1}

    success = False
    tries = 0
    while not success:
        try:
            tries += 1
            # Send a GET request to the API with the search parameters
            response = requests.get(base_url, params=params)
            replays = response.json()
            success = True
        except:
            if tries > 5:
                raise Exception("Too many tries")

    # # Send a GET request to the API with the search parameters
    # response = requests.get(base_url, params=params)

    # # Parse the JSON response from the API to extract the replay URLs
    # replays = response.json()
    replay_urls = [
        f"https://replay.pokemonshowdown.com/{replay['id']}" for replay in replays
    ]

    # Repeat steps 3-5 for each page of results until there are no more results or until the max pages are hit
    while len(replays) == 51 and params["page"] <= pages:
        params["page"] += 1
        success = False
        tries = 0
        try:
            tries += 1
            # Send a GET request to the API with the search parameters
            response = requests.get(base_url, params=params)
            replays = response.json()
            success = True
        except:
            if tries > 5:
                raise Exception("Too many tries")

        replay_urls += [
            f"https://replay.pokemonshowdown.com/{replay['id']}" for replay in replays
        ]

    # Save the replay URLs to a file or process them in some other way
    return replay_urls
