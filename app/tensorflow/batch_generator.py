from app.models.sequence import Sequence
import app.common.settings as settings
import app.common.utils as utils

class BatchGenerator(object):
  def __init__(self, batch_size, global_id = 0):
    self.global_id = global_id
    self.batch_size = batch_size

  def next(self):
    inputs = list()
    labels = list()
    sequence_lengths = list()

    # FIXME: calling SQL query every step is quite slow. Should use a variable in memory instead.
    sequences = Sequence.query.offset(self.global_id).limit(self.batch_size)
    for sequence in sequences:
      train_ids, sequence_length = utils.seq2id(sequence.content.encode('utf-8'))
      train_label = utils.get_onehot_label(sequence)

      inputs.append(train_ids)
      labels.append(train_label)
      sequence_lengths.append(sequence_length)

    new_global_id = self.global_id + self.batch_size
    if new_global_id > settings.SEQUENCE_LIMIT - self.batch_size:
      self.global_id = 0
    else:
      self.global_id = new_global_id
    return inputs, labels, sequence_lengths
