from convenience import *


def search_song_task(shove, query, user):
    """Search for a song with specific query and send to user"""

    set_greenlet_name("SearchSong")

    url = f"https://youtube.googleapis.com/youtube/v3/search"
    params = {  # url request parameters
        "key": YOUTUBE_API_KEY,
        "part": "snippet",
        "q": query,
        "maxResults": 50,
        "type": "video"
    }
    Log.trace(f"Sending YT API request")

    # https://stackoverflow.com/a/21966169/13216113 timeout keyword fixes slow request
    response = requests.get(url, params=params, timeout=1).json()
    Log.trace(f"YT API response: {response}")

    if not response:
        raise ExtractSongInformationFailed("No response from YT API")

    if not response["items"]:
        raise ExtractSongInformationFailed(f"No songs matching query query {query}")

    results = []
    for item in response["items"]:
        youtube_id = item["id"]["videoId"]
        name = item["snippet"]["title"]
        thumbnail = item["snippet"]["thumbnails"]["default"]
        channel = item["snippet"]["channelTitle"]
        # duration = isodate.parse_duration(item["contentDetails"]["duration"]).total_seconds()  # todo implement? requires additional API request for contentDetails
        results.append({
            "youtube_id": youtube_id,
            "name": name,
            "thumbnail": thumbnail,
            "channel": channel
        })

    shove.send_packet_to(user, "search_song", results)