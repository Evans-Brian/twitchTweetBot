import psycopg2 as pg2
from sqlalchemy import create_engine
from helperFunctions.twitterAPI import tweetTopGames, tweetTopStreamers, respondToTweet, tweetRandomGame, createClient
from helperFunctions.twitchAPI import twitchAPIHeaders, getStreamData
from helperFunctions.updateTables import updateStagingTables, createStagingTables, updateYesterdayTables
from helperFunctions.secretsManagement import get_secret
from datetime import datetime, time
import os

os.chdir("/home/ec2-user/twitterBot")

# logging for exceptions
logf = open("storage/myapp.log", "a")

# time used to trigger specific actions, like updating yesterdays tables and sending tweets
now = datetime.utcnow().time()

# credentials
client_id = get_secret('twitch/client_id')
client_secret = get_secret('twitch/client_secret')
password = get_secret('db/password')

# connect to Postgres SQL database and create engine
conn = pg2.connect(database='twitch', user='postgres', password=password)
cur = conn.cursor()
engine = create_engine(
    f'postgresql+psycopg2://postgres:{password}@localhost:5432/twitch')

# headers to connect to Twitch API
headers = twitchAPIHeaders(client_id, client_secret)

# client to connect to Twitter API
client = createClient()

# pulls data from the Twitch API for all streamers with over n viewers
stream_df = getStreamData(headers, 50)
stream_df.to_sql('stream_data_staging', engine, if_exists='replace')


logf.write(f'{now} 1\n')

# viewership typically bottoms out around 8AM UTC
# Therefore, we will consider our day starting at 8AM UTC

# if time is between 7:55 AM UTC and 8:05 AM UTC, delete and replace tables for yesterday's data
# otherwise update the staging tables
if time(7, 55) <= now <= time(8, 5):
    createStagingTables(cur)
    updateYesterdayTables(cur)
else:
    updateStagingTables(cur)
logf.write(f'{now} 2\n')

# respond to any tagged tweets that haven't already been read
respondToTweet(conn, client)

logf.write(f'{now} 3\n')

# if time is near 2PM UTC, tweet metrics for top games, streamers, and a random game
if time(14, 55) <= now <= time(15, 5):

    try:
        tweetTopGames(conn, client)
    except Exception as e:
        logf.write(f'tweetTopGames: {now}  {str(e)}\n')

    try:
        tweetTopStreamers(conn, client)
    except Exception as e:
        logf.write(f'tweetTopStreamers: {now}  {str(e)}\n')

    try:
        tweetRandomGame(conn, client)
    except Exception as e:
        logf.write(f'tweetRandomGame: {now}  {str(e)}\n')

logf.write(f'{now} 4\n')
conn.commit()
