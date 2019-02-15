from __future__ import absolute_import
from __future__ import print_function




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

from tf_idf_class_model import TF_IDF_MODEL

import pandas as pd
import glob

tf.flags.DEFINE_float("epsilon", 1e-8, "Epsilon value for Adam Optimizer.")
tf.flags.DEFINE_float("max_grad_norm", 40.0, "Clip gradients to this norm.")
tf.flags.DEFINE_integer("evaluation_interval", 10,
                        "Evaluate and print results every x epochs")






tf.flags.DEFINE_integer("random_state", None, "Random state.")
tf.flags.DEFINE_string("data_dir", "data/dialog-bAbI-tasks/",
                       "Directory containing bAbI tasks")
tf.flags.DEFINE_string("model_dir", "model/",
                       "Directory containing memn2n model checkpoints")
tf.flags.DEFINE_boolean('train', True, 'if True, begin to train')
tf.flags.DEFINE_boolean('converse_later', False, 'if True, converse after training')
tf.flags.DEFINE_boolean('OOV', False, 'if True, use OOV test set')
tf.flags.DEFINE_boolean('pipeline_testing',False,'if True then we are testing the workings of the pipeline and not the actual result')
tf.flags.DEFINE_boolean('mult_oop',True,'If True then test for multiple Out of Pattern')
FLAGS = tf.flags.FLAGS


def test_my_model(model,test_cases,data_base,intent) :


    for test_case in test_cases :

        per_response_accuracy, per_dialog_accuracy, per_intent_accuracy = model.test_file(test_case)

        model_data = dict()
        model_data["Intent"] = intent
        model_data["Test Case"] = test_case
                            
        model_data["Per-Response Accuracy"] = per_response_accuracy
        model_data["Per-Dialog Accuracy"] = per_dialog_accuracy
        model_data["Per-Intent Accuracy"] = per_intent_accuracy
                            
        model_data["Learning Rate"] = learning_rate
        model_data["Batch Size"] = batch_size
        model_data["Embedding Size"] = embedding_size
        model_data["Memory Size"] = memory_size
        model_data["Hops"] = hops
        model_data["Epochs"] = epochs

        data_base = data_base.append(model_data,ignore_index=True)

    return data_base
if __name__ == '__main__':
    


    list_of_columns = [
    "Intent",
    "Test Case",
    "Per-Response Accuracy",
    "Per-Dialog Accuracy",
    "Per-Intent Accuracy",
    "Learning Rate",
    "Batch Size",
    "Embedding Size",
    "Memory Size",
    "Hops",
    "Epochs"
    ]


    experiment_data_base = pd.DataFrame(columns=list_of_columns)

    #learning_rate_list = [0.001,0.003,0.01,0.03,0.1,0.3,1,3,10]
    learning_rate_list = [0.001]
    #batch_size_list = [2,4,8,16,32,64,128,256,512,1024]
    batch_size_list = [32]
    #embedding_size_list = [2,4,6,8,16,32,64,128,256,512,1024]
    embedding_size_list = [128]
    #memory_size_list = [10,20,40,80,160,320,640,1280]
    memory_size_list = [40]
    #hops_list = [1,2,4,8,16,32]
    hops_list = [3]
    #epochs_list = [10,20,40,80,160,320]
    epochs_list = [20]
    dir_path = os.path.dirname(os.path.realpath(__file__))

    
    excel_file_sheet_name = 'mult_oop_{}'.format(str(mult_oop_flag))
    excel_file_name = 'TF_IDF_Model_Results_{}.xlsx'.format(excel_file_sheet_name)

    for learning_rate in learning_rate_list :
        for batch_size in batch_size_list :
            for embedding_size in embedding_size_list :
                for hops in hops_list :
                    for epochs in epochs_list :
                        for memory_size in memory_size_list :

                            unique_identifier = "with_learning_rate_{}_batch_size_{}_embedding_size_{}_memory_size_{}_hops_{}_epochs_{}".format(learning_rate,batch_size,embedding_size,memory_size,hops,epochs)


                            restaurant_model = TF_IDF_MODEL(data_dir=os.path.join(dir_path,"../data/one_data_restaurant_domain/"), 
                                                                   model_dir=os.path.join(dir_path,"../Single_Memory_Network/Single_Intent/Restaurant_Intent_{}/Memory_Network_Model/".format(unique_identifier)),
                                                                   description="restaurant_memory_network",
                                                                   mult_oop=FLAGS.mult_oop,
                                                                   pipeline_testing=FLAGS.pipeline_testing)

                            

                            

                            if FLAGS.train :

                              restaurant_model.train()


                            # Testing for the simple test case

                            test_cases = [None]
                            experiment_data_base = test_my_model(model=restaurant_model,test_cases=test_cases,data_base=experiment_data_base,intent="Restaurant Intent")

                            # Un-Comment the code below to see the analysis of where the bot makes mistakes
                            #restaurant_model.dialog_analysis(file_directory="../Single_Memory_Network/Single_Intent/Restaurant_Intent_{}/Analysis".format(unique_identifier),file_name="analysis.txt")

                            


                            

    excel_writer_single_memory_network = pd.ExcelWriter("Experiment_Results.xlsx")

    experiment_data_base.to_excel(excel_writer_single_memory_network,sheet_name="Results")
    excel_writer_single_memory_network.save()
    excel_writer_single_memory_network.close()

