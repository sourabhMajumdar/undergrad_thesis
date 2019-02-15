
# coding: utf-8

# In[1]:


import tensorflow as tf


# In[2]:


import math
import numpy as np
import random

import argparse
import logging
import sys
from tqdm import tqdm
from make_tensor import make_tensor, load_vocab, create_tensor
from sklearn import metrics
from sys import argv
from test import evaluate
from utils import batch_iter, neg_sampling_iter, new_neg_sampling_iter
from data_utils import *
from itertools import chain
from six.moves import range, reduce
from supervised_embedding_model import Model
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
plt.ion()



tf.flags.DEFINE_string('data_dir','data/','Data directory for training and validation')
tf.flags.DEFINE_integer('epochs',20,'number of epochs to run the file')
tf.flags.DEFINE_float('margin',0.01,'margin to keep for the model')
tf.flags.DEFINE_integer('batch_size',2048,'batch size for training the model')
tf.flags.DEFINE_integer('negative_cand',100,'number of negative candidates to compare')
tf.flags.DEFINE_integer('embedding_size',128,'size of embedding for the model')
tf.flags.DEFINE_integer('evaluation_interval',1,'time after which to evaluate your model')
tf.flags.DEFINE_string('model_dir','supervised_embedding_model/','model directory to save the trained model')
tf.flags.DEFINE_boolean('train',True,'If set to true then train the model')
FLAGS = tf.flags.FLAGS



