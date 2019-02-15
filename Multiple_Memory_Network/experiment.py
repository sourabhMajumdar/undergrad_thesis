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


from MemoryNeuralNet import Multiple_Memory_Network
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
tf.flags.DEFINE_boolean('converse_later', False, 'if True, converse_later')
tf.flags.DEFINE_boolean('OOV', False, 'if True, use OOV test set')
tf.flags.DEFINE_boolean('pipeline_testing',False,'if True then we are testing the workings of the pipeline and not the actual result')
tf.flags.DEFINE_boolean('mult_oop',True,'If true then test for multiple OOP per example')
tf.flags.DEFINE_boolean('plot_progress',False,'If true then plot the plot_progress')
FLAGS = tf.flags.FLAGS

def test_my_model(model,test_cases,data_base,intent) :


    for test_case in test_cases :

        per_response_accuracy, per_dialog_accuracy, per_intent_accuracy = model.test_file(test_case)

        if test_case == None :
            test_case_tested = 'Simple'
        else :
            test_case_tested = test_case

        model_data = dict()
        model_data["Intent"] = intent
        model_data["Test Case"] = test_case_tested
                            
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


    #list_of_columns = ["Intent","Per-Response Accuracy","Per-Dialog Accuracy","Learning Rate","Batch Size","Embedding Size","Memory Size","Hops","Epochs"]

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
    "Hops"
    ]
    experiment_data_base = pd.DataFrame(columns=list_of_columns)
    learning_rate_list = [0.001,0.005,0.01]
    #learning_rate_list = [0.001]
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
    #dir_path = os.path.dirname(os.path.realpath(__file__))
    mult_oop_flag = FLAGS.mult_oop
    
    excel_file_sheet_name = 'mult_oop_{}'.format(str(mult_oop_flag))
    excel_file_name = 'Multiple_Memory_Network_Results_{}.xlsx'.format(excel_file_sheet_name)

    for learning_rate in learning_rate_list :
        for batch_size in batch_size_list :
            for embedding_size in embedding_size_list :
                for hops in hops_list :
                    for epochs in epochs_list :
                        for memory_size in memory_size_list :
                            
                            
                            unique_identifier = 'with_learning_rate_{}_batch_size_{}_embedding_size_{}_epochs_{}_memory_size_{}_hops_{}'.format(learning_rate,batch_size,embedding_size,epochs,memory_size,hops)
                            

                            '''Below is bunch of a dictionary that are associating various parameters associated with the various
                            memory networks used for this experiment'''
                            
                            name_list = [
                            "main_memory_network",
                            "transaction_memory_network",
                            "account_balance_memory_network",
                            "account_limit_memory_network",
                            "block_card_memory_network",
                            "cancel_transaction_memory_network",
                            "search_note_memory_network"
                            ]

                            data_dictionary = {
                            "main_memory_network" : "../data/start_data/",
                            "transaction_memory_network" : "../data/transaction_data/",
                            "account_balance_memory_network" : "../data/account_balance_data",
                            "account_limit_memory_network" : "../data/account_limit_data/",
                            "block_card_memory_network" : "../data/block_card_data",
                            "cancel_transaction_memory_network" : "../data/cancel_transaction_data",
                            "search_note_memory_network" : "../data/search_note_data/"
                            }

                            model_dictionary = {
                            "main_memory_network" : "../Multiple_Memory_Network/Multiple_Intent/All_Intent_{}/Main_Memory_Network_Model".format(unique_identifier),
                            "transaction_memory_network" : "../Multiple_Memory_Network/Multiple_Intent/All_Intent_{}/Transaction_Memory_Network_Model".format(unique_identifier),
                            "account_balance_memory_network" : "../Multiple_Memory_Network/Multiple_Intent/All_Intent_{}/Account_Balance_Memory_Network_Model".format(unique_identifier),
                            "account_limit_memory_network" : "../Multiple_Memory_Network/Multiple_Intent/All_Intent_{}/Account_Limit_Memory_Network_Model".format(unique_identifier),
                            "block_card_memory_network" : "../Multiple_Memory_Network/Multiple_Intent/All_Intent_{}/Block_Card_Memory_Network_Model".format(unique_identifier),
                            "cancel_transaction_memory_network" : "../Multiple_Memory_Network/Multiple_Intent/All_Intent_{}/Cancel_Transaction_Intent".format(unique_identifier),
                            "search_note_memory_network" : "../Multiple_Memory_Network/Multiple_Intent/All_Intent_{}/Search_Note_Memory_Network".format(unique_identifier)
                            }

                            description_dictionary = {
                            "main_memory_network" : "multiple_intent_main_memory_network",
                            "transaction_memory_network" : "multiple_intent_transaction_memory_network",
                            "account_balance_memory_network" : "multiple_intent_account_balance_memory_network",
                            "account_limit_memory_network" : "multiple_intent_account_limit_memory_network",
                            "block_card_memory_network" : "multiple_intent_block_card_memory_network",
                            "cancel_transaction_memory_network" : "multiple_intent_cancel_transaction_memory_network",
                            "search_note_memory_network" : "multiple_intent_search_note_memory_network"
                            }

                            # create the multiple memory network
                            mult_mem_network =  Multiple_Memory_Network(name_list=name_list,
                                                                        data_dict=data_dictionary,
                                                                        model_dir_dict=model_dictionary,
                                                                        test_directory="../data/special_data/test/",
                                                                        performance_directory="../Multiple_Memory_Network/Multiple_Intent/All_Intent_{}/Performance_Charts/".format(unique_identifier),
                                                                        converse_later=FLAGS.converse_later,
                                                                        OOV=FLAGS.OOV,
                                                                        memory_size=memory_size,
                                                                        random_state=FLAGS.random_state,
                                                                        batch_size=batch_size,
                                                                        learning_rate=learning_rate,
                                                                        epsilon=FLAGS.epsilon,
                                                                        max_grad_norm=FLAGS.max_grad_norm,
                                                                        evaluation_interval=FLAGS.evaluation_interval,
                                                                        hops=hops,
                                                                        epochs=epochs,
                                                                        embedding_size=embedding_size,
                                                                        description_dict=description_dictionary,
                                                                        pipeline_testing=FLAGS.pipeline_testing,
                                                                        mult_oop=mult_oop_flag,
                                                                        plot_progress=FLAGS.plot_progress)


                            if FLAGS.train :
                            	mult_mem_network.train()
                            

                            mult_mem_network_test_cases = [None,
                            "oot",
                            "turn_compression",
                            "turn_compression_oot",
                            "new_api",
                            "new_api_oot",
                            "re_order",
                            "re_order_oot",
                            "another_slot",
                            "another_slot_oot",
                            "audit_more",
                            "audit_more_oot"]

                            experiment_data_base = test_my_model(model=mult_mem_network,test_cases=mult_mem_network_test_cases,data_base=experiment_data_base,intent="All Intent")

                            mult_mem_network.close_session()


    excel_writer = pd.ExcelWriter(excel_file_name)
    experiment_data_base.to_excel(excel_writer,sheet_name=excel_file_sheet_name)
    excel_writer.save()
    excel_writer.close()
    
