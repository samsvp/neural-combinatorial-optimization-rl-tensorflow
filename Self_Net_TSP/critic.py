import tensorflow as tf
from tensorflow.compat.v1.nn.rnn_cell import LSTMCell, MultiRNNCell, DropoutWrapper
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

from encoder import Attentive_encoder

tf.compat.v1.disable_eager_execution()
tf.compat.v1.disable_v2_behavior() 

class Critic(object):


    def __init__(self, config):
        self.config=config

        # Data config
        self.batch_size = config.batch_size # batch size
        self.max_length = config.max_length # input sequence length (number of cities)
        self.input_dimension = config.input_dimension # dimension of a city (coordinates)

        # Network config
        self.input_embed = config.hidden_dim # dimension of embedding space
        self.num_neurons = config.hidden_dim # dimension of hidden states (LSTM cell)
        # GlorotUniform == xavier_initialer
        self.initializer = initializer = tf.initializers.GlorotUniform() # variables initializer

        # Baseline setup
        self.init_baseline = 0. # self.max_length/2 # good initial baseline for TSP

        # Training config
        self.is_training = not config.inference_mode


    def predict_rewards(self,input_):

        with tf.compat.v1.variable_scope("encoder"):

            Encoder = Attentive_encoder(self.config)
            encoder_output = Encoder.encode(input_)
            frame = tf.reduce_mean(encoder_output, 1) # [Batch size, Sequence Length, Num_neurons] to [Batch size, Num_neurons]

        with tf.compat.v1.variable_scope("ffn"):
            # ffn 1
            h0 = tf.compat.v1.layers.dense(frame, self.num_neurons, activation=tf.nn.relu, kernel_initializer=self.initializer)
            # ffn 2
            w1 =tf.compat.v1.get_variable("w1", [self.num_neurons, 1], initializer=self.initializer)
            b1 = tf.Variable(self.init_baseline, name="b1")
            self.predictions = tf.squeeze(tf.matmul(h0, w1)+b1)
