
from cgi import test
from secrets import randbits
import tweepy
import random
from bisect import bisect_left
from helperFunctions.secretsManagement import get_secret
import pandas as pd
import psycopg2 as pg2
from sqlalchemy import create_engine


password = get_secret('db/password')

# connect to Postgres SQL database and create engine
cur = pg2.connect(database='twitch', user='postgres', password=password)

engine = create_engine(
    f'postgresql+psycopg2://postgres:{password}@localhost:5432/twitch')


def createClient():
    bearer_token = get_secret('twitter/bearer_token')
    consumer_key = get_secret('twitter/consumer_key')
    consumer_secret = get_secret('twitter/consumer_secret')
    access_token = get_secret('twitter/access_token')
    access_token_secret = get_secret('twitter/access_token_secret')
    client = tweepy.Client(bearer_token, consumer_key,
                           consumer_secret, access_token, access_token_secret)
    return client


def tweetTopGames(cur, count=5):
    client = createClient()
    topGamesQuery = '''select game_name, watch_time_pretty
                from game_watch_time_table
                order by watch_time desc
                limit 5
                '''
    df = pd.read_sql_query(topGamesQuery, con=cur)

    payload = 'The most watched games on Twitch yesterday were:'

    for index, row in df.iterrows():
        name = row['game_name']
        watch_time = row['watch_time_pretty'].replace('.', '')
        add = f'\n{str(index + 1)}. {name}: {watch_time} hours'
        payload += add
    print(payload)
    client.create_tweet(text=payload)


def tweetTopStreamers(cur, count=5):
    client = createClient()
    topStreamersQuery = '''select user_name, watch_time_pretty
                from streamer_watch_time_table
                order by watch_time desc
                limit 5
                '''
    df = pd.read_sql_query(topStreamersQuery, con=cur)

    payload = 'The most watched streamers on Twitch yesterday were:'

    for index, row in df.iterrows():
        name = row['user_name']
        watch_time = row['watch_time_pretty'].replace('.', '')
        add = f'\n{str(index + 1)}. {name}: {watch_time} hours'
        payload += add
    client.create_tweet(text=payload)


def respondToTweet(cur):
    client = createClient()
    response = client.search_recent_tweets('@TwitchWatchTime', max_results=100)
    oldTweets = []
    print(response)

    # with open('storage/tweets_read.txt', 'r') as filehandle:
    #     for line in filehandle:
    #         # remove linebreak which is the last character of the string
    #         currentID = line[:-1]

    #         # add item to the list
    #         oldTweets.append(int(currentID))

    with open('storage/tweets_read.txt', 'a') as filehandle:
        for tweet in response.data:
            hashmap = dict(tweet)
            print(hashmap)
            print(hashmap['id'])
            print(hashmap['text'])
            if hashmap['id'] not in oldTweets:
                text, game_df, streamer_df = _queryRequest(
                    hashmap['text'], cur)

                if game_df.shape[0] > 0:
                    _sendGameRespone(client, text, game_df, hashmap['id'])

                if streamer_df.shape[0] > 0:
                    _sendStreamerRespone(
                        client, text, streamer_df, hashmap['id'])

                if game_df.shape[0] == 0 and streamer_df.shape[0] == 0:
                    payload = f'There were no active games or streamers yesterday with name {text}'
                    client.create_tweet(
                        text=payload, in_reply_to_tweet_id=hashmap['id'])

                filehandle.write('%s\n' % hashmap['id'])


def _queryRequest(text, cur):
    text = text.replace('@TwitchWatchTime', '')
    text = text.strip()

    gameQuery = f'''select user_name, watch_time_pretty
            from watch_time_table
            where lower(game_name) = lower(\'{text}\')
            order by watch_time desc
            limit 5;
            '''

    streamerQuery = f'''select game_name, watch_time_pretty
            from watch_time_table
            where lower(user_name) = lower(\'{text}\')
            order by watch_time desc
            limit 5;
            '''

    game_df = pd.read_sql_query(gameQuery, con=cur)
    streamer_df = pd.read_sql_query(streamerQuery, con=cur)
    return text, game_df, streamer_df


def _sendGameRespone(client, text, df, id):

    payload = f'The most watched {text} streamers yesterday were:'

    for index, row in df.iterrows():
        name = row['user_name']
        watch_time = row['watch_time_pretty'].replace('.', '')
        add = f'\n{str(index + 1)}. {name}: {watch_time} hours'
        payload += add

    client.create_tweet(text=payload, in_reply_to_tweet_id=id)


def _sendStreamerRespone(client, text, df, id):

    payload = f'{text} streamed the following games yesterday'

    for index, row in df.iterrows():
        name = row['game_name']
        watch_time = row['watch_time_pretty'].replace('.', '')
        add = f'\n{str(index + 1)}. {name}: {watch_time} hours'
        payload += add

    client.create_tweet(text=payload, in_reply_to_tweet_id=id)


tweetTopStreamers(cur)
# if exact tweet text is in storage file, skip. Otherwise respond
# call tweetTopStreamers and tweetTopGames
# query should be either a game or streamer name. If it's a game and streamer name, respond with both

# overwrite storage file

# def tweetRandomGame(cur, count=5):
#     client = createClient()
#     gameWatchTimeQuery = '''select game_name, watch_time
#                 from streamer_watch_time
#                 order by game_watch_time desc
#                 limit 1000
#                 '''
#     df = pd.read_sql_query(gameWatchTimeQuery, con=cur)

#     weights = []
#     total = 0

#     for index, row in df.iterrows():
#         total += row['watch_time_pretty'].replace('.', '')
#         weights.append((total, row['game_name']))

#     rand = random.randint(0, total)
#     game = bisect_left(weights, rand)


# tweetTopGames(cur)
# oauth = OAuth()
# api = tweepy.API(oauth, wait_on_rate_limit=True)
# client = tweepy.Client(bearer_token, consumer_key,
#                        consumer_secret, access_token, access_token_secret)
# userId = client.get_user(username='ChiefBeef3OO')
# print(userId)
# # followed = client.follow_user(879434311)

# client.create_tweet(text='testing')
# api.create_friendship('ChiefBeef300')


# print('a tweet is posted')

# M7
# lm
# 10
# TL
