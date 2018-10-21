from __future__ import absolute_import
from __future__ import print_function



from data_utils import load_dialog_task, vectorize_data, load_candidates, vectorize_candidates, vectorize_candidates_sparse, tokenize
from sklearn import metrics
from memn2n import MemN2NDialog
from itertools import chain
from six.moves import range, reduce
import sys
import tensorflow as tf
import numpy as np
import os
import matplotlib.pyplot as plt
import time
from tqdm import tqdm

from single_memory_network_model import SingleMemoryNetwork as Single_Memory_Network
tf.flags.DEFINE_float("learning_rate", 0.001,
                      "Learning rate for Adam Optimizer.")
tf.flags.DEFINE_float("epsilon", 1e-8, "Epsilon value for Adam Optimizer.")
tf.flags.DEFINE_float("max_grad_norm", 40.0, "Clip gradients to this norm.")
tf.flags.DEFINE_integer("evaluation_interval", 10,
                        "Evaluate and print results every x epochs")
tf.flags.DEFINE_integer("batch_size", 32, "Batch size for training.")
tf.flags.DEFINE_integer("hops", 3, "Number of hops in the Memory Network.")
tf.flags.DEFINE_integer("epochs", 200, "Number of epochs to train for.")
tf.flags.DEFINE_integer("embedding_size", 20,
                        "Embedding size for embedding matrices.")
tf.flags.DEFINE_integer("memory_size", 50, "Maximum size of memory.")

tf.flags.DEFINE_integer("random_state", None, "Random state.")
tf.flags.DEFINE_string("data_dir", "data/dialog-bAbI-tasks/",
                       "Directory containing bAbI tasks")
tf.flags.DEFINE_string("model_dir", "model/",
                       "Directory containing memn2n model checkpoints")
tf.flags.DEFINE_boolean('train', True, 'if True, begin to train')
tf.flags.DEFINE_boolean('converse_later', False, 'if True, converse after training')
tf.flags.DEFINE_boolean('OOV', False, 'if True, use OOV test set')
FLAGS = tf.flags.FLAGS



