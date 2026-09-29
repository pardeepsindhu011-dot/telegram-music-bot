import requests


def search_music(query):

    url = "https://itunes.apple.com/search"

    parameters = {
        "term": query,
        "media": "music",
        "limit": 5
    }

    response = requests.get(
        url,
        params=parameters,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    results = []

    for item in data.get("results", []):

        results.append({
            "song": item.get("trackName"),
            "artist": item.get("artistName"),
            "album": item.get("collectionName"),
            "link": item.get("trackViewUrl")
        })

    return results
