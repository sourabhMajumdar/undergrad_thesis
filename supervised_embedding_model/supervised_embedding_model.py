
# coding: utf-8

# In[1]:


import tensorflow as tf

import math
import numpy as np


import argparse
import logging
import sys
from tqdm import tqdm
from make_tensor import make_tensor, load_vocab
from sklearn import metrics
from sys import argv
from test import evaluate
from utils import batch_iter, neg_sampling_iter, new_neg_sampling_iter
from data_utils import *
from itertools import chain
from six.moves import range, reduce
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime



class Model(object) :
    def __init__(self,vocab_dim=1000,embedding_size=20,margin=0.01,batch_size=64,learning_rate=1e-2,epochs=20,description="random_description",session=tf.Session()) :
        self.vocab_dim = vocab_dim
        self.embedding_size = embedding_size
        self.random_seed = 42
        self.margin = margin
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs
        self.description = description
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        self.root_dir = '{}/{}-{}'.format(self.description,'summary_output',timestamp)
        self.session = session
        
        self.config = tf.ConfigProto()
        self.config.gpu_options.allow_growth = True
        self.build_model()
        
        self.saver = tf.train.Saver()
        
        init_op = tf.global_variables_initializer()
        self.session.run(init_op)
        
    def build_model(self) :
        self.create_variables()
        tf.set_random_seed(self.random_seed + 1)
        
        self.A_var = tf.Variable(initial_value=tf.random_uniform(shape=[self.embedding_size,self.vocab_dim],minval=-1,maxval=1,seed=(self.random_seed + 2)))
        self.B_var = tf.Variable(initial_value=tf.random_uniform(shape=[self.embedding_size,self.vocab_dim],minval=-1,maxval=1,seed=(self.random_seed + 2)))
        
        self.global_step = tf.Variable(0,dtype=tf.int32,trainable=False,name='global_step')
        
        self.cont_mult = tf.transpose(tf.matmul(self.A_var,tf.transpose(self.context_batch)))
        self.resp_mult = tf.matmul(self.B_var,tf.transpose(self.response_batch))
        self.neg_resp_mult = tf.matmul(self.B_var,tf.transpose(self.neg_response_batch))
        
        self.pos_raw_f = tf.diag_part(tf.matmul(self.cont_mult,self.resp_mult))
        self.neg_raw_f = tf.diag_part(tf.matmul(self.cont_mult,self.neg_resp_mult))
        
        self.f_pos = self.pos_raw_f

        #print("shape of self.f_pos is {}".format(self.f_pos.get_shape().as_list()))
        self.f_neg = self. neg_raw_f
        
        self.predict_op = tf.argmax(self.f_pos,axis=0,name='predict_op')
        #print("shape of f_pos is {}".format(self.f_pos.get_shape().as_list()))
        
        self.loss = tf.reduce_sum(tf.nn.relu(self.f_neg - self.f_pos + self.margin))

        self.graph_output = self.loss
        
        self.optimizer = tf.train.AdamOptimizer(self.learning_rate).minimize(self.loss)
        
    def create_variables(self) :
        
        self.context_batch = tf.placeholder(dtype=tf.float32,name='Context',shape=[None,self.vocab_dim])
        self.response_batch = tf.placeholder(dtype=tf.float32,name='Response',shape=[None,self.vocab_dim])
        self.neg_response_batch = tf.placeholder(dtype=tf.float32,name='NegResponse',shape=[None,self.vocab_dim])
        
    def _init_summaries(self) :
        self.accuracy = tf.placeholder_with_default(0.0,shape=(),name='Accuracy')
        self.accuracy_summary = tf.scaler_summary('Accuracy summary',self.accuracy)
        
        self.f_pos_summary = tf.histogram_summary('f_pos',self.f_pos)
        self.f_neg_summary = tf.histogram_summary('f_neg',self.f_neg)
        
        self.loss_summary = tf.scaler_summary('Mini-batch loss',self.loss)
        
        self.summary_op = tf.merge_summary([self.f_pos_summary,self.f_neg_summary,self.loss_summary])
        
    def batch_fit(self,context_batch,response_batch,neg_response_batch) :
        feed_dict = {self.context_batch : context_batch, self.response_batch : response_batch, self.neg_response_batch : neg_response_batch}
        loss = self.session.run([self.loss,self.optimizer],feed_dict=feed_dict)
        return loss
    
    def batch_predict(self,context_batch,response_batch) :
        feed_dict = {self.context_batch : context_batch, self.response_batch : response_batch}
        preds = self.session.run(self.predict_op,feed_dict=feed_dict)
        return preds
    
    def batch_compute_loss(self,context_batch,response_batch,neg_response_batch) :
        feed_dict = {self.context_batch : context_batch, self.response_batch : response_batch, self.neg_response_batch : neg_response_batch}
        loss = self.session.run([self.loss],feed_dict=feed_dict)
        return loss



def create_tensor(file_directory,file_name,vocab_dict) :
    context_response_pairs = list()
    f_handle = open(os.path.join(file_directory,file_name))
    for line in f_handle :
        sentences = line[1:].strip().split('\t')
        if len(sentences) != 2 :
            context_response_pairs.append((sentences[0],'<silence>'))
        else :
            context_response_pairs.append((sentences[0],sentences[1]))
    
    f_handle.close()
    context_list = list()
    response_list = list()
    for i, context_response in enumerate(context_response_pairs) :
        context, response = context_response
        
        vec1 = np.zeros(len(vocab_dict)+1)
        for w in context.split(' ') :
            try :
                vec1[vocab_dict[w]] = 1
            except KeyError :
                pass
        vec2 = np.zeros(len(vocab_dict)+1)
        
        for w in response.split(' ') :
            try :
                vec2[vocab_dict[w]] = 1
            except KeyError :
                pass
        context_list.append(vec1)
        response_list.append(vec2)
    context_tensor = np.array(context_list)
    response_tensor = np.array(response_list)
    return context_tensor, response_tensor
            



