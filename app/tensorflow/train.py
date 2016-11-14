from __future__ import print_function

import tensorflow as tf

import app.common.utils as utils
import app.common.settings as settings
from app.models.sequence import Sequence
from batch_generator import BatchGenerator

def model(graph):
  with graph.as_default():
    inputs = tf.placeholder(tf.int32, shape=[None, settings.MAX_SEQUENCE_LENGTH])
    labels = tf.placeholder(tf.float32, shape=[None, utils.sticker_size()])
    sequence_lengths = tf.placeholder(tf.int32, shape=(None,))
    
    embedding = tf.get_variable("embedding", shape=[settings.VOCABULARY_SIZE, settings.EMBEDDING_SIZE], dtype=tf.float32)
    embed_inputs = tf.nn.embedding_lookup(embedding, inputs)

    # keep_prob = tf.placeholder(tf.float32)
    # drop_embed_inputs = tf.nn.dropout(embed_inputs, keep_prob)

    # Use LSTM as cell
    cell = tf.nn.rnn_cell.BasicLSTMCell(settings.LSTM_SIZE, state_is_tuple=True)
    #cell = tf.nn.rnn_cell.DropoutWrapper(cell, output_keep_prob=keep_prob)
    #multi_cell = tf.nn.rnn_cell.MultiRNNCell([cell] * settings.NUM_LSTM_LAYERS, state_is_tuple=True)

    # Define RNN
    with tf.variable_scope("dynamic_rnn"):
      outputs, state = tf.nn.dynamic_rnn(cell,
                        embed_inputs,
                        dtype=tf.float32,
                        sequence_length=sequence_lengths
                        )

    # Classifier weights and biases.
    w = tf.Variable(tf.truncated_normal([settings.LSTM_SIZE, utils.sticker_size()], -0.1, 0.1), name='w')
    b = tf.Variable(tf.zeros([utils.sticker_size()]), name='b')

    # Calculate logits and loss
    logits = tf.nn.xw_plus_b(state.h, w, b)
    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits, labels))

    tf.scalar_summary('loss/loss', loss)
    # Configure optimizer
    optimizer = tf.train.AdamOptimizer(settings.LEARNING_RATE).minimize(loss)
    predictions = tf.nn.softmax(logits)

    summary_op = tf.merge_all_summaries()
    saver = tf.train.Saver()

    return inputs, labels, sequence_lengths, optimizer, loss, predictions, summary_op, saver

def train():
  graph = tf.Graph()
  inputs, labels, sequence_lengths, optimizer, loss, predictions, summary_op, saver = model(graph)
  train_writer = tf.train.SummaryWriter('tensorboard/train', graph)
  test_writer = tf.train.SummaryWriter('tensorboard/test', graph)

  with tf.Session(graph=graph) as sess:
    sess.run(tf.initialize_all_variables())
    print("Training...")
    train_batches = BatchGenerator(settings.BATCH_SIZE)
    test_batches = BatchGenerator(3000, settings.SEQUENCE_LIMIT)
    test_inputs, test_labels, test_sequence_lengths = test_batches.next()

    for step in xrange(settings.EPOCH):
      if step % 1000 != 1:
        train_inputs, train_labels, train_sequence_lengths = train_batches.next()
        feed_dict = { inputs: train_inputs, labels: train_labels, sequence_lengths: train_sequence_lengths }
        _, train_loss, train_predictions, summary = sess.run([optimizer, loss, predictions, summary_op], feed_dict=feed_dict)
        train_writer.add_summary(summary, step)
        train_writer.flush()
      else:
        test_feed_dict = { inputs: test_inputs, labels: test_labels, sequence_lengths: test_sequence_lengths }
        test_loss, summary = sess.run([loss, summary_op], feed_dict=test_feed_dict)
        test_writer.add_summary(summary, step)
        test_writer.flush()

      if step % 1000 == 0:
        print('-----------Step %d:-------------' % step)
        print('Training set:')
        print('  Loss       : ', train_loss)
        print('  Input      : ', train_inputs[0])
        print('  Label      : ', utils.onehot2sticker(train_labels))
        print('  Prediction : ', utils.onehot2sticker(train_predictions))
              
      if step % 10000 == 0:
        # Save the variables to disk.
        save_path = saver.save(sess, "checkpoints/" + settings.CKPT_NAME)
        print("Model saved in file: %s" % save_path)

if __name__ == '__main__':
  train()
