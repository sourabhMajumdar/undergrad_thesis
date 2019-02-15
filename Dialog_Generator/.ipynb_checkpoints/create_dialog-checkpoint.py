from utils import *

from Bot.transaction_bot import Transaction_bot
from Bot.account_bot import Account_bot
from Bot.transaction_history_bot import Transaction_history_bot

from User.transaction_user import Transaction_user
from User.account_user import Account_user
from User.transaction_history_user import Transaction_history_user

import numpy as np # no use until now
import random # used for random sampling of values where applicable
import math # no use untill now
import pandas as pd # to read the excel file 
import os # to carry os operations

transaction_templates_train , transaction_templates_val = make_templates(file_name="templates_for_dialogue_self_play.xlsx",
                                                                         sheet_name="MAKE_TRANSACTION",
                                                                         previous_dictionary_train=None,
                                                                         previous_dictionary_val=None)

account_balance_templates_train , account_balance_templates_val = make_templates(file_name="templates_for_dialogue_self_play.xlsx",
                                                                                 sheet_name="ACCOUNT_BALANCE",
                                                                                 previous_dictionary_train=None,
                                                                                 previous_dictionary_val=None)

transaction_history_templates_train , transaction_history_templates_val = make_templates(file_name="templates_for_dialogue_self_play.xlsx",
                                                                                         sheet_name="TRANS_HISTORY",
                                                                                         previous_dictionary_train=None,
                                                                                         previous_dictionary_val=None)


transaction_dialogs_train , transaction_dialogs_val = create_dialogs(User=Transaction_user,
                                                                     Bot=Transaction_bot,
                                                                     number_of_dialogs=500,
                                                                     dialog_templates_train=transaction_templates_train,
                                                                     dialog_templates_val=transaction_templates_val)
print("length of training transaction dialogs :{}".format(str(len(transaction_dialogs_train))))
print("length of validation transaction dialogs :{}".format(str(len(transaction_dialogs_val))))

account_dialogs_train , account_dialogs_val = create_dialogs(User=Account_user,
                                       Bot=Account_bot,
                                       number_of_dialogs=500,
                                       dialog_templates_train=account_balance_templates_train,
                                       dialog_templates_val=account_balance_templates_val)

print("length of training account dialogs :{}".format(str(len(account_dialogs_train))))
print("length of validation account dialogs :{}".format(str(len(account_dialogs_val))))

transaction_history_dialogs_train , transaction_history_dialogs_val = create_dialogs(User=Transaction_history_user,
                                                                                     Bot=Transaction_history_bot,
                                                                                     number_of_dialogs=500,
                                                                                     dialog_templates_train=transaction_history_templates_train,
                                                                                     dialog_templates_val=transaction_history_templates_val)

print("length of training transaction history dialogs :{}".format(str(len(account_dialogs_train))))
print("length of validation transaction history dialogs :{}".format(str(len(account_dialogs_val))))

dialogs_train = list()
dialogs_train.extend(transaction_dialogs_train)
dialogs_train.extend(account_dialogs_train)
dialogs_train.extend(transaction_history_dialogs_train)

dialogs_val = list()
dialogs_val.extend(transaction_dialogs_val)
dialogs_val.extend(account_dialogs_val)
dialogs_val.extend(transaction_history_dialogs_val)


start_dialogs_train = create_start_dialog(dialogs=dialogs_train)
start_dialogs_val = create_start_dialog(dialogs=dialogs_val)

create_raw_data(file_directory="../data/transaction_data/",file_name="raw_data_train.txt",dialogs=transaction_dialogs_train)
create_raw_data(file_directory="../data/transaction_data/",file_name="raw_data_val.txt",dialogs=transaction_dialogs_val)


create_raw_data(file_directory="../data/account_balance_data/",file_name="raw_data_train.txt",dialogs=account_dialogs_train)
create_raw_data(file_directory="../data/account_balance_data/",file_name="raw_data_val.txt",dialogs=account_dialogs_val)



create_raw_data(file_directory="../data/transaction_history_data/",file_name="raw_data_train.txt",dialogs=transaction_history_dialogs_train)
create_raw_data(file_directory="../data/transaction_history_data/",file_name="raw_data_val.txt",dialogs=transaction_history_dialogs_val)





create_raw_data(file_directory="../data/start_data/",file_name="raw_data_train.txt",dialogs=start_dialogs_train)
create_raw_data(file_directory="../data/start_data/",file_name="raw_data_val.txt",dialogs=start_dialogs_val)



one_dialogs_train = dialogs_train
random.shuffle(one_dialogs_train)
one_dialogs_val = dialogs_val
random.shuffle(one_dialogs_val)
    

create_raw_data(file_directory="../data/one_data/",file_name="raw_data_train.txt",dialogs=one_dialogs_train)
create_raw_data(file_directory="../data/one_data/",file_name="raw_data_val.txt",dialogs=one_dialogs_val)

create_training_data(file_directory="../data/transaction_data/",file_name="train_data.txt",dialogs=transaction_dialogs_train)
create_training_data(file_directory="../data/transaction_data/",file_name="val_data.txt",dialogs=transaction_dialogs_val)
create_training_data(file_directory="../data/transaction_data/",file_name="test_data.txt",dialogs=transaction_dialogs_val)

create_training_data(file_directory="../data/account_balance_data/",file_name="train_data.txt",dialogs=account_dialogs_train)
create_training_data(file_directory="../data/account_balance_data/",file_name="val_data.txt",dialogs=account_dialogs_val)
create_training_data(file_directory="../data/account_balance_data/",file_name="test_data.txt",dialogs=account_dialogs_val)


create_training_data(file_directory="../data/transaction_history_data/",file_name="train_data.txt",dialogs=transaction_history_dialogs_train)
create_training_data(file_directory="../data/transaction_history_data/",file_name="val_data.txt",dialogs=transaction_history_dialogs_val)
create_training_data(file_directory="../data/transaction_history_data/",file_name="test_data.txt",dialogs=transaction_history_dialogs_val)


create_training_data(file_directory="../data/start_data/",file_name="train_data.txt",dialogs=start_dialogs_train)
create_training_data(file_directory="../data/start_data/",file_name="val_data.txt",dialogs=start_dialogs_val)
create_training_data(file_directory="../data/start_data/",file_name="test_data.txt",dialogs=start_dialogs_val)


create_training_data(file_directory="../data/one_data/",file_name="train_data.txt",dialogs=one_dialogs_train)
create_training_data(file_directory="../data/one_data/",file_name="val_data.txt",dialogs=one_dialogs_val)
create_training_data(file_directory="../data/one_data/",file_name="test_data.txt",dialogs=one_dialogs_val)


create_candidates(file_directory="../data/transaction_data/",file_name="candidates.txt",dialogs=transaction_dialogs_train)

create_candidates(file_directory="../data/account_balance_data/",file_name="candidates.txt",dialogs=account_dialogs_train)


create_candidates(file_directory="../data/transaction_history_data/",file_name="candidates.txt",dialogs=transaction_history_dialogs_train)


create_candidates(file_directory="../data/start_data/",file_name="candidates.txt",dialogs=start_dialogs_train)


create_candidates(file_directory="../data/one_data/",file_name="candidates.txt",dialogs=one_dialogs_train)


