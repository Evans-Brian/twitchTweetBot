import requests
import pandas as pd

def twitchAPIHeaders(client_id, client_secret):
    URL = "https://id.twitch.tv/oauth2/token"
    CLIENT_ID = client_id
    CLIENT_SECRET = client_secret
    GRANT_TYPE = "client_credentials"

    PARAMS = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": GRANT_TYPE
    }

    r1 = requests.post(url = URL, params = PARAMS)

    token = r1.json()["access_token"]

    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': 'Bearer ' + token
    }
    
    return headers

def getStreamData(headers, minViewers = 50):
    URL = 'https://api.twitch.tv/helix/streams'
    columns = ['id', 'user_id', 'user_name', 'game_id', 'game_name', 'viewer_count', 'thumbnail_url']
    currViewerCount = float('inf')
    cursor = None
    
    while currViewerCount >= minViewers:
        if not cursor:
            stream = requests.get(f'{URL}?first=100', headers=headers).json()
            df = pd.json_normalize(stream['data'])[columns]
        else:
            stream = requests.get(f'{URL}?first=100&after=' + cursor, headers=headers).json()
            newChunkDF = pd.json_normalize(stream['data'])[columns]
            df = df.append(newChunkDF)
        
        # continue until 
        try: 
            cursor = stream['pagination']['cursor']
        except: 
            return df
        
        currViewerCount = 0
        i = 0
        while len(stream['data']) > 0 and i < 5:
            currViewerCount = max(currViewerCount, stream['data'].pop()['viewer_count'])
            i += 1

    return df