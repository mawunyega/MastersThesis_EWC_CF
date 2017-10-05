from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np
import math

import argparse
import sys
import time

from sys import byteorder
from numpy import size

from tensorflow.python.framework import dtypes

from tensorflow.contrib.learn.python.learn.datasets.mnist import read_data_sets
from tensorflow.contrib.learn.python.learn.datasets.mnist import DataSet
from tensorflow.contrib.learn.python.learn.datasets.mnist import dense_to_one_hot

FLAGS = None

# The MNIST dataset has 10 classes, representing the digits 0 through 9.
NUM_CLASSES = 10

# The MNIST images are always 28x28 pixels.
IMAGE_SIZE = 28
IMAGE_PIXELS = IMAGE_SIZE * IMAGE_SIZE


# Initialize the DataSets for the permuted MNIST task
def initDataSetsPermutation():
    # Variable to read out the labels & data of the DataSet Object.
    mnistData = read_data_sets('/tmp/tensorflow/mnist/input_data',
                               one_hot=True)

    # MNIST labels & data for training.
    mnistLabelsTrain = mnistData.train.labels
    mnistDataTrain = mnistData.train.images

    # MNIST labels & data for testing.
    mnistLabelsTest = mnistData.test.labels
    mnistDataTest = mnistData.test.images

    mnistPermutationTrain = np.array(mnistDataTrain, dtype=np.float32)
    mnistPermutationTest = np.array(mnistDataTest, dtype=np.float32)

    # Concatenate both arrays to make sure the shuffling is consistent over
    # the training and testing sets, split them afterwards and create objects
    mnistPermutation = np.concatenate([mnistDataTrain, mnistDataTest])
    np.random.shuffle(mnistPermutation.T)
    mnistPermutationTrain, mnistPermutationTest = np.split(mnistPermutation, [
        mnistDataTrain.shape[0]])

    global dataSetOneTrain
    dataSetOneTrain = DataSet(255. * mnistDataTrain,
                              mnistLabelsTrain, reshape=False)
    global dataSetOneTest
    dataSetOneTest = DataSet(255. * mnistDataTest,
                             mnistLabelsTest, reshape=False)

    global dataSetTwoTrain
    dataSetTwoTrain = DataSet(255. * mnistPermutationTrain,
                              mnistLabelsTrain, reshape=False)
    global dataSetTwoTest
    dataSetTwoTest = DataSet(255. * mnistPermutationTest,
                             mnistLabelsTest, reshape=False)


