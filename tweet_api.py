import os
import tweepy
import sentry_sdk
from sentry_sdk import configure_scope
from tweepy.error import TweepError


class TweetApi(object):
    def __init__(self, consumer_key=None, consumer_secret=None, access_token=None, access_token_secret=None):
        self.consumer_key = consumer_key or os.environ['CONS_KEY']
        self.consumer_secret = consumer_secret or os.environ['CONS_SEC']
        self.access_token = access_token or os.environ['ACC_TOK']
        self.access_token_secret = access_token_secret or os.environ['ACC_TOK_SECR']

    def with_auth(self):
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(auth)
        return self

    def tweet(self, quote):
        try:
            self.api.update_status(quote)
            print("Successfully tweeted: {}".format(quote))
        except TweepError as e:
            with configure_scope() as scope:
                scope.set_extra("Message", e.response.text)
                scope.set_extra("Tweet", quote)
                sentry_sdk.capture_exception(e)
