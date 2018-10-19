from __future__ import absolute_import
from __future__ import print_function

from data_utils import load_dialog_task, vectorize_data, load_candidates, vectorize_candidates, vectorize_candidates_sparse, tokenize , write_candidates
from sklearn import metrics
from memn2n import MemN2NDialog
from itertools import chain
from six.moves import range, reduce
import sys
import tensorflow as tf
import numpy as np
import os
import time
import matplotlib.pyplot as plt
from tqdm import tqdm

from multiple_memory_model import MultipleMemoryModel as Multiple_Memory_Model
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
tf.flags.DEFINE_boolean('converse_later', False, 'if True, converse_later')
tf.flags.DEFINE_boolean('OOV', False, 'if True, use OOV test set')
FLAGS = tf.flags.FLAGS



class Multiple_Memory_Network(object) :

    def __init__(self,name_list,
                      data_dict,
                      model_dir_dict,
                      validation_file,
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
                      description_dict) :

        self.name_list = name_list
        self.data_dict = data_dict
        self.model_dir_dict = model_dir_dict
        self.validation_file = validation_file
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
        self.description_dict = description_dict

        self.graph_dict = dict()
        self.session_dict = dict()
        self.model_dict = dict()
        self.network_dict = dict()
        
        self.max_memory_size = -9999
        self.max_sentence_size = -9999

        for name in self.name_list :
            self.graph_dict[name] = tf.Graph()
            self.session_dict[name] = tf.Session(graph=self.graph_dict[name])
            
            if not os.path.exists(self.model_dir_dict[name]) :
                os.makedirs(self.model_dir_dict[name])
            with self.graph_dict[name].as_default() :
                self.model_dict[name] = Multiple_Memory_Model(data_dir=data_dict[name], 
                        model_dir=model_dir_dict[name],
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
                        session=self.session_dict[name],
                        description=self.description_dict[name])
                self.max_memory_size = max(self.max_memory_size,self.model_dict[name].get_memory_size())
                self.max_sentence_size = max(self.max_sentence_size,self.model_dict[name].get_sentence_size())
            
        #for name in self.name_list :
            

    def train(self) :
        for name in self.name_list :
            print("attempting to create the train model {}".format(name))
            with self.graph_dict[name].as_default() :
                
                self.model_dict[name].set_memory_size(self.max_memory_size)
                self.model_dict[name].set_sentence_size(self.max_sentence_size) 
                self.model_dict[name].build_model()
                self.model_dict[name].train()
                print("trained model name : {}".format(name))
                self.network_dict[name] = [self.model_dict[name].predict_and_converse,self.graph_dict[name]]
        print("all models created successfully !!")
                

    def load_saved_model(self) :
        print("trying to load saved model")
        for name,model in self.model_dict.items() :
            print("attempting to load model name : {}".format(name))
            with self.graph_dict[name].as_default() :
                self.model_dict[name].load_saved_model()
            print("successfully loaded model : {}".format(name))

    def test(self) :


        self.load_saved_model()
        print("loaded saved model")
        story = []
        nid = 1
        network_converse = self.network_dict["main"][0]
        network_graph = self.network_dict["main"][1]
        count_sentence = 0
        correct_sentence = 0
        correct_dialog = 0
        count_dialog = 0
        f_handle = open(self.validation_file)
        print("opened validation file :{}".format(self.validation_file))
        list_of_lines = f_handle.readlines()
        correct_dialog_track = True
        for line in tqdm(list_of_lines) :
            raw_line = line[2:].strip()
            if not raw_line :
                story = []
                nid = 1
                if correct_dialog_track :
                    correct_dialog += 1
                correct_dialog_track = True
                count_dialog += 1
                network_converse = self.network_dict["main"][0]
                network_graph = self.network_dict["main"][1]
                #print("end of dialog : {}".format(count_dialog))
            else :
                count_sentence += 1
                utterances = raw_line.split('\t')
                user_utterance = utterances[0]
                bot_utterance = utterances[1]
                #print("type of story before : {}".format(type(story)))
                with network_graph.as_default() :

                    bot_response, story, nid = network_converse(story,user_utterance,nid,bot_utterance)

                    if "mem_call" in bot_utterance :
                        words = bot_utterance.strip().split(":")
                        #print("memory network switched to : {}".format(words[1]))
                        network_graph = self.network_dict[words[1]][1]
                        network_converse = self.network_dict[words[1]][0]

                    #print("type of story after prediction : {}".format(type(story)))
                    #print("bot response is : {}".format(bot_response))
                    if bot_response.strip() == bot_utterance.strip() :
                        correct_sentence += 1
                    else :
                        correct_dialog_track = False
                

        print("percentage of correct sentences : {}".format(float(correct_sentence)/count_sentence))
        print("percentage of correct dialogs : {}".format(float(correct_dialog)/count_dialog))


    def dialog_analysis(self,file_directory="Analysis_Directory",file_name="Analysis.txt") :


        self.load_saved_model()
        
        if not os.path.exists(file_directory) :
            os.makedirs(file_directory)


        story = []
        analysis_story = list()
        nid = 1
        network_converse = self.network_dict["main"][0]
        network_graph = self.network_dict["main"][1]
        count_sentence = 0
        correct_sentence = 0
        correct_dialog = 0
        count_dialog = 0
        f_handle = open(self.validation_file)
        file_handle = open(os.path.join(file_directory,file_name),'w')
        list_of_lines = f_handle.readlines()
        correct_dialog_track = True
        for line in tqdm(list_of_lines) :
            raw_line = line[2:].strip()
            if not raw_line :
                story = []
                nid = 1
                if correct_dialog_track :
                    correct_dialog += 1
                analysis_story = list()
                correct_dialog_track = True
                count_dialog += 1
                network_converse = self.network_dict["main"][0]
                network_graph = self.network_dict["main"][1]
                #print("end of dialog : {}".format(count_dialog))
            else :
                count_sentence += 1
                utterances = raw_line.split('\t')
                user_utterance = utterances[0]
                bot_utterance = utterances[1]
                #print("type of story before : {}".format(type(story)))
                with network_graph.as_default() :

                    bot_response, story, nid = network_converse(story,user_utterance,nid,bot_utterance)

                    if "mem_call" in bot_utterance :
                        words = bot_utterance.strip().split(":")
                        #print("memory network switched to : {}".format(words[1]))
                        network_graph = self.network_dict[words[1]][1]
                        network_converse = self.network_dict[words[1]][0]

                    #print("type of story after prediction : {}".format(type(story)))
                    #print("bot response is : {}".format(bot_response))
                    if bot_response.strip() != bot_utterance.strip() :
                        file_handle.write("Story is : \n")
                        for l in analysis_story :
                            file_handle.write("{}\n".format(l))
                        file_handle.write("\n")
                        file_handle.write("User Utterance is {}\n".format(user_utterance))
                        file_handle.write("Bot Utterance (expected) : {}\n".format(bot_utterance))
                        file_handle.write("Bot Utternace (predicted) : {}\n\n".format(bot_response))

                    analysis_story.append(raw_line)
        file_handle.close()


    def close_session(self) :
        for name in self.name_list :
            self.model_dict[name].close_session()