# Initialize the DataSets for the partitioned digits task
def initDataSetsExcludedDigits():
    args = parser.parse_args()
    if args.exclude[0:]:
        labelsToErase = [int(i) for i in args.exclude[0:]]

    # Variable to read out the labels & data of the DataSet Object.
    mnistData = read_data_sets('/tmp/tensorflow/mnist/input_data',
                               one_hot=False)

    # MNIST labels & data for training.
    mnistLabelsTrain = mnistData.train.labels
    mnistDataTrain = mnistData.train.images

    # MNIST labels & data for testing.
    mnistLabelsTest = mnistData.test.labels
    mnistDataTest = mnistData.test.images

    # Filtered labels & data for training (DataSetOne).
    labelsExcludedTrain = np.array([mnistLabelsTrain[i] for i in xrange(0,
                                                                        mnistLabelsTrain.shape[0]) if
                                    mnistLabelsTrain[i]
                                    in labelsToErase], dtype=np.uint8)

    dataExcludedTrain = np.array([mnistDataTrain[i, :] for i in xrange(0,
                                                                       mnistLabelsTrain.shape[0]) if mnistLabelsTrain[i]
                                  in labelsToErase], dtype=np.float32)

    # Filtered labels & data for testing (DataSetOne).
    labelsExcludedTest = np.array([mnistLabelsTest[i] for i in xrange(0,
                                                                      mnistLabelsTest.shape[0]) if mnistLabelsTest[i]
                                   in labelsToErase], dtype=np.uint8)

    dataExcludedTest = np.array([mnistDataTest[i, :] for i in xrange(0,
                                                                     mnistLabelsTest.shape[0]) if mnistLabelsTest[i]
                                 in labelsToErase], dtype=np.float32)

    # Filtered labels & data for training (DataSetTwo).
    labelsKeepedTrain = np.array([mnistLabelsTrain[i] for i in xrange(0,
                                                                      mnistLabelsTrain.shape[0]) if mnistLabelsTrain[i]
                                  not in labelsToErase], dtype=np.uint8)

    dataKeepedTrain = np.array([mnistDataTrain[i, :] for i in xrange(0,
                                                                     mnistLabelsTrain.shape[0]) if mnistLabelsTrain[i]
                                not in labelsToErase], dtype=np.float32)

    # Filtered labels & data for testing (DataSetTwo).
    labelsKeepedTest = np.array([mnistLabelsTest[i] for i in xrange(0,
                                                                    mnistLabelsTest.shape[0]) if mnistLabelsTest[i]
                                 not in labelsToErase], dtype=np.uint8)

    dataKeepedTest = np.array([mnistDataTest[i, :] for i in xrange(0,
                                                                   mnistLabelsTest.shape[0]) if mnistLabelsTest[i]
                               not in labelsToErase], dtype=np.float32)

    # Transform labels to one-hot vectors
    labelsKeepedTrainOnehot = dense_to_one_hot(labelsKeepedTrain, 10)
    labelsExcludedTrainOnehot = dense_to_one_hot(labelsExcludedTrain, 10)

    labelsKeepedTestOnehot = dense_to_one_hot(labelsKeepedTest, 10)
    labelsExcludedTestOnehot = dense_to_one_hot(labelsExcludedTest, 10)

    labelsAllTrainOnehot = dense_to_one_hot(mnistLabelsTrain, 10)
    labelsAllTestOnehot = dense_to_one_hot(mnistLabelsTest, 10)

    # Create DataSets (1: kept digits, 2: excluded digits, all: MNIST digits)
    global dataSetOneTrain
    dataSetOneTrain = DataSet(255. * dataKeepedTrain,
                              labelsKeepedTrainOnehot, reshape=False)
    global dataSetOneTest
    dataSetOneTest = DataSet(255. * dataKeepedTest,
                             labelsKeepedTestOnehot, reshape=False)

    global dataSetTwoTrain
    dataSetTwoTrain = DataSet(255. * dataExcludedTrain,
                              labelsExcludedTrainOnehot, reshape=False)
    global dataSetTwoTest
    dataSetTwoTest = DataSet(255. * dataExcludedTest,
                             labelsExcludedTestOnehot, reshape=False)

    global dataSetAllTrain
    dataSetAllTrain = DataSet(255. * mnistDataTrain,
                              labelsAllTrainOnehot, reshape=False)
    global dataSetAllTest
    dataSetAllTest = DataSet(255. * mnistDataTest,
                             labelsAllTestOnehot, reshape=False)