class Single_Memory_Model(object) :

    def __init__(self,data_dir,
                      model_dir,
                      validation_file,
                      performance_directory,
                      converse_later,
                      OOV,
                      memory_size,
                      random_state,
                      batch_size,
                      learning_rate,
                      epsilon,
                      max_grad_norm,
                      evaluation_interval,
                      hops,
                      epochs,
                      embedding_size,
                      description) :

        self.data_dir = data_dir
        self.model_dir = model_dir
        self.validation_file = validation_file
        self.performance_directory = performance_directory
        self.converse_later = converse_later
        self.OOV = OOV
        self.memory_size = memory_size
        self.random_state = random_state
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.epsilon = epsilon
        self.max_grad_norm = max_grad_norm
        self.evaluation_interval = evaluation_interval
        self.hops = hops
        self.epochs = epochs
        self.embedding_size = embedding_size
        self.description = description

        self.graph = tf.Graph()


        self.session = tf.Session(graph=self.graph)

        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        
        
        
        
        with self.graph.as_default() :

            self.model = Single_Memory_Network(data_dir=self.data_dir,
                                               model_dir=self.model_dir,
                                               performance_directory=self.performance_directory,
                                               converse_later=self.converse_later,
                                               OOV=self.OOV,
                                               memory_size=self.memory_size,
                                               random_state=self.random_state,
                                               batch_size=self.batch_size,
                                               learning_rate=self.learning_rate,
                                               epsilon=self.epsilon,
                                               max_grad_norm=self.max_grad_norm,
                                               evaluation_interval=self.evaluation_interval,
                                               hops=self.hops,
                                               epochs=self.epochs,
                                               embedding_size=self.embedding_size,
                                               description=self.description,
                                               session=self.session)
        

        self.validtion_file = validation_file
    def train(self) :

        print(" Training Model with description : {}".format(self.get_description()))
        with self.graph.as_default() :
            self.model.train()

    def test(self) :
        print(" Testing Model with description : {}".format(self.get_description()))
        with self.graph.as_default() :
            self.model.load_saved_model()
            story = list()
            nid = 1
            network_converse = self.model.predict_and_converse
            count_sentence = 0
            correct_sentence = 0
            correct_dialog = 0
            count_dialog = 1
            correct_dialog_track = True

            f_handle = open(self.validation_file)
            list_of_lines = f_handle.readlines()
            for line in tqdm(list_of_lines) :
                raw_line = line[2:].strip()
                if not raw_line :
                    story = list()
                    nid = 1
                    if correct_dialog_track :
                        correct_dialog += 1
                    correct_dialog_track = True
                    count_dialog += 1
                else :
                    count_sentence += 1
                    utterances = raw_line.split('\t')
                    user_utterance = utterances[0]
                    bot_utterance = utterances[1]
                    bot_response, story, nid = network_converse(story,user_utterance,nid,bot_utterance)
                    if bot_response.strip() == bot_utterance :
                        correct_sentence += 1
                    else :
                        correct_dialog_track = False
            print("percentage of correct sentences : {}".format(float(correct_sentence)/count_sentence))
            print("percentage of correct dialogs : {}".format(float(correct_dialog)/count_dialog))

    def dialog_analysis(self,file_directory="Analysis_Directory/",file_name="Analysis.txt") :
        
        print(" Analysing Dialogs for Model description : {}".format(self.get_description()))
        
        if not os.path.exists(file_directory) :
            os.makedirs(file_directory)

        file_handle = open(os.path.join(file_directory,file_name),'w')

        with self.graph.as_default() :
            self.model.load_saved_model()
            story = list()

            analysis_story = list()
            nid = 1
            network_converse = self.model.predict_and_converse
            count_sentence = 0
            correct_sentence = 0
            correct_dialog = 0
            count_dialog = 0
            error_count = 0
            api_error = 0
            non_api_error = 0
            correct_dialog_track = True

            f_handle = open(self.validation_file)
            
            list_of_lines = f_handle.readlines()
            for line in tqdm(list_of_lines) :
                
                raw_line = line[2:].strip()
                if not raw_line :
                    story = list()
                    nid = 1
                    analysis_story = list()
                    if correct_dialog_track :
                        correct_dialog += 1
                    correct_dialog_track = True
                    count_dialog += 1
                else :
                    count_sentence += 1
                    utterances = raw_line.split('\t')
                    user_utterance = utterances[0]
                    bot_utterance = utterances[1]
                    bot_response, story, nid = network_converse(story,user_utterance,nid,bot_utterance)
                    if bot_response.strip() != bot_utterance :
                        error_count += 1
                        if "api_call" in bot_utterance and "api_call" in bot_response :
                            api_error += 1
                        else :
                            non_api_error +=1
                        correct_dialog_track = False
                        
                        file_handle.write("Story is :\n")
                        for l in analysis_story :
                            file_handle.write("{}\n".format(l))
                        file_handle.write("\n")
                        file_handle.write("User Utterance : {}\n".format(user_utterance))
                        file_handle.write("Bot Utterance (expected) : {}\n".format(bot_utterance))
                        file_handle.write("Bot Utterance (predicted) : {}\n\n".format(bot_response))
                    

                    analysis_story.append("User >> {} || Bot >> {} \n".format(user_utterance,bot_utterance))

        print("Number of api error's = {}/{}".format(str(api_error),str(error_count)))
        print("Number of non api error's = {}/{}".format(str(non_api_error),str(error_count)))

        file_handle.close()


    def get_description(self) :
        return self.description
    def close_session(self) :
        self.model.close_session()

