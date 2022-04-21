import config
import tweepy

def api_v1_oauth1():
    """ V1.1 authentication - OAuth 1.0a User Context"""
    auth = tweepy.OAuth1UserHandler(
        consumer_key=config.API_KEY,
        consumer_secret=config.API_SECRET,
        access_token=config.ACCESS_TOKEN,
        access_token_secret=config.ACCESS_TOKEN_SECRET
        )
    api = tweepy.API(auth)
    return api

def api_v2_oauth1():
    """ V2 authentication - OAuth 1.0a User Context"""
    client = tweepy.Client(
        consumer_key=config.API_KEY,
        consumer_secret=config.API_SECRET,
        access_token=config.ACCESS_TOKEN,
        access_token_secret=config.ACCESS_TOKEN_SECRET
        )
    return client

def api_v2_oauth2():
    """ API V2 - OAuth 2.0 Bearer Token (App-Only) """
    client = tweepy.Client(config.BEARER_TOKEN)
    return client