class SupervisedEmbeddingModel(object) :

    def __init__(self,embedding_size,random_seed,margin,negative_cand,batch_size,epochs,evaluation_interval,data_dir,model_dir,description) :
        
        self.embedding_size = embedding_size
        self.random_seed = random_seed
        self.margin = margin
        self.negative_cand = negative_cand
        self.batch_size = batch_size
        self.epochs = epochs
        self.evaluation_interval = evaluation_interval
        self.data_dir = data_dir
        self.OOV = False
        self.memory_size = 10
        self.model_dir = model_dir
        self.evaluation_interval = evaluation_interval
        candidates, self.candid2indx = load_candidates(self.data_dir)
        self.n_cand = len(candidates)
        self.description = description
        self.session = tf.Session()
        print("Candidate Size", self.n_cand)

        self.indx2candid = dict((self.candid2indx[key], key) for key in self.candid2indx)
        # task data
        self.trainData, self.testData, self.valData = load_dialog_task(self.data_dir, self.candid2indx, self.OOV)
        data = self.trainData + self.testData + self.valData
        self.build_vocab(data, candidates)
        # self.candidates_vec=vectorize_candidates_sparse(candidates,self.word_idx)
        self.candidates_vec = vectorize_candidates(candidates, self.word_idx, self.candidate_sentence_size)
        
        self.model = Model(vocab_dim=self.vocab_size,embedding_size=self.embedding_size,margin=self.margin,batch_size=self.batch_size,epochs=self.epochs,description=self.description,session=self.session)
        
        self.saver = tf.train.Saver(max_to_keep=50)
        self.summary_writer = tf.summary.FileWriter(self.model.root_dir,self.model.graph_output.graph)

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
        self.memory_size = min(self.memory_size, max_story_size)
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
        
        plt.legend(handles=[red_patch,blue_patch],loc='upper right')


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

        print("length of train_context : {}, length of train_response : {}, lebgth of trainA : {}".format(len(train_context),len(train_response),len(trainA)))

        candidates, _ = create_tensor(self.data_dir,'candidates.txt',self.word_idx)

        print("printing length of candidates : {}".format(len(candidates)))

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

        best_validation_accuracy = 0.0

        for t in range(1,self.epochs + 1) :

            print("Epoch# {}".format(t))
            np.random.shuffle(train_batches)
            total_train_cost = 0.0
            neg_samples = list()


            
            print("Calculating training cost")
            for start, end in tqdm(train_batches) :
                
                neg_train_response = np.array(train_response.tolist()[:max(0,start - 1)] + train_response.tolist()[min(n_train,end + 1):])
                neg_samples = new_neg_sampling_iter(neg_train_response,self.batch_size,self.negative_cand)
                for n in neg_samples :
                    c = train_context[start:end]
                    r = train_response[start:end]
                    train_loss = self.model.batch_fit(c,r,n)
                    total_train_cost += train_loss[0]

            #train_index = random.randint(0,len(train_context))
            #train_index_end = min(train_index + 100,len(train_context))
            train_index = 0
            train_index_end = len(train_context)

            train_preds = self.batch_predict(train_context[train_index:train_index_end],candidates)

            train_accuracy = metrics.accuracy_score(np.array(train_preds),trainA[train_index:train_index_end])
            train_fbeta_score = metrics.fbeta_score(np.array(train_preds),trainA[train_index:train_index_end],beta=9999,average='micro')

            total_train_cost /= (n_train*self.negative_cand)

            epoch_list.append(t)

            train_cost_list.append(total_train_cost)
            train_fbeta_list.append(train_fbeta_score)

            self.print_results(cost=total_train_cost,
                accuracy=train_accuracy,
                fbeta_score=train_fbeta_score,
                description="training")

            total_val_cost = 0.0
            
            print("Calculating validation cost")
            for start,end in tqdm(val_batches) :
                c = val_context[start:end]
                r = val_response[start:end]
                neg_val_response = np.array(val_response.tolist()[:max(0,start-1)] + val_response.tolist()[min(n_val,end + 1):])
                neg_samples = new_neg_sampling_iter(neg_val_response,self.batch_size,self.negative_cand)
                for n in neg_samples :
                    val_loss = self.model.batch_compute_loss(c,r,n)
                    total_val_cost += val_loss[0]

            total_val_cost /= (n_val*self.negative_cand)

            #val_index = random.randint(0,len(val_context))
            #val_index_end = min(val_index + 100,len(val_context))
            val_index = 0
            val_index_end = len(val_context)

            val_preds = self.batch_predict(val_context[val_index:val_index_end],candidates)

            val_accuracy = metrics.accuracy_score(np.array(val_preds),valA[val_index:val_index_end])
            val_fbeta_score = metrics.fbeta_score(np.array(val_preds),valA[val_index:val_index_end],beta=9999,average='micro')
           
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
            
            if t % self.evaluation_interval == 0 :

                train_acc_summary = tf.summary.scalar(os.path.join(self.description + '/','train_acc'),tf.constant(train_accuracy,dtype=tf.float32))
                val_acc_summary = tf.summary.scalar(os.path.join(self.description + '/','val_acc'),tf.constant(val_accuracy,dtype=tf.float32))
                merged_summary = tf.summary.merge([train_acc_summary,val_acc_summary])
                summary_str = self.session.run(merged_summary)
                self.summary_writer.add_summary(summary_str,t)
                self.summary_writer.flush()
                
                if val_accuracy > best_validation_accuracy :
                    best_validation_accuracy = val_accuracy
                    self.saver.save(self.session,os.path.join(self.model_dir,'model.ckpt'),global_step=t)

    def load_saved_model(self) :
        print("model directory : {}".format(self.model_dir))
        ckpt = tf.train.get_checkpoint_state(self.model_dir)

        if ckpt and ckpt.model_checkpoint_path :
            self.saver.restore(self.session,ckpt.model_checkpoint_path)
        else :
            print("...no checkpoint found...")

    def test(self) :

        self.load_saved_model()

        test_context,test_response = create_tensor(self.data_dir,'test_data.txt',self.word_idx)

        test_candidates, _ = create_tensor(self.data_dir,'candidates.txt',self.word_idx)

        print("shapes ")
        print(test_context.shape)
        print(test_response.shape)
        print(test_candidates.shape)

        n_test = len(test_context)

        print("len of test is : {}".format(n_test))

        _, _, self.testA = vectorize_data(self.testData,self.word_idx,self.sentence_size,self.batch_size,self.n_cand,self.memory_size)

        print("len of test answers : {}".format(len(self.testA)))


        #calculating test accuracy

        test_preds = self.batch_predict(test_context,test_candidates)
        print("length of test predictions : ".format(len(test_preds)))
        print("first 10 predictions : {}".format(test_preds[:10]))
        print("first 10 answers     : {}".format(self.testA[:10]))

        test_accuracy = metrics.accuracy_score(np.array(test_preds),self.testA)

        test_fbeta_score = metrics.fbeta_score(np.array(test_preds),self.testA,beta=9999,average='micro')

        
        test_batches = zip(range(0,n_test-self.batch_size,self.batch_size),range(self.batch_size,n_test,self.batch_size))
        test_batches = [(start,end) for start,end in test_batches]


        total_test_cost  = 0.0

        print("Calculating test cost")
        '''
        for start,end in tqdm(test_batches) :

            c = test_context[start:end]
            r = test_response[start:end]

            

            neg_test_response = np.array(test_response.tolist()[:max(0,start-1)] + test_response.tolist()[min(n_test,end + 1):])

            neg_samples = new_neg_sampling_iter(neg_test_response,self.batch_size,self.negative_cand)

            for n in neg_samples :

                total_test_loss = self.model.batch_compute_loss(c,r,n)
                total_test_cost += total_test_loss[0]

            total_test_cost /= (n_test*self.negative_cand)

        self.print_results(cost=total_test_cost,accuracy=test_accuracy,fbeta_score=test_fbeta_score,description="test")'''

        print("test accuracy is : {}\t".format(str(test_accuracy)))

    def batch_predict(self,train_context,train_response) :

        candidate_list = list()

        for i in tqdm(range(len(train_context))) :

            
            #print("printing shape of train_context[i]")
            #print(train_context[i:i+1].shape)
            #nh = input()
            context_repeat = np.repeat(train_context[i:i+1],train_response.shape[0],axis=0)
            #print("shape of context repeat is ==> {}".format(context_repeat.shape))
            #fr = input()

            '''print("printing shapes")
            print(train_context[i:i+1].shape)
            print(train_response.shape)
            print(context_repeat.shape)'''

            index = self.model.batch_predict(context_repeat,train_response)

            candidate_list.append(index)

        return candidate_list



if __name__ == '__main__' :

    model = SupervisedEmbeddingModel(embedding_size=FLAGS.embedding_size,
                                     random_seed=42,
                                     margin=FLAGS.margin,
                                     negative_cand=FLAGS.negative_cand,
                                     batch_size=FLAGS.batch_size,
                                     epochs=FLAGS.epochs,
                                     evaluation_interval=FLAGS.evaluation_interval,
                                     data_dir=FLAGS.data_dir,
                                     model_dir=FLAGS.model_dir,
                                     description="restaurant_domain")

    if FLAGS.train :
        model.train()

    model.test()




