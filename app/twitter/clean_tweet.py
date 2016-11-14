# coding=utf-8
from __future__ import print_function

import re

from app import db
from app.models.tweet import Tweet
from app.models.sequence import Sequence

with open('dicts/emoji_list.txt', 'r') as emoji_file:
  emojis= emoji_file.read().splitlines()

def clean_tweet(content):  
  # remove URLs, usernames, hashtags, RT (http://stackoverflow.com/a/13896637/4314737)
  content =re.sub(r"(?:\@|#|^RT|https?\://)[\w\-:：]*", "", content)
  # remove whitespaces
  return re.sub(r"\s+", "", content)

def remove_non_japanese_characters(sequence):
  non_jap_regex = u'[^一-龥ぁ-んァ-ン]' # not include symbols + hankaku
  return re.sub(non_jap_regex, "", sequence)

def create_sequence(line, tweet):
  if len(line) > 2:
    emojis_regex = '(' + '|'.join(map(re.escape, emojis)) + ')'
    sequences = iter(re.split(emojis_regex, line))
    for sequence, emoji in zip(sequences, sequences):
      sequence = sequence.strip()
      # sequence = remove_non_japanese_characters(sequence)
      if len(sequence) > 2:
        print(sequence + ' -> ' + emoji)
        seq = Sequence(sequence.decode('utf-8'), emoji.decode('utf-8'), tweet)
        db.session.add(seq)
        db.session.commit()

# last tweet id = 226832
for tweet in Tweet.query.offset(226832).all():
  print(tweet.id)
  lines = tweet.content.encode('utf-8').splitlines()
  for line in lines:
    line = clean_tweet(line)
    create_sequence(line, tweet)
    

  print("-----------------")
