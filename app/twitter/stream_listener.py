from __future__ import print_function

import os
import tweepy
from app import db
from app.models.tweet import Tweet

class TwitterStreamListener(tweepy.StreamListener):
  def on_status(self, status):
    print(status.text)
    tweet = Tweet(status.text)
    db.session.add(tweet)
    db.session.commit()

  def on_error(self, status_code):
    print('Got an error with status code: ' + str(status_code))
    return True

consumer_token = os.environ['CONSUMER_TOKEN']
consumer_secret = os.environ['CONSUMER_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_secret = os.environ['ACCESS_SECRET']

auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)

myStreamListener = TwitterStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)

with open('dicts/emoji_list.txt', 'r') as emoji_file:
  emojis= emoji_file.read().decode('utf-8').splitlines()

myStream.filter(languages = ["ja"], track=emojis, async=True)