if __name__ == '__main__':
    
    
    name_list = ["main","transaction","account_balance","transaction_history"]

    data_dictionary = {"main" : "../data/start_data/", "transaction" : "../data/transaction_data/", "account_balance" : "../data/account_balance_data", "transaction_history" : "../data/transaction_history_data/"}

    model_dictionary = {"main" : "../Multiple_Memory_Network/main_memory_network", "transaction" : "../Multiple_Memory_Network/transaction_memory_network", "account_balance" : "../Multiple_Memory_Network/account_balance_memory_network", "transaction_history" : "../Multiple_Memory_Network/transaction_history_memory_network"}

    description_dictionary = {"main" : "main_memory_network", "transaction" : "transaction_memory_network", "account_balance" : "account_balance_memory_network", "transaction_history" : "transaction_history_memory_network"}
    mult_mem_network =  Multiple_Memory_Network(name_list=name_list,
                      data_dict=data_dictionary,
                      model_dir_dict=model_dictionary,
                      validation_file="../data/special_data/val_data.txt",
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
                      description_dict=description_dictionary)

    transaction_name_list = ["main","transaction"]
    transaction_data_dictionary = {"main" : "../data/start_data/", "transaction" : "../data/transaction_data/"}
    transaction_model_dictionary = {"main" : "../Multiple_Memory_Network/main_memory_network_transaction_only", "transaction" : "../Multiple_Memory_Network/transaction_memory_network_transaction_only"}
    transaction_description_dictionary = {"main" : "main_memory_network_transaction_only", "transaction" : "transaction_memory_network_transaction_only"}


    mult_transaction_memory_network = Multiple_Memory_Network(name_list=transaction_name_list,
                      data_dict=transaction_data_dictionary,
                      model_dir_dict=transaction_model_dictionary,
                      validation_file="../data/special_transaction_data/val_data.txt",
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
                      description_dict=transaction_description_dictionary)


    account_balance_name_list = ["main","account_balance"]
    account_balance_data_dictionary = {"main" : "../data/start_data","account_balance": "../data/account_balance_data/"}
    account_balance_model_dictionary = {"main" : "../Multiple_Memory_Network/main_memory_network_account_balance_only","account_balance" : "../Multiple_Memory_Network/account_balance_memory_network_account_balance_only"}
    account_balance_description_dictionary = {"main" : "main_memory_network_account_balance_only","account_balance" : "account_balance_memory_network_account_balance_only"}

    mult_account_balance_memory_network = Multiple_Memory_Network(name_list=account_balance_name_list,
                      data_dict=account_balance_data_dictionary,
                      model_dir_dict=account_balance_model_dictionary,
                      validation_file="../data/special_account_balance_data/val_data.txt",
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
                      description_dict=account_balance_description_dictionary)

    transaction_history_name_list = ["main","transaction_history"]
    transaction_history_data_dictionary = {"main" : "../data/start_data/", "transaction_history" : "../data/transaction_history_data/"}
    transaction_history_model_dictionary = {"main" : "../Multiple_Memory_Network/main_memory_network_transaction_history_only", "transaction_history" : "../Multiple_Memory_Network/transaction_history_memory_network_transaction_history_only"}
    transaction_history_description_dictionary = {"main" : "main_memory_network_transaction_history_only", "transaction_history" : "transaction_history_memory_network_transaction_history_only"}

    mult_transaction_history_memory_network = Multiple_Memory_Network(name_list=transaction_history_name_list,
                      data_dict=transaction_history_data_dictionary,
                      model_dir_dict=transaction_history_model_dictionary,
                      validation_file="../data/special_transaction_history_data/val_data.txt",
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
                      description_dict=transaction_history_description_dictionary)


    
    
	
    if FLAGS.train :
        mult_mem_network.train()
        mult_transaction_memory_network.train()
        mult_account_balance_memory_network.train()
        mult_transaction_history_memory_network.train()

    mult_mem_network.test()	
    mult_transaction_memory_network.test()
    mult_account_balance_memory_network.test()
    mult_transaction_history_memory_network.test()

    mult_mem_network.dialog_analysis(file_directory="All_Intent_Analysis/",file_name="all_intents_analysis.txt")
    mult_transaction_memory_network.dialog_analysis(file_directory="Transaction_Intent_Only_Analysis/",file_name="transaction_intent_analysis.txt")
    mult_account_balance_memory_network.dialog_analysis(file_directory="Account_Balance_Intent_Analysis/",file_name="account_balance_intent_analysis.txt")
    mult_transaction_history_memory_network.dialog_analysis(file_directory="Transaction_History_Intent_Analysis/",file_name="transaction_history_analysis.txt")
    #chatbot.close_session()
    mult_mem_network.close_session()
    mult_transaction_memory_network.close_session()
    mult_account_balance_memory_network.close_session()
    mult_transaction_history_memory_network.close_session()
    




    





