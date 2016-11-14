# -*- coding: utf-8 -*-

import cPickle as pickle
import MeCab
import numpy as np
import settings

#mecab = MeCab.Tagger("-F%f[7]-%f[0]\s -U<UNK>\s -E\s") #yomi-hinshi
mecab = MeCab.Tagger("-Owakati")

""" Load dictionaries from pickles
"""
def load_dictionary():
  with open('dicts/dictionary.pickle', 'rb') as handle:
    dictionary = pickle.load(handle)
  with open('dicts/reverse_dictionary.pickle', 'rb') as handle:
    reverse_dictionary = pickle.load(handle)
  return dictionary, reverse_dictionary

def load_emoji_sticker_dictionary():
  with open('dicts/emoji_sticker_dictionary.pickle', 'rb') as handle:
    emoji_sticker_dictionary = pickle.load(handle)
  return emoji_sticker_dictionary

def load_sticker_dictionary():
  with open('dicts/sticker_dictionary.pickle', 'rb') as handle:
    sticker_dict = pickle.load(handle)
  return sticker_dict

def load_reverse_sticker_dictionary():
  with open('dicts/reverse_sticker_dictionary.pickle', 'rb') as handle:
    reverse_sticker_dict = pickle.load(handle)
  return reverse_sticker_dict

""" Let's load!
"""
def load_dictionaries():
  dictionary, reverse_dictionary = load_dictionary()
  emoji_sticker_dictionary = load_emoji_sticker_dictionary()
  sticker_dictionary = load_sticker_dictionary()
  reverse_sticker_dictionary = load_reverse_sticker_dictionary()
  return dictionary, reverse_dictionary, emoji_sticker_dictionary, sticker_dictionary, reverse_sticker_dictionary

dictionary, reverse_dictionary, emoji_sticker_dictionary, sticker_dictionary, reverse_sticker_dictionary = load_dictionaries()

def sticker_size():
  return len(sticker_dictionary)

""" Some useful convertion functions
"""
def uniqid2sticker(id):
  """ Convert unique_id to Line's sticker_id
  """
  return reverse_sticker_dictionary[id]

def emoji2onehot(emoji):
  """ Convert emoji to sticker, then convert sticker to onehot
  """
  onehot = np.zeros(len(sticker_dictionary))
  onehot[sticker_dictionary[emoji_sticker_dictionary[emoji]]] = 1.0
  return onehot

def seq2id(content):
  """ Convert a sequence's content to a list of word IDs, and sequence_length.
  If sequence_length < MAX_SEQUENCE_LENGTH, padding with <PAD> symbol (word_id = 0)
  If sequence_length > MAX_SEQUENCE_LENGTH, convert only the last MAX_SEQUENCE_LENGTH words of sequence
  Example:
    seq2id('誘ってくれてありがとう') -> ([2877, 1, 73, 1, 25, 1, 1, 1, 1, 1], 5)
    utils.seq2id('これはとても長い文章です。どうぞよろしくお願いします！')　-> ([147, 13, 634, 1815, 5753, 10, 41, 552, 171, 7], 10)
  """
  input_words = mecab.parse(content).split()
  input_ids = list(map(lambda word: dictionary.get(word,settings.UNK_ID), input_words))
  input_length = len(input_ids)
  if input_length > settings.MAX_SEQUENCE_LENGTH:
    input_length = settings.MAX_SEQUENCE_LENGTH
    input_ids = input_ids[-settings.MAX_SEQUENCE_LENGTH:]
  else:
    input_ids = input_ids + [settings.PAD_ID]*(settings.MAX_SEQUENCE_LENGTH - input_length)
  return input_ids, input_length

def get_onehot_label(sequence):
  """ Use for training
  """
  return emoji2onehot(sequence.emoji.encode('utf-8'))


  return emoji_sticker_dictionary[sequence.emoji.encode('utf-8')]

def onehot2sticker(predictions):
  return uniqid2sticker(np.argmax(predictions[0]))
