import tensorflow as tf
import numpy as np
import argparse
import logging
import sys
from tqdm import tqdm
from make_tensor import make_tensor, load_vocab, new_make_tensor
from sklearn import metrics
from model2 import Model
from sys import argv
from test import evaluate
from utils import batch_iter, neg_sampling_iter, new_neg_sampling_iter


tf.flags.DEFINE_string('train','data/train-task-1.tsv','Training file directory')
tf.flags.DEFINE_string('dev','data/dev-task-1-500.tsv','Validation file directory')
tf.flags.DEFINE_string('vocab','data/vocab.tsv','Vocab directory')
tf.flags.DEFINE_string('candidates','data/candidates.tsv','candidate directory')
tf.flags.DEFINE_integer('emb_dim',32,'embedding size the network')
tf.flags.DEFINE_string('save_dir','checkpoints/task-1/model','place to save')
tf.flags.DEFINE_float('margin',0.01,'margin of error for the function')
tf.flags.DEFINE_integer('negative_cand',100,'size of negative candidates')
tf.flags.DEFINE_float('learning_rate',0.01,'learning rate for the model')
FLAGS = tf.flags.FLAGS





def main_2(train_context,train_response,train_candidates,model,config) :

    epochs = config['epochs']
    batch_size = config['batch_size']
    negative_cand = config['negative_cand']
    save_dir = config['save_dir']
    n_train = len(train_context)
    print("Training Size : {}".format(n_train))

    train_batches = zip(range(0,n_train-batch_size,batch_size),range(batch_size,n_train,batch_size)) 
    train_batches = [(start,end) for start,end in train_batches]
    
    #print(type(neg_samples))
    for t in range(1,epochs + 1) :
       print(" Epoch# {}".format(t))
       np.random.shuffle(train_batches)
       total_cost = 0.0
       neg_samples = list()
       for start,end in tqdm(train_batches) :
           neg_train_response = list(train_response[:max(0,start-1)]) + list(train_response[min(n_train,end + 1):])
           neg_samples = new_neg_sampling_iter(train_response,batch_size,negative_cand)
           for n in neg_samples :
               c = train_context[start:end]
               r = train_response[start:end]

               #print("shape of neg_batch")
               #print(n.shape)
               loss = model.batch_fit(c,r,n)
               total_cost += loss[0]
       total_cost /= (n_train*negative_cand) 
       print('Train cost : {}'.format(str(total_cost)))
           





if __name__ == '__main__':
    vocab = load_vocab(FLAGS.vocab)
    print("printing vocab ")
    print("type of vocab {}".format(vocab))
    print(type(vocab))
    train_tensor = make_tensor(FLAGS.train, vocab)
    train_context, train_response = new_make_tensor(FLAGS.train,vocab)

    
    dev_tensor = make_tensor(FLAGS.dev, vocab)
    val_context, val_response = new_make_tensor(FLAGS.dev,vocab)
    print(dev_tensor)
    candidates_tensor = make_tensor(FLAGS.candidates, vocab)
    train_candidates, _ = new_make_tensor(FLAGS.candidates,vocab)
    
    config = {'batch_size': 32, 'epochs': 20,
              'negative_cand': FLAGS.negative_cand, 'save_dir': FLAGS.save_dir,
              'lr': FLAGS.learning_rate}
    model = Model(len(vocab), emb_dim=FLAGS.emb_dim, margin=FLAGS.margin)
    
    main_2(train_context,train_response,train_candidates,model,config)
