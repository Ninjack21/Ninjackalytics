import requests


def get_replay_urls(battle_format: str):
    # Define the base URL for the replay search API
    base_url = "https://replay.pokemonshowdown.com/search.json"

    # Define the search parameters for the API
    params = {"format": battle_format, "page": 1}

    # Send a GET request to the API with the search parameters
    response = requests.get(base_url, params=params)

    # Parse the JSON response from the API to extract the replay URLs
    replays = response.json()
    replay_urls = [
        f"https://replay.pokemonshowdown.com/{replay['id']}" for replay in replays
    ]

    # Repeat steps 3-5 for each page of results until there are no more results or until the max pages are hit
    while len(replays) == 51 and params["page"] <= 24:
        params["page"] += 1
        response = requests.get(base_url, params=params)
        replays = response.json()
        replay_urls += [
            f"https://replay.pokemonshowdown.com/{replay['id']}" for replay in replays
        ]

    # Save the replay URLs to a file or process them in some other way
    return replay_urls
