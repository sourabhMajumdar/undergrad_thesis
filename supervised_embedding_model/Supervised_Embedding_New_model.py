
# coding: utf-8

# In[1]:


import tensorflow as tf


# In[2]:


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


# In[9]:


train = 'data/train-task-1.tsv'
dev = 'data/dev-task-1-500.tsv'
vocab_file = 'data/vocab-task-1.tsv'
candidates = 'data/candidates-1.tsv'
embedding_size = 128
save_dir = 'checkpoints/task-1/model'
margin = 0.01
negative_cand = 10
learning_rate = 0.01
batch_size = 2048
epochs = 1


# In[10]:


class Model(object) :
    def __init__(self,vocab_dim=1000,embedding_size=20,margin=0.01,batch_size=64,learning_rate=1e-2,epochs=20) :
        self.vocab_dim = vocab_dim
        self.embedding_size = embedding_size
        self.random_seed = 42
        self.margin = margin
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs
        
        self.session = tf.Session()
        
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
        self.f_neg = self. neg_raw_f
        
        self.predict_op = tf.argmax(self.f_pos,axis=0,name='predict_op')
        
        self.loss = tf.reduce_sum(tf.nn.relu(self.f_neg - self.f_pos + self.margin))
        
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


# In[11]:


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
            


# In[12]:


