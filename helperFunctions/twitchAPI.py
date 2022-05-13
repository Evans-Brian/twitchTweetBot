import requests
import pandas as pd


def twitchAPIHeaders(client_id, client_secret):
    """Generates headers used to connect to Twitch API.

    Args:
        client_id (string): Twitch client ID.
        client_secret (string): Twitch client secret.

    Returns:
        headers(dict): Dict containing client ID and bearer token. Headers are used as an input for requesting data from the Twitch API
    """
    URL = "https://id.twitch.tv/oauth2/token"
    CLIENT_ID = client_id
    CLIENT_SECRET = client_secret
    GRANT_TYPE = "client_credentials"

    PARAMS = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": GRANT_TYPE
    }

    r1 = requests.post(url=URL, params=PARAMS)

    token = r1.json()["access_token"]

    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': 'Bearer ' + token
    }

    return headers


def getStreamData(headers, minViewers=50):
    """Pulls streaming data from Twitch API page by page and appends relevant data to a dataframe.

    Args:
        headers (string): Client ID and Bearer token used to connect to Twitch API.
        minViewers (int, optional): After a stream is read with below this number of viewers, API requests will stop.

    Returns:
        df (dataframe): Dataframe containing data on Twitch streams
    """
    URL = 'https://api.twitch.tv/helix/streams'
    columns = ['id', 'user_id', 'user_name', 'game_id',
               'game_name', 'viewer_count', 'thumbnail_url']
    currViewerCount = float('inf')
    cursor = None

    while currViewerCount >= minViewers:
        if not cursor:
            stream = requests.get(f'{URL}?first=100', headers=headers).json()
            df = pd.json_normalize(stream['data'])[columns]
        else:
            stream = requests.get(
                f'{URL}?first=100&after=' + cursor, headers=headers).json()
            newChunkDF = pd.json_normalize(stream['data'])[columns]
            df = df.append(newChunkDF)

        try:
            cursor = stream['pagination']['cursor']
        except:
            return df

        currViewerCount = 0
        i = 0
        while len(stream['data']) > 0 and i < 5:
            currViewerCount = max(
                currViewerCount, stream['data'].pop()['viewer_count'])
            i += 1

        return df


def descriptionTesting(headers, minViewers=50):
    # seems to require verified email in headers for authentication
    URL = 'https://api.twitch.tv/helix/users'
    columns = ['display_name', 'description']
    cursor = None
    stream = requests.get(f'{URL}?first=100', headers=headers).json()
