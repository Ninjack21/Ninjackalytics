import requests

# gen9ou full replay list spanned ~ 2 days. 1275th battle was from 2 days prior.


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
