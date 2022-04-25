import psycopg2 as pg2
import requests
from sqlalchemy import create_engine
from helperFunctions.twitchAPI import twitchAPIHeaders, getStreamData
from helperFunctions.updateTables import createBaseTables, updateBaseTables
from helperFunctions.secretsManagement import get_secret

client_id = get_secret('twitch/client_id')
client_secret = get_secret('twitch/client_secret')
password = get_secret('db/password')

# connect to Postgres SQL database and create engine
conn = pg2.connect(database = 'twitch', user = 'postgres', password = password)
cur = conn.cursor()
engine = create_engine(f'postgresql+psycopg2://postgres:{password}@localhost:5432/twitch')

headers = twitchAPIHeaders(client_id, client_secret)

stream_df = getStreamData(headers, 5000)

stream_df.to_sql('stream_data_staging', engine, if_exists = 'replace')

# createBaseTables(cur)
updateBaseTables(cur)

conn.commit()