import os
import psycopg2 as pg2
from sqlalchemy import create_engine
from helperFunctions.twitterAPI import respondToTweet, createClient

client = createClient()

password = get_secret('db/password')

conn = pg2.connect(database='twitch', user='postgres', password=password)

os.chdir("/home/ec2-user/twitterBot")
respondToTweet(conn, client)