if __name__ == '__main__':
    

    restaurant_model = Single_Memory_Model(data_dir="../data/one_data_restaurant_domain/", 
                        model_dir="restaurant_domain_memory_network/",
                        validation_file="../data/one_data_restaurant_domain/test_data.txt",
                        performance_directory="../Performance_Charts/", 
                        converse_later=FLAGS.converse_later,    
                        OOV=FLAGS.OOV,
                        memory_size=FLAGS.memory_size,
                        random_state=FLAGS.random_state,
                        batch_size=FLAGS.batch_size,
                        learning_rate=FLAGS.learning_rate,
                        epsilon=FLAGS.epsilon,
                        max_grad_norm=FLAGS.max_grad_norm,
                        evaluation_interval=FLAGS.evaluation_interval,
                        hops=FLAGS.hops,
                        epochs=FLAGS.epochs,
                        embedding_size=FLAGS.embedding_size,
                        description="restaurant_memory_network")

    transaction_model = Single_Memory_Model(data_dir="../data/transaction_data/", 
                        model_dir="transaction_memory_network/",
                        validation_file="../data/transaction_data/val_data.txt",
                        performance_directory="../Performance_Charts/",
                        converse_later=FLAGS.converse_later,    
                        OOV=FLAGS.OOV,
                        memory_size=FLAGS.memory_size,
                        random_state=FLAGS.random_state,
                        batch_size=FLAGS.batch_size,
                        learning_rate=FLAGS.learning_rate,
                        epsilon=FLAGS.epsilon,
                        max_grad_norm=FLAGS.max_grad_norm,
                        evaluation_interval=FLAGS.evaluation_interval,
                        hops=FLAGS.hops,
                        epochs=FLAGS.epochs,
                        embedding_size=FLAGS.embedding_size,
                        description="transaction_memory_network")


    account_balance_model = Single_Memory_Model(data_dir="../data/account_balance_data/", 
                        model_dir="account_balance_memory_network/",
                        validation_file="../data/account_balance_data/val_data.txt",
                        performance_directory="../Performance_Charts/",
                        converse_later=FLAGS.converse_later,    
                        OOV=FLAGS.OOV,
                        memory_size=FLAGS.memory_size,
                        random_state=FLAGS.random_state,
                        batch_size=FLAGS.batch_size,
                        learning_rate=FLAGS.learning_rate,
                        epsilon=FLAGS.epsilon,
                        max_grad_norm=FLAGS.max_grad_norm,
                        evaluation_interval=FLAGS.evaluation_interval,
                        hops=FLAGS.hops,
                        epochs=FLAGS.epochs,
                        embedding_size=FLAGS.embedding_size,
                        description="account_balance_memory_network")


    transaction_history_model = Single_Memory_Model(data_dir="../data/transaction_history_data/", 
                        model_dir="transaction_history_memory_network/",
                        validation_file="../data/transaction_history_data/val_data.txt",
                        performance_directory="../Performance_Charts/" ,
                        converse_later=FLAGS.converse_later,    
                        OOV=FLAGS.OOV,
                        memory_size=FLAGS.memory_size,
                        random_state=FLAGS.random_state,
                        batch_size=FLAGS.batch_size,
                        learning_rate=FLAGS.learning_rate,
                        epsilon=FLAGS.epsilon,
                        max_grad_norm=FLAGS.max_grad_norm,
                        evaluation_interval=FLAGS.evaluation_interval,
                        hops=FLAGS.hops,
                        epochs=FLAGS.epochs,
                        embedding_size=FLAGS.embedding_size,
                        description="transaction_history_memory_network")

    all_intent_model = Single_Memory_Model(data_dir="../data/one_data/", 
                        model_dir="all_intent_memory_network/",
                        validation_file="../data/one_data/val_data.txt",
                        performance_directory="../Performance_Charts/" ,
                        converse_later=FLAGS.converse_later,    
                        OOV=FLAGS.OOV,
                        memory_size=FLAGS.memory_size,
                        random_state=FLAGS.random_state,
                        batch_size=FLAGS.batch_size,
                        learning_rate=FLAGS.learning_rate,
                        epsilon=FLAGS.epsilon,
                        max_grad_norm=FLAGS.max_grad_norm,
                        evaluation_interval=FLAGS.evaluation_interval,
                        hops=FLAGS.hops,
                        epochs=FLAGS.epochs,
                        embedding_size=FLAGS.embedding_size,
                        description="all_intent_memory_network")


    # chatbot.run()
    if FLAGS.train:
        restaurant_model.train()
        time.sleep(10)
        transaction_model.train()
        time.sleep(10)
        account_balance_model.train()
        time.sleep(10)
        transaction_history_model.train()
        time.sleep(10)
        all_intent_model.train()

    print("Testing All Single Memory Networks ")
    
    restaurant_model.test()
    
    transaction_model.test()
    
    account_balance_model.test()
    
    transaction_history_model.test()
    
    all_intent_model.test()
    
    
    restaurant_model.dialog_analysis(file_directory="Restaurant_Data_Analysis/",file_name="restaurant_analysis.txt")
    
    transaction_model.dialog_analysis(file_directory="Transaction_Data_Analysis/",file_name="transaction_analysis.txt")
    
    account_balance_model.dialog_analysis(file_directory="Account_Balance_Data_Analysis/",file_name="account_balance_analysis.txt")
    
    transaction_history_model.dialog_analysis(file_directory="Transaction_History_Data_Analysis/",file_name="transaction_history_analysis.txt")
    
    all_intent_model.dialog_analysis(file_directory="All_Intent_Data_Analysis",file_name="all_intent_analysis.txt")



    restaurant_model.close_session()
    transaction_model.close_session()
    account_balance_model.close_session()
    transaction_history_model.close_session()
    all_intent_model.close_session()
