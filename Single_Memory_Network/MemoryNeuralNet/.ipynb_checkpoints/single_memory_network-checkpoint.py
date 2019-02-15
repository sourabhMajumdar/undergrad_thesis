from __future__ import absolute_import
from __future__ import print_function



from .data_utils import load_dialog_task, vectorize_data, load_candidates, vectorize_candidates, vectorize_candidates_sparse, tokenize
from sklearn import metrics

from itertools import chain
from six.moves import range, reduce
from nltk.translate.bleu_score import sentence_bleu

import sys
import tensorflow as tf
import numpy as np
import os
import matplotlib.pyplot as plt
import time
from tqdm import tqdm

from .single_memory_network_model import SingleMemoryNetwork as Single_Memory_Network
import glob

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
            print("Created memory network : {}".format(self.description))
        
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

            test_directory = os.path.join(self.data_dir,'test/')

            for file_name in glob.glob(test_directory + 'test_data_*.txt') :

                print("file using {}".format(file_name))

                f_handle = open(file_name)
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
                        #print("Raw line is : {}".format(raw_line))
                        utterances = raw_line.split('\t')
                        user_utterance = utterances[0]
                        bot_utterance = utterances[1]
                        bot_response, story, nid = network_converse(story,user_utterance,nid,bot_utterance)
                        if bot_response.strip() == bot_utterance :
                            correct_sentence += 1
                        else :
                            correct_dialog_track = False

                per_response_accuracy = float(correct_sentence)/count_sentence
                per_dialog_accuracy = float(correct_dialog)/count_dialog
                print("{} percentage of correct sentences : {}".format(file_name,per_response_accuracy))
                print("{} percentage of correct dialogs : {}".format(file_name,per_dialog_accuracy))

            return per_response_accuracy, per_dialog_accuracy
        
        
    def test_file(self,test_case) :
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

            test_directory = os.path.join(self.data_dir,'test/')
            
            test_file_name = 'test_data_{}.txt'.format(test_case)
            
            file_name = os.path.join(test_directory,test_file_name)
            
            f_handle = open(file_name)
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
                    #print("Raw line is : {}".format(raw_line))
                    utterances = raw_line.split('\t')
                    user_utterance = utterances[0]
                    bot_utterance = utterances[1]
                    bot_response, story, nid = network_converse(story,user_utterance,nid,bot_utterance)
                    if bot_response.strip() == bot_utterance :
                        correct_sentence += 1
                    else :
                        correct_dialog_track = False

            per_response_accuracy = float(correct_sentence)/count_sentence
            per_dialog_accuracy = float(correct_dialog)/count_dialog
            print("{} percentage of correct sentences : {}".format(file_name,per_response_accuracy))
            print("{} percentage of correct dialogs : {}".format(file_name,per_dialog_accuracy))

        return per_response_accuracy, per_dialog_accuracy

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
            api_bleu_score = 0.0
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
                            tok_bot_utterance = tokenize(bot_utterance)
                            tok_bot_response = tokenize(bot_response)
                            api_bleu_score += sentence_bleu([tok_bot_utterance],tok_bot_response)
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

        if api_error == 0 :
            print("Congrat's no api_error")
        else :
            print("Number of api error's = {}/{}, Avg api_bleu score = {}".format(str(api_error),str(error_count),str(float(api_bleu_score)/api_error)))
        print("Number of non api error's = {}/{}".format(str(non_api_error),str(error_count)))

        file_handle.close()


    def get_description(self) :
        return self.description
    def close_session(self) :
        self.model.close_session()

