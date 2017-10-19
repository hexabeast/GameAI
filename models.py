#!env2/bin/python
import tflearn
from tflearn.layers.conv import conv_2d, max_pool_2d,avg_pool_2d, conv_3d, max_pool_3d, avg_pool_3d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from tflearn.layers.normalization import local_response_normalization
from tflearn.layers.merge_ops import merge
import tensorflow as tf

def alexnet2(width, height, lr, output=3, timesteps = 50):
    network = input_data(shape=[None, width, height, 3], name='input')
    network = tflearn.reshape(network, [-1, width, height, 3])
    network = conv_2d(network, 96, 11, strides=4, activation='relu')
    network = max_pool_2d(network, 3, strides=2)
    network = local_response_normalization(network)
    network = conv_2d(network, 128, 5, activation='relu')
    network = max_pool_2d(network, 3, strides=2)
    network = local_response_normalization(network)
    network = conv_2d(network, 128, 3, activation='relu')
    network = conv_2d(network, 128, 3, activation='relu')
    network = conv_2d(network, 128, 3, activation='relu')
    network = max_pool_2d(network, 3, strides=2)
    network = conv_2d(network, 128, 5, activation='relu')
    #network = max_pool_2d(network, 3, strides=2)
    network = local_response_normalization(network)
    network = conv_2d(network, 128, 3, activation='relu')
    network = conv_2d(network, 128, 3, activation='relu')
    network = conv_2d(network, 128, 3, activation='relu')
    network = max_pool_2d(network, 3, strides=2)
    network = local_response_normalization(network)
    print(network.shape)
    network = fully_connected(network, 2048, activation='tanh')
    network = dropout(network, 0.5)
    network = fully_connected(network, 1024, activation='tanh')
    network = dropout(network, 0.5)
    '''network = fully_connected(network, 4096, activation='tanh')
    network = dropout(network, 0.5)
    network = fully_connected(network, 4096, activation='tanh')
    network = dropout(network, 0.5)'''
    ###
    print(network.shape)
    network = tflearn.reshape(network, [-1, timesteps, 1024])
    network = tflearn.lstm(network, 128, dropout=0.8, dynamic=True,return_seq=True)
    '''network = tflearn.layers.merge_ops.merge(network,'concat',axis=0,name="MERGE")
    print(network.shape)
    network = tflearn.reshape(network, [-1,timesteps, 128])
    '''
    network = tflearn.lstm(network, 128, dropout=0.8, dynamic=True,return_seq=True)
    '''network = tflearn.layers.merge_ops.merge(network,'concat',axis=0,name="MERGE2")
    print(network.shape)
    network = tflearn.reshape(network, [-1, 128])'''
    ###
    network = tf.concat(network,axis=0)
    network = fully_connected(network, output, activation='softmax')
    network = regression(network, optimizer='momentum',
                         loss='categorical_crossentropy',
                         learning_rate=lr, name='targets')

    model = tflearn.DNN(network, checkpoint_path='model_alexnet',
                        max_checkpoints=1, tensorboard_verbose=0, tensorboard_dir='log')
    return model

    

def alexnet2backup(width, height, lr, output=3, timesteps = 50):
    network = input_data(shape=[None, width, height, 3], name='input')
    network = tflearn.reshape(network, [-1, width, height, 3])
    network = conv_2d(network, 96, 11, strides=4, activation='relu')
    network = max_pool_2d(network, 3, strides=2)
    network = local_response_normalization(network)
    network = conv_2d(network, 256, 5, activation='relu')
    network = max_pool_2d(network, 3, strides=2)
    network = local_response_normalization(network)
    network = conv_2d(network, 256, 3, activation='relu')
    network = conv_2d(network, 256, 3, activation='relu')
    network = conv_2d(network, 256, 3, activation='relu')
    network = max_pool_2d(network, 3, strides=2)
    network = conv_2d(network, 256, 5, activation='relu')
    #network = max_pool_2d(network, 3, strides=2)
    network = local_response_normalization(network)
    network = conv_2d(network, 256, 3, activation='relu')
    network = conv_2d(network, 256, 3, activation='relu')
    network = conv_2d(network, 128, 3, activation='relu')
    network = max_pool_2d(network, 3, strides=2)
    network = local_response_normalization(network)
    network = fully_connected(network, 4096, activation='tanh')
    network = dropout(network, 0.5)
    network = fully_connected(network, 2048, activation='tanh')
    network = dropout(network, 0.5)
    network = fully_connected(network, 2048, activation='tanh')
    network = dropout(network, 0.5)
    network = fully_connected(network, 2048, activation='tanh')
    network = dropout(network, 0.5)
    ###
    #network = tflearn.reshape(network, [-1, timesteps, 2048])
    #network = tflearn.lstm(network, 128, dropout=0.8)
    ###
    network = fully_connected(network, output, activation='softmax')
    network = regression(network, optimizer='momentum',
                         loss='categorical_crossentropy',
                         learning_rate=lr, name='targets')

    model = tflearn.DNN(network, checkpoint_path='model_alexnet',
                        max_checkpoints=1, tensorboard_verbose=0, tensorboard_dir='log')

    return model