def train():
    # feed dictionary for dataSetOne
    def feed_dict_1(train):
        if train:
            xs, ys = dataSetOneTrain.next_batch(FLAGS.batch_size_1)
            k_h = FLAGS.dropout_hidden
            k_i = FLAGS.dropout_input
        else:
            xs, ys = dataSetOneTest.images, dataSetOneTest.labels
            k_h = 1.0
            k_i = 1.0
        return {x: xs, y_: ys, keep_prob_input: k_i, keep_prob_hidden: k_h}

    # feed dictionary for dataSetTwo
    def feed_dict_2(train):
        if train:
            xs, ys = dataSetTwoTrain.next_batch(FLAGS.batch_size_2)
            k_h = FLAGS.dropout_hidden
            k_i = FLAGS.dropout_input
        else:
            xs, ys = dataSetTwoTest.images, dataSetTwoTest.labels
            k_h = 1.0
            k_i = 1.0
        return {x: xs, y_: ys, keep_prob_input: k_i, keep_prob_hidden: k_h}

    # feed dictionary for dataSetAll
    def feed_dict_all(train):
        if train:
            xs, ys = dataSetAllTrain.next_batch(FLAGS.batch_size_all)
            k_h = FLAGS.dropout_hidden
            k_i = FLAGS.dropout_input
        else:
            xs, ys = dataSetAllTest.images, dataSetAllTest.labels
            k_h = 1.0
            k_i = 1.0
        return {x: xs, y_: ys, keep_prob_input: k_i, keep_prob_hidden: k_h}

    # weights initialization
    def weight_variable(shape, stddev):
        initial = tf.truncated_normal(shape, stddev=stddev)
        return tf.Variable(initial)

    # biases initialization
    def bias_variable(shape):
        initial = tf.zeros(shape)
        return tf.Variable(initial)


        # define a fully connected layer

    def fc_layer(input, channels_in, channels_out, stddev, name='fc'):
        with tf.name_scope(name):
            with tf.name_scope('weights'):
                W = weight_variable([channels_in,
                                     channels_out], stddev)
            with tf.name_scope('biases'):
                b = bias_variable([channels_out])
            act = tf.nn.relu(tf.matmul(input, W) + b)
            tf.summary.histogram("weights", W)
            tf.summary.histogram("biases", b)
            tf.summary.histogram("activation", act)
            return act

    # define a sotfmax linear classification layer
    def softmax_linear(input, channels_in, channels_out, stddev, name='read'):
        with tf.name_scope(name):
            with tf.name_scope('weights'):
                W = weight_variable([channels_in,
                                     channels_out], stddev)
            with tf.name_scope('biases'):
                b = bias_variable([channels_out])
            act = tf.matmul(input, W) + b
            tf.summary.histogram("weights", W)
            tf.summary.histogram("biases", b)
            tf.summary.histogram("activation", act)
            return act

    # Start an Interactive session
    sess = tf.InteractiveSession()

    # Placeholder for input variables
    with tf.name_scope('input'):
        x = tf.placeholder(tf.float32, shape=[None, 784], name='x')
        y_ = tf.placeholder(tf.float32, shape=[None, 10], name='labels')
    x_image = tf.reshape(x, [-1, 28, 28, 1])
    tf.summary.image('input', x_image, 9)

    # apply dropout to the input layer
    keep_prob_input = tf.placeholder(tf.float32)
    tf.summary.scalar('dropout_input', keep_prob_input)

    x_drop = tf.nn.dropout(x, keep_prob_input)

    # Create the first hidden layer
    h_fc1 = fc_layer(x_drop, IMAGE_PIXELS, FLAGS.hidden1,
                     1.0 / math.sqrt(float(IMAGE_PIXELS)), 'h_fc1')

    # Apply dropout to first hidden layer
    keep_prob_hidden = tf.placeholder(tf.float32)
    tf.summary.scalar('dropout_hidden', keep_prob_hidden)

    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob_hidden)

    # Create the second hidden layer
    h_fc2 = fc_layer(h_fc1_drop, FLAGS.hidden1, FLAGS.hidden2,
                     1.0 / math.sqrt(float(FLAGS.hidden1)), 'h_fc2')

    # apply dropout to second hidden layer
    h_fc2_drop = tf.nn.dropout(h_fc2, keep_prob_hidden)

    # Create a softmax linear classification layer for the outputs
    logits_ds1 = softmax_linear(h_fc2_drop, FLAGS.hidden2, NUM_CLASSES,
                            1.0 / math.sqrt(float(FLAGS.hidden2)),
                            'softmax_linear')

    logits_ds2 = softmax_linear(h_fc2_drop, FLAGS.hidden2, NUM_CLASSES,
                            1.0 / math.sqrt(float(FLAGS.hidden2)),
                            'softmax_linear')

    # Define the loss model as a cross entropy with softmax
    with tf.name_scope('cross_entropy_ds1'):
        diff_ds1 = tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=logits_ds1)
        with tf.name_scope('total_ds1'):
            cross_entropy_ds1 = tf.reduce_mean(diff_ds1)
    tf.summary.scalar('cross_entropy_ds1', cross_entropy_ds1)

    with tf.name_scope('cross_entropy_ds2'):
        diff_ds2 = tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=logits_ds2)
        with tf.name_scope('total_ds2'):
            cross_entropy_ds2 = tf.reduce_mean(diff_ds2)
    tf.summary.scalar('cross_entropy_ds2', cross_entropy_ds2)

    # Use Gradient descent optimizer for training steps and minimize x-entropy
    with tf.name_scope('train'):
        train_step_ds1 = tf.train.GradientDescentOptimizer(
            FLAGS.learning_rate).minimize(cross_entropy_ds1)
        train_step_ds2 = tf.train.GradientDescentOptimizer(
        FLAGS.learning_rate).minimize(cross_entropy_ds2)

    # Compute correct prediction and accuracy
    with tf.name_scope('accuracy_ds1'):
        with tf.name_scope('correct_prediction_ds1'):
            correct_prediction_ds1 = tf.equal(tf.argmax(logits_ds1, 1), tf.argmax(y_, 1))
        with tf.name_scope('accuracy_ds1'):
            accuracy_ds1 = tf.reduce_mean(tf.cast(correct_prediction_ds1, tf.float32))
    tf.summary.scalar('accuracy_ds1', accuracy_ds1)

    with tf.name_scope('accuracy_ds2'):
        with tf.name_scope('correct_prediction_ds2'):
            correct_prediction_ds2 = tf.equal(tf.argmax(logits_ds2, 1), tf.argmax(y_, 1))
        with tf.name_scope('accuracy_ds2'):
            accuracy_ds2 = tf.reduce_mean(tf.cast(correct_prediction_ds2, tf.float32))
    tf.summary.scalar('accuracy_ds2', accuracy_ds2)

    # Merge all summaries and write them out to /tmp/tensorflow/mnist/logs
    # different writers are used to separate test accuracy from train accuracy
    # also a writer is implemented to observe CF after we trained on both sets
    merged = tf.summary.merge_all()

    train_writer_ds1 = tf.summary.FileWriter(FLAGS.log_dir + '/training_ds1',
                                             sess.graph)
    train_writer_ds2 = tf.summary.FileWriter(FLAGS.log_dir + '/training_ds2',
                                             sess.graph)

    test_writer_ds1 = tf.summary.FileWriter(FLAGS.log_dir + '/testing_ds1')
    test_writer_ds2 = tf.summary.FileWriter(FLAGS.log_dir + '/testing_ds2')

    test_writer_ds1_cf = tf.summary.FileWriter(FLAGS.log_dir +
                                               '/testing_ds1_cf')
    test_writer_dsc_cf = tf.summary.FileWriter(FLAGS.log_dir +
                                               '/testing_dsc_cf')

    # Initialize all global variables
    tf.global_variables_initializer().run()

    print('Fully Connected Neural Network with two hidden layers')
    print('Files being logged to... %s' % (FLAGS.log_dir,))
    print('\nHyperparameters:')
    print('____________________________________________________________')
    print('\nTraining steps for first training (data set 1): %s'
          % (FLAGS.max_steps_ds1,))
    print('Training steps for second training (data set 2): %s'
          % (FLAGS.max_steps_ds2,))
    print('Batch size for data set 1: %s' % (FLAGS.batch_size_1,))
    print('Batch size for data set 2: %s' % (FLAGS.batch_size_2,))
    print('Number of hidden units for layer 1: %s' % (FLAGS.hidden1,))
    print('Number of hidden units for layer 2: %s' % (FLAGS.hidden2,))
    print('Keep probability on input units: %s' % (FLAGS.dropout_input,))
    print('Keep probability on hidden units: %s' % (FLAGS.dropout_hidden,))
    print('Learning rate: %s' % (FLAGS.learning_rate,))
    print('\nInformation about the data sets:')
    print('____________________________________________________________')
    if FLAGS.exclude:
        print('\nExcluded digits: ')
        print('DataSetOne (train) contains: %s images.'
              % (dataSetOneTrain.labels.shape[0],))
        print('DataSetOne (test) contains: %s images.\n'
              % (dataSetOneTest.labels.shape[0],))
        print('DataSetTwo (train) contains: %s images.'
              % (dataSetTwoTrain.labels.shape[0],))
        print('DataSetTwo (test) contains: %s images.\n'
              % (dataSetTwoTest.labels.shape[0],))
        print('Original MNIST data-set (train) contains: %s images.'
              % (dataSetAllTrain.labels.shape[0],))
        print('Original MNIST data-set (test) contains: %s images.'
              % (dataSetAllTest.labels.shape[0],))
    if FLAGS.permutation:
        print('\nPermuted digits: ')
        print('DataSetOne (train) contains: %s images.'
              % (dataSetOneTrain.labels.shape[0],))
        print('DataSetOne (test) contains: %s images.\n'
              % (dataSetOneTest.labels.shape[0],))
        print('DataSetTwo (train) contains: %s images.'
              % (dataSetTwoTrain.labels.shape[0],))
        print('DataSetTwo (test) contains: %s images.\n'
              % (dataSetTwoTest.labels.shape[0],))

    print('\nTraining on DataSetOne...')
    print('____________________________________________________________')
    print(time.strftime('%X %x %Z'))
    # Start training on dataSetOne
    for i in range(FLAGS.max_steps_ds1):
        if i % 5 == 0:  # record summaries & test-set accuracy every 5 steps
            s, acc = sess.run([merged, accuracy_ds1], feed_dict=feed_dict_1(False))
            test_writer_ds1.add_summary(s, i)
            print('test set 1 accuracy at step: %s \t \t %s' % (i, acc))
        else:  # record train set summaries, and run training steps
            s, _ = sess.run([merged, train_step_ds1], feed_dict_1(True))
            train_writer_ds1.add_summary(s, i)
    train_writer_ds1.close()
    test_writer_ds1.close()

    print('\nTraining on DataSetTwo...')
    print('____________________________________________________________')
    print(time.strftime('%X %x %Z'))
    # Start training on dataSetTwo
    for i in range(FLAGS.max_steps_ds2):
        if i % 5 == 0:  # record summaries & test-set accuracy every 5 steps
            s1, acc1 = sess.run([merged, accuracy_ds2],
                                feed_dict=feed_dict_2(False))
            test_writer_ds2.add_summary(s1, i)
            print('test set 2 accuracy at step: %s \t \t %s' % (i, acc1))
            if FLAGS.exclude:
                s3, accC = sess.run([merged, accuracy_ds1],
                                    feed_dict=feed_dict_all(False))
                test_writer_dsc_cf.add_summary(s3, i)
        else:  # record train set summaries, and run training steps
            s, _ = sess.run([merged, train_step_ds2], feed_dict_2(True))
            train_writer_ds2.add_summary(s, i)
            s2, acc2 = sess.run([merged, accuracy_ds1],
                                feed_dict=feed_dict_1(False))
            # sess.run()
            test_writer_ds1_cf.add_summary(s2, i)
    train_writer_ds2.close()
    test_writer_ds2.close()
    test_writer_ds1_cf.close()
    if FLAGS.exclude:
        test_writer_dsc_cf.close()


