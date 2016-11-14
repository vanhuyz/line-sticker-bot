# coding=utf-8
from __future__ import print_function

import os
import ctypes
import boto3
import cPickle as pickle
import logging
import json
import secret

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, StickerMessage,
    StickerSendMessage,
)

libdir = os.path.join(os.getcwd(), 'local', 'lib')
libmecab = ctypes.cdll.LoadLibrary(os.path.join(libdir, 'libmecab.so'))

import MeCab

# MeCab
dicdir = os.path.join(os.getcwd(), 'local', 'lib', 'mecab', 'dic', 'ipadic')
rcfile = os.path.join(os.getcwd(), 'local', 'etc', 'mecabrc')
mecab = MeCab.Tagger("-d{} -r{} -F%f[7]-%f[0]\s -U<UNK>\s -E\s".format(dicdir, rcfile))

# DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Linebot')

# Line
channel_secret = secret.channel_secret
channel_access_token = secret.channel_access_token

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

def lambda_handler(event, context):
  logger.info('got event{}'.format(event))

  # FIXME: should handle exceptions
  signature = event['headers']['X-Line-Signature']
  body = event['body']
  handler.handle(body, signature)
  return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
  text = event.message.text.encode('utf-8')
  seq_ids, seq_length = seq2id(text)
  table.put_item(
    Item={
      'id': event.message.id.encode('utf-8'),
      'user_id': event.source.user_id.encode('utf-8'),
      'text':  text,
      'seq_ids': seq_ids,
      'seq_length': seq_length,
      'reply_token': event.reply_token.encode('utf-8'),
      'timestamp': event.timestamp
    }
  )


def seq2id(content):
  with open('dicts/dictionary.pickle', 'rb') as handle:
    dictionary = pickle.load(handle)
  input_words = mecab.parse(content).split()
  input_ids = list(map(lambda word: dictionary.get(word,1), input_words))
  input_length = len(input_ids)
  if input_length > 10:
    input_length = 10
    input_ids = input_ids[-10:]
  else:
    input_ids = input_ids + [0]*(10 - input_length)
  return input_ids, input_length

if __name__ == "__main__":
  lambda_handler(None, None)