class SupervisedEmbeddingModel(object) :
    def __init__(self,embedding_size,random_seed,margin,negative_cand,batch_size,epochs,data_dir) :
        
        self.embedding_size = embedding_size
        self.random_seed = random_seed
        self.margin = margin
        self.negative_cand = negative_cand
        self.batch_size = batch_size
        self.epochs = epochs
        self.data_dir = data_dir
        self.OOV = False
        self.memory_size = 10
        candidates, self.candid2indx = load_candidates(self.data_dir)
        self.n_cand = len(candidates)
        print("Candidate Size", self.n_cand)
        self.indx2candid = dict((self.candid2indx[key], key) for key in self.candid2indx)
        # task data
        self.trainData, self.testData, self.valData = load_dialog_task(self.data_dir, self.candid2indx, self.OOV)
        data = self.trainData + self.testData + self.valData
        self.build_vocab(data, candidates)
        # self.candidates_vec=vectorize_candidates_sparse(candidates,self.word_idx)
        self.candidates_vec = vectorize_candidates(candidates, self.word_idx, self.candidate_sentence_size)
        
        self.model = Model(vocab_dim=self.vocab_size,embedding_size=self.embedding_size,margin=self.margin,batch_size=self.batch_size,epochs=self.epochs)
        
    def build_vocab(self, data, candidates):
        
        vocab = reduce(lambda x, y: x | y, (set(
            list(chain.from_iterable(s)) + q) for s, q, a in data))
        vocab |= reduce(lambda x, y: x | y, (set(candidate)
                                             for candidate in candidates))
        vocab = sorted(vocab)
        self.word_idx = dict((c, i + 1) for i, c in enumerate(vocab))
        max_story_size = max(map(len, (s for s, _, _ in data)))
        mean_story_size = int(np.mean([len(s) for s, _, _ in data]))
        self.sentence_size = max(
            map(len, chain.from_iterable(s for s, _, _ in data)))
        self.candidate_sentence_size = max(map(len, candidates))
        query_size = max(map(len, (q for _, q, _ in data)))
        self.memory_size = min(self.memory_size,max_story_size)
        self.vocab_size = len(self.word_idx) + 1  # +1 for nil word
        self.sentence_size = max(
            query_size, self.sentence_size)  # for the position
        # params
        print("vocab size:", self.vocab_size)
        print("Longest sentence length", self.sentence_size)
        print("Longest candidate sentence length",
              self.candidate_sentence_size)
        print("Longest story length", max_story_size)
        print("Average story length", mean_story_size)


    def print_results(self,cost,accuracy,description,fbeta_score) :
        print("---------------------RESULTS FOR {}----------------------".format(description))
        print("\n=====================> {} cost     = {}".format(description,str(cost)))
        print("=====================> {} accuracy = {}%".format(description,str(accuracy*100)))
        print("=====================> {} fbeta score = {} \n".format(description,str(fbeta_score)))
        print("-------------------------------><---------------------------------------------")

    def display_results(self,train_cost_list,train_fbeta_list,val_cost_list,val_fbeta_list,epoch_list) :

        
        plt.subplot(2,1,1)
        plt.title(self.description + "_performance")
        plt.plot(epoch_list,train_cost_list,'b',label='train_cost')
        plt.plot(epoch_list,val_cost_list,'r',label='val_cost')
        
        plt.xlabel('#Epochs')
        plt.ylabel('Cost')
        red_patch = mpatches.Patch(color='red',label='Validation Cost')
        blue_patch = mpatches.Patch(color='blue',label='Training Cost')
        
        plt.legend(handles=[red_patch,green_patch,yellow_patch,blue_patch],loc='upper right')


        plt.subplot(2,1,2)
        red_beta_patch = mpatches.Patch(color='blue',label='train_fbeta_score')
        blue_beta_patch = mpatches.Patch(color='red',label='val_fbeta_score')
        plt.legend(handles=[red_beta_patch,blue_beta_patch],loc='upper right')
        plt.plot(epoch_list,train_fbeta_list,'b',label='train_fbeta_score')
        plt.plot(epoch_list,val_fbeta_list,'r',label='val_fbeta_score')
        plt.xlabel('#Epochs')
        plt.ylabel('fbeta_score')

        
        plt.show()
        plt.pause(0.01)
        
    def train(self) :
        
        self.train_file_name = os.path.join(self.data_dir,'train_data.txt')
        self.val_file_name = os.path.join(self.data_dir,'val_data.txt')
        self.candidate_file_name = os.path.join(self.data_dir,'candidates.txt')
        
        vocab = self.word_idx
        
        _, _, trainA = vectorize_data(self.trainData,self.word_idx,self.sentence_size,self.batch_size,self.n_cand,self.memory_size)
        _, _, valA = vectorize_data(self.valData,self.word_idx,self.sentence_size,self.batch_size,self.n_cand,self.memory_size)

        print("Name of train file is : {}\n type of vocab is : {}".format(self.train_file_name,type(vocab)))
        #train_context, train_response = make_tensor(self.train_file_name,self.word_idx)
        train_context, train_response = create_tensor(self.data_dir,'train_data.txt',self.word_idx)
        print("length of train_context : {}, length of train_response : {}".format(len(train_context),len(train_response)))

        candidates, _ = create_tensor(self.data_dir,'candidates.txt',self.word_idx)

        val_context,val_response = create_tensor(self.data_dir,'val_data.txt',self.word_idx)
        n_train = len(train_context)
        n_val = len(val_context)

        train_batches = zip(range(0,n_train-self.batch_size,self.batch_size),range(self.batch_size,n_train,self.batch_size))
        train_batches = [(start,end) for start,end in train_batches]
        
        val_batches = zip(range(0,n_val-self.batch_size,self.batch_size),range(self.batch_size,n_val,self.batch_size))
        val_batches = [(start,end) for start,end in val_batches]

        epoch_list = list()
        train_cost_list = list()
        val_cost_list = list()
        avg_train_cost_list = list()
        avg_val_cost_list = list()
        train_fbeta_list = list()
        val_fbeta_list = list()


        for t in range(1,self.epochs + 1) :
            print("Epoch# {}".format(t))
            np.random.shuffle(train_batches)
            total_train_cost = 0.0
            total_val_cost = 0.0
            neg_samples = list()
            for start, end in tqdm(train_batches) :
                
                neg_train_response = np.array(train_response.tolist()[:max(0,start - 1)] + train_response.tolist()[min(n_train,end + 1):])
                neg_samples = new_neg_sampling_iter(neg_train_response,self.batch_size,self.negative_cand)
                for n in neg_samples :
                    c = train_context[start:end]
                    r = train_response[start:end]
                    train_loss = self.model.batch_fit(c,r,n)
                    total_train_cost += train_loss[0]

            train_preds = self.batch_predict(train_context,candidates)

            train_accuracy = metrics.accuracy_score(np.array(train_preds),trainA)
            train_fbeta_score = metrics.fbeta_score(np.array(train_preds),trainA)

            total_train_cost /= (n_train*self.negative_cand)

            epoch_list.append(t)

            train_cost_list.append(total_train_cost)
            train_fbeta_list.append(train_fbeta_score)

            self.print_results(cost=total_train_cost,
                accuracy=train_accuracy,
                fbeta_score=train_fbeta_score,
                description="training")

            
            
            for start,end in tqdm(val_batches) :
                c = val_context[start:end]
                r = val_response[start:end]
                neg_val_response = np.array(val_response.tolist()[:max(0,start-1)] + val_response.tolist()[min(n_val,end + 1):])
                neg_samples = new_neg_sampling_iter(neg_val_response,self.batch_size,self.negative_cand)
                for n in neg_samples :
                    val_loss = self.model.batch_compute_loss(c,r,n)
                    total_val_cost += val_loss[0]

            total_val_cost /= (n_val*self.negative_cand)

            val_preds = self.batch_predict(val_context,candidates)

            val_accuracy = metrics.accuracy_score(np.array(val_preds),valA)
            val_fbeta_score = metrics.fbeta_score(np.array(val_preds),valA)
           
            val_cost_list.append(total_val_cost)
            val_fbeta_list.append(val_fbeta_score)

            self.print_results(cost=total_val_cost,
                accuracy=val_accuracy,
                fbeta_score=val_fbeta_score,
                description="validation")

            self.display_results(train_cost_list=train_cost_list,
                train_fbeta_list=train_fbeta_list,
                val_cost_list=val_cost_list,
                val_fbeta_list=val_fbeta_list,
                epoch_list=epoch_list)
            

    def batch_predict(self,train_context,train_response) :
        candidate_list = list()
        for i in tqdm(range(len(train_context))) :
            score_list = list()
            for j in range(len(train_response)) :
                #print("Printing the shape of train_response : {} \n shape of train_context is : {}".format(train_response[j:j+1].shape,train_context[i:i+1].shape))
                score = self.model.batch_predict(train_context[i].reshape(1,train_context[i].shape[0]),train_response[j].reshape(1,train_response[j].shape[0]))
                score_list.append(score)
            score_list_array = np.array(score_list)
            candidate_index = np.argmax(score_list_array)
            candidate_list.append(candidate_index)
        return candidate_list


# In[ ]:



model = SupervisedEmbeddingModel(embedding_size=embedding_size,
                                 random_seed=42,
                                 margin=margin,
                                 negative_cand=negative_cand,
                                 batch_size=batch_size,
                                 epochs=epochs,
                                  data_dir='data/')

model.train()

