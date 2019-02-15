from __future__ import absolute_import
from __future__ import print_function


from sklearn import metrics

from itertools import chain
from six.moves import range, reduce
import sys
import tensorflow as tf
import numpy as np
import os
import time
import matplotlib.pyplot as plt
from tqdm import tqdm

from .multiple_memory_model import MultipleMemoryModel as Multiple_Memory_Model


class Multiple_Memory_Network(object) :

    def __init__(self,name_list,
                      data_dict,
                      model_dir_dict,
                      test_directory,
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
                      description_dict) :

        self.name_list = name_list
        self.data_dict = data_dict
        self.model_dir_dict = model_dir_dict
        self.test_directory = test_directory
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

    def test_file(self,test_case=None) :


        self.load_saved_model()
        print("loaded saved model")
        story = []
        nid = 1
        network_converse = self.network_dict["main_memory_network"][0]
        network_graph = self.network_dict["main_memory_network"][1]
        count_sentence = 0
        correct_sentence = 0
        correct_dialog = 0
        count_dialog = 0

        name_of_test_file = 'test_data_{}.txt'.format(test_case)
        file_name = os.path.join(self.test_directory,name_of_test_file)

        f_handle = open(file_name)
        #print("opened validation file :{}".format(self.validation_file))
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
                network_converse = self.network_dict["main_memory_network"][0]
                network_graph = self.network_dict["main_memory_network"][1]
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
            

        per_response_accuracy = float(correct_sentence)/count_sentence
        per_dialog_accuracy = float(correct_dialog)/count_dialog
        print("percentage of correct sentences : {}".format(per_response_accuracy))
        print("percentage of correct dialogs : {}".format(per_dialog_accuracy))

        return per_response_accuracy, per_dialog_accuracy
    
    def test(self) :


        self.load_saved_model()
        print("loaded saved model")
        story = []
        nid = 1
        network_converse = self.network_dict["main_memory_network"][0]
        network_graph = self.network_dict["main_memory_network"][1]
        count_sentence = 0
        correct_sentence = 0
        correct_dialog = 0
        count_dialog = 0

        special_test_path = 'special_' + self.data_dir
        test_directory = os.path.join(special_test_path,'test/')

        for file_name in glob.glob(test_directory + 'test_data_*.txt') :
            print("file using \t:{}".format(file_name))

            f_handle = open(file_name)
            #print("opened validation file :{}".format(self.validation_file))
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
                    network_converse = self.network_dict["main_memory_network"][0]
                    network_graph = self.network_dict["main_memory_network"][1]
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
                

            per_response_accuracy = float(correct_sentence)/count_sentence
            per_dialog_accuracy = float(correct_dialog)/count_dialog
            print("percentage of correct sentences : {}".format(per_response_accuracy))
            print("percentage of correct dialogs : {}".format(per_dialog_accuracy))

        return per_response_accuracy, per_dialog_accuracy


    def dialog_analysis(self,file_directory="Analysis_Directory",file_name="Analysis.txt") :


        self.load_saved_model()
        
        if not os.path.exists(file_directory) :
            os.makedirs(file_directory)


        story = []
        analysis_story = list()
        nid = 1
        network_converse = self.network_dict["main_memory_network"][0]
        network_graph = self.network_dict["main_memory_network"][1]
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
                network_converse = self.network_dict["main_memory_network"][0]
                network_graph = self.network_dict["main_memory_network"][1]
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







    