def main(_):
    if tf.gfile.Exists(FLAGS.log_dir):
        tf.gfile.DeleteRecursively(FLAGS.log_dir)
        tf.gfile.MakeDirs(FLAGS.log_dir)
    if FLAGS.permutation:
        initDataSetsPermutation()
    if FLAGS.exclude:
        initDataSetsExcludedDigits()
    train()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--exclude', type=int, nargs='*',
                        help="Exclude specified classes from the MNIST DataSet")
    parser.add_argument('--permutation', action='store_true',
                        help='Use a random consistent permutation of MNIST.')
    parser.add_argument('--max_steps_ds1', type=int, default=2000,
                        help='Number of steps to run trainer for data set 1.')
    parser.add_argument('--max_steps_ds2', type=int, default=100,
                        help='Number of steps to run trainer for data set 2.')
    parser.add_argument('--hidden1', type=int, default=128,
                        help='Number of hidden units in layer 1')
    parser.add_argument('--hidden2', type=int, default=32,
                        help='Number of hidden units in layer 2')
    parser.add_argument('--batch_size_1', type=int, default=100,
                        help='Size of mini-batches we feed from dataSetOne.')
    parser.add_argument('--batch_size_2', type=int, default=100,
                        help='Size of mini-batches we feed from dataSetTwo.')
    parser.add_argument('--batch_size_all', type=int, default=100,
                        help='Size of mini-batches we feed from dataSetAll.')
    parser.add_argument('--learning_rate', type=float, default=0.01,
                        help='Initial learning rate')
    parser.add_argument('--dropout_hidden', type=float, default=0.5,
                        help='Keep probability for dropout on hidden units.')
    parser.add_argument('--dropout_input', type=float, default=0.8,
                        help='Keep probability for dropout on input units.')
    parser.add_argument('--data_dir', type=str,
                        default='/tmp/tensorflow/mnist/input_data',
                        help='Directory for storing input data')
    parser.add_argument('--log_dir', type=str,
                        default='/tmp/tensorflow/mnist/logs',
                        help='Summaries log directory')

    FLAGS, unparsed = parser.parse_known_args()
    tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)