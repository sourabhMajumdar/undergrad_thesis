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

transaction_templates = make_templates(file_name="templates_for_dialogue_self_play.xlsx",
                                     sheet_name="MAKE_TRANSACTION",
                                     previous_dictionary=None)





account_balance_templates = make_templates(file_name="templates_for_dialogue_self_play.xlsx",
                                     sheet_name="ACCOUNT_BALANCE",
                                     previous_dictionary=None)




transaction_history_templates = make_templates(file_name="templates_for_dialogue_self_play.xlsx",
                                     sheet_name="TRANS_HISTORY",
                                     previous_dictionary=None)




transaction_dialogs = create_dialogs(User=Transaction_user,Bot=Transaction_bot,number_of_dialogs=100,dialog_templates=transaction_templates)
account_dialogs = create_dialogs(User=Account_user,Bot=Account_bot,number_of_dialogs=100,dialog_templates=account_balance_templates)
transaction_history_dialogs = create_dialogs(User=Transaction_history_user,Bot=Transaction_history_bot,number_of_dialogs=100,dialog_templates=transaction_history_templates)

dialogs = list()
dialogs.extend(transaction_dialogs)
dialogs.extend(account_dialogs)
dialogs.extend(transaction_history_dialogs)





start_dialogs = list()
for dialog in dialogs :
    start_dialog = list()
    for action in dialog :
        start_dialog.append(action)
        if action.get_action() == "inform" and "intent" in action.get_slots() :
            mem_action = Action(actor="Bot",
                                action="mem_call",
                                slots=None,
                                values=None,
                                message="mem_call:{}".format(action.get_values()["intent"]))
            start_dialog.append(mem_action)
            break
    start_dialogs.append(start_dialog)

create_raw_data(file_directory="../data/transaction_data/",file_name="raw_data.txt",dialogs=transaction_dialogs)


create_raw_data(file_directory="../data/account_balance_data/",file_name="raw_data.txt",dialogs=account_dialogs)





create_raw_data(file_directory="../data/transaction_history_data/",file_name="raw_data.txt",dialogs=transaction_history_dialogs)





create_raw_data(file_directory="../data/start_data/",file_name="raw_data.txt",dialogs=start_dialogs)




one_dialogs = dialogs
random.shuffle(one_dialogs)



create_raw_data(file_directory="../data/one_data/",file_name="raw_data.txt",dialogs=one_dialogs)


create_training_data(file_directory="../data/transaction_data/",file_name="train_data.txt",dialogs=transaction_dialogs)
create_training_data(file_directory="../data/transaction_data/",file_name="val_data.txt",dialogs=transaction_dialogs)
create_training_data(file_directory="../data/transaction_data/",file_name="test_data.txt",dialogs=transaction_dialogs)


create_training_data(file_directory="../data/account_balance_data/",file_name="train_data.txt",dialogs=account_dialogs)
create_training_data(file_directory="../data/account_balance_data/",file_name="val_data.txt",dialogs=account_dialogs)
create_training_data(file_directory="../data/account_balance_data/",file_name="test_data.txt",dialogs=account_dialogs)



create_training_data(file_directory="../data/transaction_history_data/",file_name="train_data.txt",dialogs=transaction_history_dialogs)
create_training_data(file_directory="../data/transaction_history_data/",file_name="val_data.txt",dialogs=transaction_history_dialogs)
create_training_data(file_directory="../data/transaction_history_data/",file_name="test_data.txt",dialogs=transaction_history_dialogs)



create_training_data(file_directory="../data/start_data/",file_name="train_data.txt",dialogs=start_dialogs)
create_training_data(file_directory="../data/start_data/",file_name="val_data.txt",dialogs=start_dialogs)
create_training_data(file_directory="../data/start_data/",file_name="test_data.txt",dialogs=start_dialogs)



create_training_data(file_directory="../data/one_data/",file_name="train_data.txt",dialogs=one_dialogs)
create_training_data(file_directory="../data/one_data/",file_name="val_data.txt",dialogs=one_dialogs)
create_training_data(file_directory="../data/one_data/",file_name="test_data.txt",dialogs=one_dialogs)


create_candidates(file_directory="../data/transaction_data/",file_name="candidates.txt",dialogs=transaction_dialogs)



create_candidates(file_directory="../data/account_balance_data/",file_name="candidates.txt",dialogs=account_dialogs)




create_candidates(file_directory="../data/transaction_history_data/",file_name="candidates.txt",dialogs=transaction_history_dialogs)




create_candidates(file_directory="../data/start_data/",file_name="candidates.txt",dialogs=start_dialogs)





create_candidates(file_directory="../data/one_data/",file_name="candidates.txt",dialogs=one_dialogs)


