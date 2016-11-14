# coding=utf-8
from __future__ import print_function

import numpy as np
import tensorflow as tf
import cPickle as pickle
import settings
import secret
from boto3.dynamodb.types import TypeDeserializer
import logging

from linebot import (
    LineBotApi, WebhookParser
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, StickerMessage,
    StickerSendMessage,
)

from linebot.exceptions import (
    LineBotApiError
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

t = TypeDeserializer()

# Line
channel_secret = secret.channel_secret
channel_access_token = secret.channel_access_token

line_bot_api = LineBotApi(channel_access_token)

def lambda_handler(event, context):
  logger.info('got event{}'.format(event))

  for record in event['Records']:
    # only handle INSERT event
    if not 'NewImage' in record['dynamodb']:
      continue

    # deserialize dynamodb record to python object
    seq_ids = [int(n) for n in t.deserialize(record['dynamodb']['NewImage']['seq_ids'])]
    seq_length = int(t.deserialize(record['dynamodb']['NewImage']['seq_length']))
    logger.info('record: {}'.format(record['dynamodb']['NewImage']))
    reply_token = t.deserialize(record['dynamodb']['NewImage']['reply_token']).encode('utf-8')
    logger.info('reply_token: {}'.format(reply_token))
    sticker_id = seq2sticker(seq_ids, seq_length)

    try:
      line_bot_api.reply_message(
        reply_token,
        StickerSendMessage(
          package_id=2,
          sticker_id=sticker_id
        )
      )
    except LineBotApiError as e:
      logger.error(e)
      pass

  return 'OK'


def model(graph):
  with graph.as_default():
    inputs = tf.placeholder(tf.int32, shape=[None, settings.MAX_SEQUENCE_LENGTH])
    sequence_lengths = tf.placeholder(tf.int32, shape=(None,))
    
    embedding = tf.get_variable("embedding", shape=[settings.VOCABULARY_SIZE, settings.EMBEDDING_SIZE], dtype=tf.float32)
    embed_inputs = tf.nn.embedding_lookup(embedding, inputs)

    # Use LSTM as cell
    cell = tf.nn.rnn_cell.BasicLSTMCell(settings.LSTM_SIZE, state_is_tuple=True)
    # cell = tf.nn.rnn_cell.MultiRNNCell([lstm_cell] * settings.NUM_LSTM_LAYERS, state_is_tuple=True)
    
    # Define RNN
    with tf.variable_scope("dynamic_rnn"):
      outputs, state = tf.nn.dynamic_rnn(cell,
                        embed_inputs,
                        dtype=tf.float32,
                        sequence_length=sequence_lengths
                        )

    # Classifier weights and biases.
    w = tf.Variable(tf.truncated_normal([settings.LSTM_SIZE, 47], -0.1, 0.1), name='w')
    b = tf.Variable(tf.zeros([47]), name='b')

    # Calculate logits and loss
    final_state = state.h
    logits = tf.nn.xw_plus_b(final_state, w, b)

    # Calculate predictions
    predictions = tf.nn.softmax(logits)
    saver = tf.train.Saver()
    return inputs, sequence_lengths, predictions, saver

def predict_sticker(predictions):
  with open('dicts/reverse_sticker_dictionary.pickle', 'rb') as handle:
    reverse_sticker_dict = pickle.load(handle)
  sticker_uniq_id = np.argmax(predictions[0])
  return reverse_sticker_dict[sticker_uniq_id]

def seq2sticker(seq_ids, seq_length):
  graph = tf.Graph()
  inputs, sequence_lengths, predictions, saver = model(graph)

  with tf.Session(graph=graph) as sess:
    saver.restore(sess, "model.ckpt")
    test_feed_dict = {inputs: [seq_ids], sequence_lengths: [seq_length]}
    test_predictions = predictions.eval(feed_dict=test_feed_dict)
    sticker_id = predict_sticker(test_predictions)
  return sticker_id

if __name__ == "__main__":
  lambda_handler(None, None)