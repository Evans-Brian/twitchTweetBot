
import tweepy
from helperFunctions.secretsManagement import get_secret

bearer_token = get_secret('twitter/bearer_token')
consumer_key = get_secret('twitter/consumer_key')
consumer_secret = get_secret('twitter/consumer_secret')

access_token = get_secret('twitter/access_token')
access_token_secret = get_secret('twitter/access_token_secret')


# print(bearer_token)
# val = [consumer_key, consumer_secret, bearer_token, access_token,
#        access_token_secret]

# for v in val:
#     print(v)


# def OAuth():
#     # try:
#     auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
#     auth.set_access_token(access_token, access_token_secret)

#     return auth

#     # except Exception as e:
#     #     print('except')
#     #     return None


# oauth = OAuth()
# api = tweepy.API(oauth, wait_on_rate_limit=True)

client = tweepy.Client(bearer_token, consumer_key,
                       consumer_secret, access_token, access_token_secret)
userId = client.get_user(username='ChiefBeef3OO')
print(userId)
# followed = client.follow_user(879434311)

# client.create_tweet(text='testing')
# api.create_friendship('ChiefBeef300')


# print('a tweet is posted')

# M7
# lm
# 10
# TL
