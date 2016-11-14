from __future__ import print_function

import collections
import MeCab
import cPickle as pickle

import app.common.settings as settings
import app.common.utils as utils
from app.models.sequence import Sequence


def get_words():
  words = list()
  for sequence in Sequence.query.limit(settings.SEQUENCE_LIMIT):
    words_in_sequence = utils.mecab.parse(sequence.content.encode('utf-8')).split()
    words.extend(words_in_sequence)
  return words

""" Build dictionaries
"""
def build_dictionary(words):
  print("Build dictionary...")
  count = collections.Counter(words).most_common(settings.VOCABULARY_SIZE - 2)
  dictionary = dict()
  dictionary['<PAD>'] = settings.PAD_ID # PAD -> 0
  dictionary['<UNK>'] = settings.UNK_ID # UNK -> 1
  for word, _ in count:
    if word != '<UNK>':
      dictionary[word] = len(dictionary)

  reverse_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
  with open('dicts/dictionary.pickle', 'wb') as handle:
    pickle.dump(dictionary, handle)
  with open('dicts/reverse_dictionary.pickle', 'wb') as handle:
    pickle.dump(reverse_dictionary, handle)

def build_emoji_sticker_dictionary():
  print("Build emoji-sticker dictionary...")
  es_dict = dict()
  with open('dicts/emoji_sticker_mapping.txt', 'r') as emoji_file:
    for line in emoji_file:
      (emoji, sticker_id) = line.split()
      es_dict[emoji] = int(sticker_id)
  with open('dicts/emoji_sticker_dictionary.pickle', 'wb') as handle:
    pickle.dump(es_dict, handle)

def build_sticker_dictionary():
  """ Line's sticker_id to unique_id
  unique_id: from 0 to sticker_number
  """
  print("Build sticker dictionary...")
  es_dict = utils.load_emoji_sticker_dictionary()
  uniq_stickers = list(set(es_dict.values()))
  sticker_dict = dict()
  for val in uniq_stickers:
    sticker_dict[val] = uniq_stickers.index(val)
  with open('dicts/sticker_dictionary.pickle', 'wb') as handle:
    pickle.dump(sticker_dict, handle)

def build_reverse_sticker_dictionary():
  """ unique_id to Line's sticker_id
  """
  print("Build reverse sticker dictionary...")
  sticker_dict = utils.load_sticker_dictionary()
  reverse_sticker_dict = {v: k for k, v in sticker_dict.items()}
  with open('dicts/reverse_sticker_dictionary.pickle', 'wb') as handle:
    pickle.dump(reverse_sticker_dict, handle)

""" Endpoint
"""
def build_dictionaries():
  words = get_words()
  build_dictionary(words)
  build_emoji_sticker_dictionary()
  build_sticker_dictionary()
  build_reverse_sticker_dictionary()

if __name__ == '__main__':
  build_dictionaries()
  dictionary, reverse_dictionary, emoji_sticker_dictionary, sticker_dictionary, reverse_sticker_dictionary = utils.load_dictionaries()
  print('len(dictionary): ' + str(len(dictionary)))
  print('dictionary[<PAD>]: ' + str(dictionary['<PAD>']))
  print('dictionary[<UNK>]: ' + str(dictionary['<UNK>']))
  print('len(reverse_dictionary): ' + str(len(reverse_dictionary)))
  [print("%d: %s" % (i,reverse_dictionary[i])) for i in xrange(5)]
  print('reverse_dictionary[100]: ' + str(reverse_dictionary[100]))
  print('len(emoji_sticker_dictionary): ' + str(len(emoji_sticker_dictionary)))
  print('len(sticker_dictionary): ' + str(len(sticker_dictionary)))
  print('len(reverse_sticker_dictionary):' + str(len(reverse_sticker_dictionary)))