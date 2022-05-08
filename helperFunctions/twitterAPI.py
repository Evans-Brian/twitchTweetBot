import tweepy
import random
from bisect import bisect_left
import pandas as pd
from helperFunctions.secretsManagement import get_secret
import psycopg2 as pg2

# password = get_secret('db/password')

# connect to Postgres SQL database and create engine
# conn = pg2.connect(database='twitch', user='postgres', password=password)


def createClient():
    """Creates a new client to connect to Twitter API.

    Returns:
        client (obj): Client connecting to Twitter API v2.
    """

    bearer_token = get_secret('twitter/bearer_token')
    consumer_key = get_secret('twitter/consumer_key')
    consumer_secret = get_secret('twitter/consumer_secret')
    access_token = get_secret('twitter/access_token')
    access_token_secret = get_secret('twitter/access_token_secret')
    client = tweepy.Client(bearer_token, consumer_key,
                           consumer_secret, access_token, access_token_secret)
    return client


def tweetTopGames(conn, client, count=5):
    """Tweets the top {count} games in order of watch time.

    Args:
        conn (connection): Connection to PSQL database
        client (obj): Client connecting to Twitter API v2.
        count (int, optional): The number of games that will be returned. Defaults to 5.
    """
    topGamesQuery = '''select game_name, watch_time
                from game_watch_time_table
                order by watch_time desc
                limit 5
                '''
    df = pd.read_sql_query(topGamesQuery, con=conn)

    payload = 'The most watched games on Twitch yesterday were:'

    for index, row in df.iterrows():
        name = row['game_name']
        watch_time = format(row['watch_time'], ",").replace('.0', '')
        add = f'\n{str(index + 1)}. {name}: {watch_time} hours'
        payload += add
    client.create_tweet(text=payload)


def tweetTopStreamers(conn, client, count=5):
    """Tweets the top {count} streamers in order of watch time.

    Args:
        conn (connection): Connection to PSQL database
        client (obj): Client connecting to Twitter API v2.
        count (int, optional): The number of streaners that will be returned. Defaults to 5.
    """
    topStreamersQuery = '''select user_name, watch_time
                from streamer_watch_time_table
                order by watch_time desc
                limit 5
                '''
    df = pd.read_sql_query(topStreamersQuery, con=conn)

    payload = 'The most watched streamers on Twitch yesterday were:'

    for index, row in df.iterrows():
        name = row['user_name']
        watch_time = format(row['watch_time'], ",").replace('.0', '')
        add = f'\n{str(index + 1)}. {name}: {watch_time} hours'
        payload += add
    client.create_tweet(text=payload)


def respondToTweet(conn, client):
    """Reads all tweets tagged @TwitchWatchTime. If the tweet text is a game or a streamer,
    respond to the tweet with the top 5 streamers for that game or the top 5 games for that streamer,
    ordered by watch time.  Calls _queryRequest, _sendGameRespone, _sendStreamerRespone.

    Args:
        conn (connection): Connection to PSQL database
        client (obj): Client connecting to Twitter API v2.
    """
    response = client.search_recent_tweets('@TwitchWatchTime', max_results=100)
    oldTweets = []

    with open('storage/tweets_read.txt', 'r') as filehandle:
        for line in filehandle:
            # remove linebreak which is the last character of the string
            currentID = line[:-1]

            # add item to the list
            oldTweets.append(int(currentID))

    with open('storage/tweets_read.txt', 'a') as filehandle:
        for tweet in response.data:
            hashmap = dict(tweet)

            # if tweet ID exists in storage/tweets_read.txt, skip
            if hashmap['id'] not in oldTweets:
                text, game_df, streamer_df = _queryRequest(
                    hashmap['text'], conn)

                if game_df.shape[0] > 0:
                    _sendGameRespone(client, text, game_df, hashmap['id'])

                if streamer_df.shape[0] > 0:
                    _sendStreamerRespone(
                        client, text, streamer_df, hashmap['id'])

                if game_df.shape[0] == 0 and streamer_df.shape[0] == 0:
                    payload = f'There were no active games or streamers yesterday with name {text}'
                    client.create_tweet(
                        text=payload, in_reply_to_tweet_id=hashmap['id'])

                # writes tweet IDs that have been read to storage/tweets_read.txt
                # this will prevent us from responding to the same tweet multiple times
                filehandle.write('%s\n' % hashmap['id'])


