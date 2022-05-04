import psycopg2 as pg2
from sqlalchemy import create_engine
from helperFunctions.twitchAPI import twitchAPIHeaders, getStreamData, descriptionTesting
from helperFunctions.updateTables import updateStagingTables, createStagingTables, updateYesterdayTables
from helperFunctions.secretsManagement import get_secret
from datetime import datetime, time


client_id = get_secret('twitch/client_id')
client_secret = get_secret('twitch/client_secret')
password = get_secret('db/password')

# connect to Postgres SQL database and create engine
conn = pg2.connect(database='twitch', user='postgres', password=password)
cur = conn.cursor()
engine = create_engine(
    f'postgresql+psycopg2://postgres:{password}@localhost:5432/twitch')

headers = twitchAPIHeaders(client_id, client_secret)

stream_df = getStreamData(headers, 200)

stream_df.to_sql('stream_data_staging', engine, if_exists='replace')


now = datetime.utcnow().time()
# viewership typically bottoms out around 8AM UTC
# Therefore, we will consider our day starting at 8AM UTC
if time(7, 55) <= now <= time(8, 5):
    createStagingTables(cur)
    updateYesterdayTables(cur)
else:
    updateStagingTables(cur)

conn.commit()