def _queryRequest(text, conn):
    """Queries the watch_time table for games and streamers matching the given text.

    Args:
        text (string): text to query against game_name and user_name.
        conn (connection): Connection to PSQL database.

    Returns:
        text (string): Returns input text with '@TwitchWatchTime' and leading/trailing spaces removed.
        game_df (dataframe): Top 5 streamers for games with name matching input text.
        streamer_df (dataframe): Top 5 games for streamers with name matching input text.
    """
    text = text.replace('@TwitchWatchTime', '')
    text = text.strip()

    gameQuery = f'''select user_name, watch_time
            from watch_time_table
            where lower(game_name) = lower(\'{text}\')
            order by watch_time desc
            limit 5;
            '''

    streamerQuery = f'''select game_name, watch_time
            from watch_time_table
            where lower(user_name) = lower(\'{text}\')
            order by watch_time desc
            limit 5;
            '''

    game_df = pd.read_sql_query(gameQuery, con=conn)
    streamer_df = pd.read_sql_query(streamerQuery, con=conn)
    return text, game_df, streamer_df


def _sendGameRespone(client, text, df, id):
    """Responds to tweet with id = id with the top 5 streamers if there is a game with name equal to input text.

    Args:
        text (string): Game name.
        client (obj): Client connecting to Twitter API v2.
        df (dataframe): Dataframe containing the top 5 streamers for a game and their associated watch time.
        id (int): id of tweet to respond to.
    """
    payload = f'The most watched {text} streamers yesterday were:'

    for index, row in df.iterrows():
        name = row['user_name']
        watch_time = format(row['watch_time'], ",").replace('.0', '')
        add = f'\n{str(index + 1)}. {name}: {watch_time} hours'
        payload += add

    client.create_tweet(text=payload, in_reply_to_tweet_id=id)


def _sendStreamerRespone(client, text, df, id):
    """Responds to tweet with id = id with the top 5 games streamed if there is a streamer with name equal to input text.

    Args:
        text (string): Streamer name.
        client (obj): Client connecting to Twitter API v2.
        df (dataframe): Dataframe containing the top 5 games for a streamer and their associated watch time.
        id (int): id of tweet to respond to.
    """
    payload = f'{text} streamed the following games yesterday'

    for index, row in df.iterrows():
        name = row['game_name']
        watch_time = format(row['watch_time'], ",").replace('.0', '')
        add = f'\n{str(index + 1)}. {name}: {watch_time} hours'
        payload += add

    client.create_tweet(text=payload, in_reply_to_tweet_id=id)


def tweetRandomGame(conn, client, count=5):
    """Tweeets the top 5 streamers and their watch times for a random game. The random game chosen is weighted 
    based on total watch time and is chosen from only the top 1000 most watched games.

    Args:
        conn (connection): Connection to PSQL database
        count (int, optional): The number of streaners that will be returned. Defaults to 5.
    """

    gameWatchTimeQuery = '''
                    select game_name, watch_time
                    from game_watch_time_table
                    order by watch_time desc
                    limit 1000
                    '''
    df = pd.read_sql_query(gameWatchTimeQuery, con=conn)

    weights = []
    total = 0

    for index, row in df.iterrows():
        total += row['watch_time']
        weights.append((total, row['game_name']))

    rand = random.randint(0, total)
    _, game = weights[bisect_left(weights, (rand, None))]

    randomGameTopStreams = f'''
                    select user_name, watch_time
                    from watch_time_table
                    where game_name = \'{game}\'
                    order by watch_time desc
                    limit 5
                    '''

    df = pd.read_sql_query(randomGameTopStreams, con=conn)

    payload = f'Today\'s random game is {game}. The top {count} streamers yesterday for {game} are:'

    for index, row in df.iterrows():
        name = row['user_name']
        watch_time = format(row['watch_time'], ",").replace('.0', '')
        add = f'\n{str(index + 1)}. {name}: {watch_time} hours'
        payload += add
    client.create_tweet(text=payload)
