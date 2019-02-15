from utils import *
import tensorflow as tf

from Bot.transaction_bot import Transaction_bot
from Bot.account_balance_bot import Account_bot
from Bot.account_limit_bot import Account_limit_bot
from Bot.block_card_bot import Block_card_bot
from Bot.cancel_transaction_bot import Cancel_transaction_bot
from Bot.search_note_bot import Search_note_bot

from User.transaction_user import Transaction_user
from User.account_balance_user import Account_user
from User.account_limit_user import Account_limit_user
from User.block_card_user import Block_card_user
from User.cancel_transaction_user import Cancel_transaction_user
from User.search_note_user import Search_note_user

import numpy as np # no use until now
import random # used for random sampling of values where applicable
import math # no use untill now
import pandas as pd # to read the excel file 
import os # to carry os operations
import glob
import copy

tf.flags.DEFINE_integer("number_of_dialogs",100,"Number of Dialogs to create, it is uniform for both train,validation and test sets")
FLAGS = tf.flags.FLAGS


transaction_templates = make_templates(sheet_name="MAKE_TRANSACTION",previous_dictionary=None)



account_balance_templates = make_templates(sheet_name="BALANCE",previous_dictionary=None)




account_limit_templates = make_templates(sheet_name="LIMIT",previous_dictionary=None)




block_card_templates = make_templates(sheet_name="BLOCK_CARD",previous_dictionary=None)



cancel_transaction_templates = make_templates(sheet_name="CANCEL_LAST_TRANSACTION",previous_dictionary=None)


search_note_templates = make_templates(sheet_name="SEARCH_NOTE",previous_dictionary=None)





knowledge_base = pd.read_excel('user_values.xlsx','UserValues')
list_of_user_profiles = list()

for index,row in knowledge_base.iterrows() :
    list_of_user_profiles.append(row)


data_frame = pd.read_excel('Game_of_Dialogs.xlsx','VARIABLE_VALUES')
user_values = dict()

for index,row in data_frame.iterrows() :
    for column in data_frame.columns :
        list_of_values = list()
        if column in user_values.keys() :
            list_of_values = user_values[column]
        if not pd.isnull(row[column]) :
            list_of_values.append(row[column])
        user_values[column] = list_of_values


required_number_of_dialogs = FLAGS.number_of_dialogs


transaction_dialogs = create_dialogs(User=Transaction_user,
                                     Bot=Transaction_bot,
                                     number_of_dialogs=required_number_of_dialogs,
                                     dialog_templates=transaction_templates,
                                     list_of_user_profiles=list_of_user_profiles,
                                     user_values=user_values,
                                     turn_compression=False,
                                     new_api=False,
                                     re_order=False,
                                     another_slot=False,
                                     audit_more=False)

print("length of training transaction dialogs :{}".format(str(len(transaction_dialogs["train"]))))
print("length of validation transaction dialogs :{}".format(str(len(transaction_dialogs["val"]))))
print("length of test transaction dialogs : {}".format(str(len(transaction_dialogs["test_oot"]))))

transaction_dialogs_turn_compression = create_dialogs(User=Transaction_user,
                                                      Bot=Transaction_bot,
                                                      number_of_dialogs=required_number_of_dialogs,
                                                      dialog_templates=transaction_templates,
                                                      list_of_user_profiles=list_of_user_profiles,
                                                      user_values=user_values,
                                                      turn_compression=True,
                                                      new_api=False,
                                                      re_order=False,
                                                      another_slot=False,
                                                      audit_more=False)

print("length of training transaction dialogs for turn compression test :{}".format(str(len(transaction_dialogs_turn_compression["test"]))))
print("length of test transaction dialogs for turn compressioon test with oot : {}".format(str(len(transaction_dialogs_turn_compression["test_oot"]))))

transaction_dialogs_new_api = create_dialogs(User=Transaction_user,
                                             Bot=Transaction_bot,
                                             number_of_dialogs=required_number_of_dialogs,
                                             dialog_templates=transaction_templates,
                                             list_of_user_profiles=list_of_user_profiles,
                                             user_values=user_values,
                                             turn_compression=False,
                                             new_api=True,
                                             re_order=False,
                                             another_slot=False,
                                             audit_more=False)

print("length of training transaction dialogs for new api test :{}".format(str(len(transaction_dialogs_new_api["test"]))))
print("length of test transaction dialogs for new api test with oot : {}".format(str(len(transaction_dialogs_new_api["test_oot"]))))

transaction_dialogs_re_order = create_dialogs(User=Transaction_user,
                                              Bot=Transaction_bot,
                                              number_of_dialogs=required_number_of_dialogs,
                                              dialog_templates=transaction_templates,
                                              list_of_user_profiles=list_of_user_profiles,
                                              user_values=user_values,
                                              turn_compression=False,
                                              new_api=False,
                                              re_order=True,
                                              another_slot=False,
                                              audit_more=False)

print("length of training transaction dialogs for re-order test :{}".format(str(len(transaction_dialogs_re_order["test"]))))
print("length of test transaction dialogs for re-order test with oot : {}".format(str(len(transaction_dialogs_re_order["test_oot"]))))

transaction_dialogs_another_slot = create_dialogs(User=Transaction_user,
                                                  Bot=Transaction_bot,
                                                  number_of_dialogs=required_number_of_dialogs,
                                                  dialog_templates=transaction_templates,
                                                  list_of_user_profiles=list_of_user_profiles,
                                                  user_values=user_values,
                                                  turn_compression=False,
                                                  new_api=False,
                                                  re_order=False,
                                                  another_slot=True,
                                                  audit_more=False)


print("length of training transaction dialogs for another slot test : {}".format(str(len(transaction_dialogs_another_slot["test"]))))
print("lenght of test transaction dialogs for another slot with oot : {}".format(str(len(transaction_dialogs_another_slot["test_oot"]))))

transaction_dialogs_audit_more = create_dialogs(User=Transaction_user,
                                                Bot=Transaction_bot,
                                                number_of_dialogs=required_number_of_dialogs,
                                                dialog_templates=transaction_templates,
                                                list_of_user_profiles=list_of_user_profiles,
                                                user_values=user_values,
                                                turn_compression=False,
                                                new_api=False,
                                                re_order=False,
                                                another_slot=False,
                                                audit_more=True)

print("length of transaction dialogs test : {}".format(str(len(transaction_dialogs_audit_more["test"]))))
print("length of transaction dialogs test oot : {}".format(str(len(transaction_dialogs_audit_more["test_oot"]))))


# In[60]:


account_balance_dialogs = create_dialogs(User=Account_user,
                                         Bot=Account_bot,
                                         number_of_dialogs=required_number_of_dialogs,
                                         dialog_templates=account_balance_templates,
                                         list_of_user_profiles=list_of_user_profiles,
                                         user_values=user_values,
                                         turn_compression=False,
                                         new_api=False,
                                         re_order=False,
                                         another_slot=False,
                                         audit_more=False)

print("length of training account dialogs :{}".format(str(len(account_balance_dialogs["train"]))))
print("length of validation account dialogs :{}".format(str(len(account_balance_dialogs["val"]))))
print("length of validation account dialogs test oot  :{}".format(str(len(account_balance_dialogs["test_oot"]))))

account_balance_dialogs_turn_compression = create_dialogs(User=Account_user,
                                                          Bot=Account_bot,
                                                          number_of_dialogs=required_number_of_dialogs,
                                                          dialog_templates=account_balance_templates,
                                                          list_of_user_profiles=list_of_user_profiles,
                                                          user_values=user_values,
                                                          turn_compression=True,
                                                          new_api=False,
                                                          re_order=False,
                                                          another_slot=False,
                                                          audit_more=False)


print("length of training account dialogs turn compression test :{}".format(str(len(account_balance_dialogs_turn_compression["test"]))))
print("length of validation account dialogs turn compression test oot  :{}".format(str(len(account_balance_dialogs_turn_compression["test_oot"]))))

account_balance_dialogs_new_api = create_dialogs(User=Account_user,
                                                 Bot=Account_bot,
                                                 number_of_dialogs=required_number_of_dialogs,
                                                 dialog_templates=account_balance_templates,
                                                 list_of_user_profiles=list_of_user_profiles,
                                                 user_values=user_values,
                                                 turn_compression=False,
                                                 new_api=True,
                                                 re_order=False,
                                                 another_slot=False,
                                                 audit_more=False)


print("length of training account dialogs new api test :{}".format(str(len(account_balance_dialogs_new_api["test"]))))
print("length of validation account dialogs new api test oot  :{}".format(str(len(account_balance_dialogs_new_api["test_oot"]))))

account_balance_dialogs_re_order = create_dialogs(User=Account_user,
                                                  Bot=Account_bot,
                                                  number_of_dialogs=required_number_of_dialogs,
                                                  dialog_templates=account_balance_templates,
                                                  list_of_user_profiles=list_of_user_profiles,
                                                  user_values=user_values,
                                                  turn_compression=False,
                                                  new_api=False,
                                                  re_order=True,
                                                  another_slot=False,
                                                  audit_more=False)

print("length of training account dialogs re order test :{}".format(str(len(account_balance_dialogs_re_order["test"]))))
print("length of validation account dialogs re order test oot  :{}".format(str(len(account_balance_dialogs_re_order["test_oot"]))))

account_balance_dialogs_another_slot = create_dialogs(User=Account_user,
                                                      Bot=Account_bot,
                                                      number_of_dialogs=required_number_of_dialogs,
                                                      dialog_templates=account_balance_templates,
                                                      list_of_user_profiles=list_of_user_profiles,
                                                      user_values=user_values,
                                                      turn_compression=False,
                                                      new_api=False,
                                                      re_order=False,
                                                      another_slot=False,
                                                      audit_more=False)


print("length of account dialogs for another slot test : {}".format(str(len(account_balance_dialogs_another_slot["test"]))))
print("length of account dialogs for another slot test oot : {}".format(str(len(account_balance_dialogs_another_slot["test_oot"]))))

account_balance_dialogs_audit_more= create_dialogs(User=Account_user,
                                                   Bot=Account_bot,
                                                   number_of_dialogs=required_number_of_dialogs,
                                                   dialog_templates=account_balance_templates,
                                                   list_of_user_profiles=list_of_user_profiles,
                                                   user_values=user_values,
                                                   turn_compression=False,
                                                   new_api=False,
                                                   re_order=False,
                                                   another_slot=False,
                                                   audit_more=True)


print("length of account dialogs for audit more slot test : {}".format(str(len(account_balance_dialogs_audit_more["test"]))))
print("length of account dialogs for audit more slot test oot : {}".format(str(len(account_balance_dialogs_audit_more["test_oot"]))))


# In[61]:


account_limit_dialogs = create_dialogs(User=Account_limit_user,
                                       Bot=Account_limit_bot,
                                       number_of_dialogs=required_number_of_dialogs,
                                       dialog_templates=account_limit_templates,
                                       list_of_user_profiles=list_of_user_profiles,
                                       user_values=user_values,
                                       turn_compression=False,
                                       new_api=False,
                                       re_order=False,
                                       another_slot=False,
                                       audit_more=False)
print("length of training account limit dialogs :{}".format(str(len(account_limit_dialogs["train"]))))
print("length of validation account limit dialogs :{}".format(str(len(account_limit_dialogs["val"]))))

account_limit_dialogs_turn_compression = create_dialogs(User=Account_limit_user,
                                                        Bot=Account_limit_bot,
                                                        number_of_dialogs=required_number_of_dialogs,
                                                        dialog_templates=account_limit_templates,
                                                        list_of_user_profiles=list_of_user_profiles,
                                                        user_values=user_values,
                                                        turn_compression=True,
                                                        new_api=False,
                                                        re_order=False,
                                                        another_slot=False,
                                                        audit_more=False)


print("length of training account limit dialogs test :{}".format(str(len(account_limit_dialogs_turn_compression["test"]))))
print("length of validation account limit dialogs  test oot:{}".format(str(len(account_limit_dialogs_turn_compression["test_oot"]))))

account_limit_dialogs_new_api = create_dialogs(User=Account_limit_user,
                                               Bot=Account_limit_bot,
                                               number_of_dialogs=required_number_of_dialogs,
                                               dialog_templates=account_limit_templates,
                                               list_of_user_profiles=list_of_user_profiles,
                                               user_values=user_values,
                                               turn_compression=False,
                                               new_api=True,
                                               re_order=False,
                                               another_slot=False,
                                               audit_more=False)


print("length of training account limit dialogs test :{}".format(str(len(account_limit_dialogs_new_api["test"]))))
print("length of validation account limit dialogs  test oot:{}".format(str(len(account_limit_dialogs_new_api["test_oot"]))))

account_limit_dialogs_re_order = create_dialogs(User=Account_limit_user,
                                                Bot=Account_limit_bot,
                                                number_of_dialogs=required_number_of_dialogs,
                                                dialog_templates=account_limit_templates,
                                                list_of_user_profiles=list_of_user_profiles,
                                                user_values=user_values,
                                                turn_compression=False,
                                                new_api=False,
                                                re_order=True,
                                                another_slot=False,
                                                audit_more=False)



print("length of training account limit dialogs re order test :{}".format(str(len(account_limit_dialogs_re_order["test"]))))
print("length of validation account limit dialogs re_order test oot:{}".format(str(len(account_limit_dialogs_re_order["test_oot"]))))

account_limit_dialogs_another_slot = create_dialogs(User=Account_limit_user,
                                                    Bot=Account_limit_bot,
                                                    number_of_dialogs=required_number_of_dialogs,
                                                    dialog_templates=account_limit_templates,
                                                    list_of_user_profiles=list_of_user_profiles,
                                                    user_values=user_values,
                                                    turn_compression=False,
                                                    new_api=False,
                                                    re_order=False,
                                                    another_slot=True,
                                                    audit_more=False)

print("length of training account limit dialogs re order test :{}".format(str(len(account_limit_dialogs_another_slot["test"]))))
print("length of validation account limit dialogs re_order test oot:{}".format(str(len(account_limit_dialogs_another_slot["test_oot"]))))

account_limit_dialogs_audit_more = create_dialogs(User=Account_limit_user,
                                                  Bot=Account_limit_bot,
                                                  number_of_dialogs=required_number_of_dialogs,
                                                  dialog_templates=account_limit_templates,
                                                  list_of_user_profiles=list_of_user_profiles,
                                                  user_values=user_values,
                                                  turn_compression=False,
                                                  new_api=False,
                                                  re_order=False,
                                                  another_slot=False,
                                                  audit_more=True)


print("length of training account limit dialogs audit more test :{}".format(str(len(account_limit_dialogs_audit_more["test"]))))
print("length of validation account limit dialogs audit more test oot:{}".format(str(len(account_limit_dialogs_audit_more["test_oot"]))))


# In[62]:


block_card_dialogs = create_dialogs(User=Block_card_user,
                                    Bot=Block_card_bot,
                                    number_of_dialogs=required_number_of_dialogs,
                                    dialog_templates=block_card_templates,
                                    list_of_user_profiles=list_of_user_profiles,
                                    user_values=user_values,
                                    turn_compression=False,
                                    new_api=False,
                                    re_order=False,
                                    another_slot=False,
                                    audit_more=False)

print("length of training account limit dialogs :{}".format(str(len(block_card_dialogs["train"]))))
print("length of validation account limit dialogs :{}".format(str(len(block_card_dialogs["val"]))))

block_card_dialogs_turn_compression = create_dialogs(User=Block_card_user,
                                                     Bot=Block_card_bot,
                                                     number_of_dialogs=required_number_of_dialogs,
                                                     dialog_templates=block_card_templates,
                                                     list_of_user_profiles=list_of_user_profiles,
                                                     user_values=user_values,
                                                     turn_compression=True,
                                                     new_api=False,
                                                     re_order=False,
                                                     another_slot=False,
                                                     audit_more=False)

print("length of training account limit dialogs turn compression test:{}".format(str(len(block_card_dialogs_turn_compression["test"]))))
print("length of validation account limit dialogs turn compressio test oot :{}".format(str(len(block_card_dialogs_turn_compression["test_oot"]))))

block_card_dialogs_new_api = create_dialogs(User=Block_card_user,
                                            Bot=Block_card_bot,
                                            number_of_dialogs=required_number_of_dialogs,
                                            dialog_templates=block_card_templates,
                                            list_of_user_profiles=list_of_user_profiles,
                                            user_values=user_values,
                                            turn_compression=False,
                                            new_api=True,
                                            re_order=False,
                                            another_slot=False,
                                            audit_more=False)

print("length of training account limit dialogs new api test:{}".format(str(len(block_card_dialogs_new_api["test"]))))
print("length of validation account limit dialogs new api test oot :{}".format(str(len(block_card_dialogs_new_api["test_oot"]))))

block_card_dialogs_re_order = create_dialogs(User=Block_card_user,
                                              Bot=Block_card_bot,
                                              number_of_dialogs=required_number_of_dialogs,
                                              dialog_templates=block_card_templates,
                                             list_of_user_profiles=list_of_user_profiles,
                                             user_values=user_values,
                                              turn_compression=False,
                                              new_api=False,
                                              re_order=True,
                                              another_slot=False,
                                              audit_more=False)

print("length of training account limit dialogs re order test:{}".format(str(len(block_card_dialogs_re_order["test"]))))
print("length of validation account limit dialogs re order test oot :{}".format(str(len(block_card_dialogs_re_order["test_oot"]))))

block_card_dialogs_another_slot = create_dialogs(User=Block_card_user,
                                                 Bot=Block_card_bot,
                                                 number_of_dialogs=required_number_of_dialogs,
                                                 dialog_templates=block_card_templates,
                                                 list_of_user_profiles=list_of_user_profiles,
                                                 user_values=user_values,
                                                 turn_compression=False,
                                                 new_api=False,
                                                 re_order=False,
                                                 another_slot=True,
                                                 audit_more=False)



print("length of training account limit dialogs another slot test:{}".format(str(len(block_card_dialogs_another_slot["test"]))))
print("length of validation account limit dialogs another slot test oot :{}".format(str(len(block_card_dialogs_another_slot["test_oot"]))))

block_card_dialogs_audit_more = create_dialogs(User=Block_card_user,
                                               Bot=Block_card_bot,
                                               number_of_dialogs=required_number_of_dialogs,
                                               dialog_templates=block_card_templates,
                                               list_of_user_profiles=list_of_user_profiles,
                                               user_values=user_values,
                                               turn_compression=False,
                                               new_api=False,
                                               re_order=False,
                                               another_slot=False,
                                               audit_more=True)

print("length of training account limit dialogs audit more test:{}".format(str(len(block_card_dialogs_audit_more["test"]))))
print("length of validation account limit dialogs audit more test oot :{}".format(str(len(block_card_dialogs_audit_more["test_oot"]))))


# In[63]:


cancel_transaction_dialogs = create_dialogs(User=Cancel_transaction_user,
                                           Bot=Cancel_transaction_bot,
                                           number_of_dialogs=required_number_of_dialogs,
                                           dialog_templates=cancel_transaction_templates,
                                            list_of_user_profiles=list_of_user_profiles,
                                            user_values=user_values,
                                           turn_compression=False,
                                           new_api=False,
                                           re_order=False,
                                           another_slot=False,
                                           audit_more=False)

print("length of training account limit dialogs :{}".format(str(len(cancel_transaction_dialogs["train"]))))
print("length of validation account limit dialogs :{}".format(str(len(cancel_transaction_dialogs["val"]))))

cancel_transaction_dialogs_turn_compression = create_dialogs(User=Cancel_transaction_user,
                                                             Bot=Cancel_transaction_bot,
                                                             number_of_dialogs=required_number_of_dialogs,
                                                             dialog_templates=cancel_transaction_templates,
                                                             list_of_user_profiles=list_of_user_profiles,
                                                         user_values=user_values,
                                                            turn_compression=True,
                                                             new_api=False,
                                                             re_order=False,
                                                             another_slot=False,
                                                             audit_more=False)

print("length of training account limit dialogs turn compression :{}".format(str(len(cancel_transaction_dialogs_turn_compression["test"]))))
print("length of validation account limit dialogs turn compression oot :{}".format(str(len(cancel_transaction_dialogs_turn_compression["test_oot"]))))

cancel_transaction_dialogs_new_api = create_dialogs(User=Cancel_transaction_user,
                                                    Bot=Cancel_transaction_bot,
                                                    number_of_dialogs=required_number_of_dialogs,
                                                    dialog_templates=cancel_transaction_templates,
                                                    list_of_user_profiles=list_of_user_profiles,
                                                    user_values=user_values,
                                                    turn_compression=False,
                                                    new_api=True,
                                                    re_order=False,
                                                    another_slot=False,
                                                    audit_more=False)


print("length of training account limit dialogs new api :{}".format(str(len(cancel_transaction_dialogs_new_api["test"]))))
print("length of validation account limit dialogs new api oot :{}".format(str(len(cancel_transaction_dialogs_new_api["test_oot"]))))

cancel_transaction_dialogs_re_order = create_dialogs(User=Cancel_transaction_user,
                                                     Bot=Cancel_transaction_bot,
                                                     number_of_dialogs=required_number_of_dialogs,
                                                     dialog_templates=cancel_transaction_templates,
                                                     list_of_user_profiles=list_of_user_profiles,
                                                     user_values=user_values,
                                                     turn_compression=True,
                                                     new_api=True,
                                                     re_order=True,
                                                     another_slot=False,
                                                     audit_more=False)

print("length of training account limit dialogs re order :{}".format(str(len(cancel_transaction_dialogs_re_order["test"]))))
print("length of validation account limit dialogs re order oot :{}".format(str(len(cancel_transaction_dialogs_re_order["test_oot"]))))

cancel_transaction_dialogs_another_slot = create_dialogs(User=Cancel_transaction_user,
                                                         Bot=Cancel_transaction_bot,
                                                         number_of_dialogs=required_number_of_dialogs,
                                                         dialog_templates=cancel_transaction_templates,
                                                         list_of_user_profiles=list_of_user_profiles,
                                                         user_values=user_values,
                                                         turn_compression=False,
                                                         new_api=False,
                                                         re_order=False,
                                                         another_slot=True,
                                                         audit_more=False)

print("length of training account limit dialogs re order :{}".format(str(len(cancel_transaction_dialogs_another_slot["test"]))))
print("length of validation account limit dialogs re order oot :{}".format(str(len(cancel_transaction_dialogs_another_slot["test_oot"]))))

cancel_transaction_dialogs_audit_more = create_dialogs(User=Cancel_transaction_user,
                                                       Bot=Cancel_transaction_bot,
                                                       number_of_dialogs=required_number_of_dialogs,
                                                       dialog_templates=cancel_transaction_templates,
                                                       list_of_user_profiles=list_of_user_profiles,
                                                       user_values=user_values,
                                                       turn_compression=False,
                                                       new_api=False,
                                                       re_order=False,
                                                       another_slot=False,
                                                       audit_more=True)

print("length of training account limit dialogs audit more :{}".format(str(len(cancel_transaction_dialogs_audit_more["test"]))))
print("length of validation account limit dialogs audit more oot :{}".format(str(len(cancel_transaction_dialogs_audit_more["test_oot"]))))


# In[64]:


search_note_dialogs = create_dialogs(User=Search_note_user,
                                     Bot=Search_note_bot,
                                     number_of_dialogs=required_number_of_dialogs,
                                     dialog_templates=search_note_templates,
                                     list_of_user_profiles=list_of_user_profiles,
                                     user_values=user_values,
                                     turn_compression=False,
                                     new_api=False,
                                     re_order=False,
                                     another_slot=False,
                                     audit_more=False)

print("length of training transaction dialogs :{}".format(str(len(search_note_dialogs["train"]))))
print("length of validation transaction dialogs :{}".format(str(len(search_note_dialogs["val"]))))

search_note_dialogs_turn_compression = create_dialogs(User=Search_note_user,
                                                      Bot=Search_note_bot,
                                                      number_of_dialogs=required_number_of_dialogs,
                                                      dialog_templates=search_note_templates,
                                                      list_of_user_profiles=list_of_user_profiles,
                                                      user_values=user_values,
                                                      turn_compression=True,
                                                      new_api=False,
                                                      re_order=False,
                                                      another_slot=False,
                                                      audit_more=False)

print("length of  cancel transaction dialogs test :{}".format(str(len(search_note_dialogs_turn_compression["test"]))))
print("length of cancel transaction dialogs test oot:{}".format(str(len(search_note_dialogs_turn_compression["test_oot"]))))

search_note_dialogs_new_api = create_dialogs(User=Search_note_user,
                                             Bot=Search_note_bot,
                                             number_of_dialogs=required_number_of_dialogs,
                                             dialog_templates=search_note_templates,
                                             list_of_user_profiles=list_of_user_profiles,
                                             user_values=user_values,
                                             turn_compression=False,
                                             new_api=True,
                                             re_order=False,
                                             another_slot=False,
                                             audit_more=False)


print("length of  cancel transaction dialogs test :{}".format(str(len(search_note_dialogs_new_api["test"]))))
print("length of cancel transaction dialogs test oot:{}".format(str(len(search_note_dialogs_new_api["test_oot"]))))

search_note_dialogs_re_order = create_dialogs(User=Search_note_user,
                                              Bot=Search_note_bot,
                                              number_of_dialogs=required_number_of_dialogs,
                                              dialog_templates=search_note_templates,
                                              list_of_user_profiles=list_of_user_profiles,
                                              user_values=user_values,
                                              turn_compression=False,
                                              new_api=False,
                                              re_order=True,
                                              another_slot=False,
                                              audit_more=False)


print("length of  cancel transaction dialogs test :{}".format(str(len(search_note_dialogs_re_order["test"]))))
print("length of cancel transaction dialogs test oot:{}".format(str(len(search_note_dialogs_re_order["test"]))))

search_note_dialogs_another_slot = create_dialogs(User=Search_note_user,
                                                  Bot=Search_note_bot,
                                                  number_of_dialogs=required_number_of_dialogs,
                                                  dialog_templates=search_note_templates,
                                                  list_of_user_profiles=list_of_user_profiles,
                                                  user_values=user_values,
                                                  turn_compression=False,
                                                  new_api=False,
                                                  re_order=False,
                                                  another_slot=True,
                                                  audit_more=False)


print("length of  cancel transaction dialogs another slot test :{}".format(str(len(search_note_dialogs_another_slot["test"]))))
print("length of cancel transaction dialogs another slot test oot:{}".format(str(len(search_note_dialogs_another_slot["test"]))))

search_note_dialogs_audit_more = create_dialogs(User=Search_note_user,
                                                Bot=Search_note_bot,
                                                number_of_dialogs=required_number_of_dialogs,
                                                dialog_templates=search_note_templates,
                                                list_of_user_profiles=list_of_user_profiles,
                                                user_values=user_values,
                                                turn_compression=False,
                                                new_api=False,
                                                re_order=True,
                                                another_slot=False,
                                                audit_more=True)

print("length of  cancel transaction dialogs test :{}".format(str(len(search_note_dialogs_audit_more["test"]))))
print("length of cancel transaction dialogs test oot:{}".format(str(len(search_note_dialogs_audit_more["test"]))))




dialogs_train = list()
dialogs_train.extend(transaction_dialogs["train"])
dialogs_train.extend(account_balance_dialogs["train"])
dialogs_train.extend(account_limit_dialogs["train"])
dialogs_train.extend(block_card_dialogs["train"])
dialogs_train.extend(cancel_transaction_dialogs["train"])
dialogs_train.extend(search_note_dialogs["train"])



dialogs_val = list()
dialogs_val.extend(transaction_dialogs["val"])
dialogs_val.extend(account_balance_dialogs["val"])
dialogs_val.extend(account_limit_dialogs["val"])
dialogs_val.extend(block_card_dialogs["val"])
dialogs_val.extend(cancel_transaction_dialogs["val"])
dialogs_val.extend(search_note_dialogs["val"])


dialogs_test = list()
dialogs_test.extend(transaction_dialogs["test"])
dialogs_test.extend(account_balance_dialogs["test"])
dialogs_test.extend(account_limit_dialogs["test"])
dialogs_test.extend(block_card_dialogs["test"])
dialogs_test.extend(cancel_transaction_dialogs["test"])
dialogs_test.extend(search_note_dialogs["test"])


dialogs_test_oot = list()
dialogs_test_oot.extend(transaction_dialogs["test_oot"])
dialogs_test_oot.extend(account_balance_dialogs["test_oot"])
dialogs_test_oot.extend(account_limit_dialogs["test_oot"])
dialogs_test_oot.extend(block_card_dialogs["test_oot"])
dialogs_test_oot.extend(cancel_transaction_dialogs["test_oot"])
dialogs_test_oot.extend(search_note_dialogs["test_oot"])


dialogs_turn_compression_test = list()
dialogs_turn_compression_test.extend(transaction_dialogs_turn_compression["test"])
dialogs_turn_compression_test.extend(account_balance_dialogs_turn_compression["test"])
dialogs_turn_compression_test.extend(account_limit_dialogs_turn_compression["test"])
dialogs_turn_compression_test.extend(block_card_dialogs_turn_compression["test"])
dialogs_turn_compression_test.extend(cancel_transaction_dialogs_turn_compression["test"])
dialogs_turn_compression_test.extend(search_note_dialogs_turn_compression["test"])


dialogs_turn_compression_test_oot = list()
dialogs_turn_compression_test_oot.extend(transaction_dialogs_turn_compression["test_oot"])
dialogs_turn_compression_test_oot.extend(account_balance_dialogs_turn_compression["test_oot"])
dialogs_turn_compression_test_oot.extend(account_limit_dialogs_turn_compression["test_oot"])
dialogs_turn_compression_test_oot.extend(block_card_dialogs_turn_compression["test_oot"])
dialogs_turn_compression_test_oot.extend(cancel_transaction_dialogs_turn_compression["test_oot"])
dialogs_turn_compression_test_oot.extend(search_note_dialogs_turn_compression["test_oot"])


dialogs_new_api_test = list()
dialogs_new_api_test.extend(transaction_dialogs_new_api["test"])
dialogs_new_api_test.extend(account_balance_dialogs_new_api["test"])
dialogs_new_api_test.extend(account_limit_dialogs_new_api["test"])
dialogs_new_api_test.extend(block_card_dialogs_new_api["test"])
dialogs_new_api_test.extend(cancel_transaction_dialogs_new_api["test"])
dialogs_new_api_test.extend(search_note_dialogs_new_api["test"])


dialogs_new_api_test_oot = list()
dialogs_new_api_test_oot.extend(transaction_dialogs_new_api["test_oot"])
dialogs_new_api_test_oot.extend(account_balance_dialogs_new_api["test_oot"])
dialogs_new_api_test_oot.extend(account_limit_dialogs_new_api["test_oot"])
dialogs_new_api_test_oot.extend(block_card_dialogs_new_api["test_oot"])
dialogs_new_api_test_oot.extend(cancel_transaction_dialogs_new_api["test_oot"])
dialogs_new_api_test_oot.extend(search_note_dialogs_new_api["test_oot"])


dialogs_re_order_test = list()
dialogs_re_order_test.extend(transaction_dialogs_re_order["test"])
dialogs_re_order_test.extend(account_balance_dialogs_re_order["test"])
dialogs_re_order_test.extend(account_limit_dialogs_re_order["test"])
dialogs_re_order_test.extend(block_card_dialogs_re_order["test"])
dialogs_re_order_test.extend(cancel_transaction_dialogs_re_order["test"])
dialogs_re_order_test.extend(search_note_dialogs_re_order["test"])


dialogs_re_order_test_oot = list()
dialogs_re_order_test_oot.extend(transaction_dialogs_re_order["test_oot"])
dialogs_re_order_test_oot.extend(account_balance_dialogs_re_order["test_oot"])
dialogs_re_order_test_oot.extend(account_limit_dialogs_re_order["test_oot"])
dialogs_re_order_test_oot.extend(block_card_dialogs_re_order["test_oot"])
dialogs_re_order_test_oot.extend(cancel_transaction_dialogs_re_order["test_oot"])
dialogs_re_order_test_oot.extend(search_note_dialogs_re_order["test_oot"])


dialogs_another_slot_test = list()
dialogs_another_slot_test.extend(transaction_dialogs_another_slot["test"])
dialogs_another_slot_test.extend(account_balance_dialogs_another_slot["test"])
dialogs_another_slot_test.extend(account_limit_dialogs_another_slot["test"])
dialogs_another_slot_test.extend(block_card_dialogs_another_slot["test"])
dialogs_another_slot_test.extend(cancel_transaction_dialogs_another_slot["test"])
dialogs_another_slot_test.extend(search_note_dialogs_another_slot["test"])


dialogs_another_slot_test_oot = list()
dialogs_another_slot_test_oot.extend(transaction_dialogs_another_slot["test_oot"])
dialogs_another_slot_test_oot.extend(account_balance_dialogs_another_slot["test_oot"])
dialogs_another_slot_test_oot.extend(account_limit_dialogs_another_slot["test_oot"])
dialogs_another_slot_test_oot.extend(block_card_dialogs_another_slot["test_oot"])
dialogs_another_slot_test_oot.extend(cancel_transaction_dialogs_another_slot["test_oot"])
dialogs_another_slot_test_oot.extend(search_note_dialogs_another_slot["test_oot"])


dialogs_audit_more_test = list()
dialogs_audit_more_test.extend(transaction_dialogs_audit_more["test"])
dialogs_audit_more_test.extend(account_balance_dialogs_audit_more["test"])
dialogs_audit_more_test.extend(account_limit_dialogs_audit_more["test"])
dialogs_audit_more_test.extend(block_card_dialogs_audit_more["test"])
dialogs_audit_more_test.extend(cancel_transaction_dialogs_audit_more["test"])
dialogs_audit_more_test.extend(search_note_dialogs_audit_more["test"])



dialogs_audit_more_test_oot = list()
dialogs_audit_more_test_oot.extend(transaction_dialogs_audit_more["test_oot"])
dialogs_audit_more_test_oot.extend(account_balance_dialogs_audit_more["test_oot"])
dialogs_audit_more_test_oot.extend(account_limit_dialogs_audit_more["test_oot"])
dialogs_audit_more_test_oot.extend(block_card_dialogs_audit_more["test_oot"])
dialogs_audit_more_test_oot.extend(cancel_transaction_dialogs_audit_more["test_oot"])
dialogs_audit_more_test_oot.extend(search_note_dialogs_audit_more["test_oot"])


one_dialogs_train = dialogs_train
random.shuffle(one_dialogs_train)
one_dialogs_val = dialogs_val
random.shuffle(one_dialogs_val)

one_dialogs_test = dialogs_test
one_dialogs_test_oot = dialogs_test_oot

one_dialogs_turn_compression_test = dialogs_turn_compression_test
one_dialogs_turn_compression_test_oot = dialogs_turn_compression_test_oot

one_dialogs_new_api_test = dialogs_new_api_test
one_dialogs_new_api_test_oot = dialogs_new_api_test_oot

one_dialogs_re_order_test = dialogs_re_order_test
one_dialogs_re_order_test_oot = dialogs_re_order_test_oot

one_dialogs_another_slot_test = dialogs_another_slot_test
one_dialogs_another_slot_test_oot = dialogs_another_slot_test_oot

one_dialogs_audit_more_test = dialogs_audit_more_test
one_dialogs_audit_more_test_oot = dialogs_audit_more_test_oot

random.shuffle(one_dialogs_test_oot)

random.shuffle(one_dialogs_turn_compression_test)
random.shuffle(one_dialogs_turn_compression_test_oot)

random.shuffle(one_dialogs_new_api_test)
random.shuffle(one_dialogs_new_api_test_oot)

random.shuffle(one_dialogs_re_order_test)
random.shuffle(one_dialogs_re_order_test_oot)

random.shuffle(one_dialogs_another_slot_test)
random.shuffle(one_dialogs_another_slot_test_oot)

random.shuffle(one_dialogs_turn_compression_test)
random.shuffle(one_dialogs_turn_compression_test_oot)


start_dialogs_train = create_start_dialog(dialogs=dialogs_train)
start_dialogs_val = create_start_dialog(dialogs=dialogs_val)



start_dialogs_test = create_start_dialog(dialogs=dialogs_test)
start_dialogs_test_oot = create_start_dialog(dialogs=dialogs_test_oot)

start_dialogs_turn_compression_test = create_start_dialog(dialogs=dialogs_turn_compression_test)
start_dialogs_turn_compression_test_oot = create_start_dialog(dialogs=dialogs_turn_compression_test_oot)

start_dialogs_new_api_test = create_start_dialog(dialogs=dialogs_new_api_test)
start_dialogs_new_api_test_oot = create_start_dialog(dialogs=dialogs_new_api_test_oot)

start_dialogs_re_order_test = create_start_dialog(dialogs=dialogs_re_order_test)
start_dialogs_re_order_test_oot = create_start_dialog(dialogs=dialogs_re_order_test_oot)

start_dialogs_another_slot_test = create_start_dialog(dialogs=dialogs_another_slot_test)
start_dialogs_another_slot_test_oot = create_start_dialog(dialogs=dialogs_another_slot_test_oot)

start_dialogs_audit_more_test = create_start_dialog(dialogs=dialogs_audit_more_test)
start_dialogs_audit_more_test_oot = create_start_dialog(dialogs=dialogs_audit_more_test_oot)

start_dialogs_all = list()

start_dialogs_all.extend(start_dialogs_train)
start_dialogs_all.extend(start_dialogs_val)

start_dialogs_all.extend(start_dialogs_test)
start_dialogs_all.extend(start_dialogs_test_oot)

start_dialogs_all.extend(start_dialogs_turn_compression_test)
start_dialogs_all.extend(start_dialogs_turn_compression_test_oot)

start_dialogs_all.extend(start_dialogs_new_api_test)
start_dialogs_all.extend(start_dialogs_new_api_test_oot)

start_dialogs_all.extend(start_dialogs_re_order_test)
start_dialogs_all.extend(start_dialogs_re_order_test_oot)

start_dialogs_all.extend(start_dialogs_another_slot_test)
start_dialogs_all.extend(start_dialogs_another_slot_test_oot)

start_dialogs_all.extend(start_dialogs_audit_more_test)
start_dialogs_all.extend(start_dialogs_audit_more_test_oot)

random.shuffle(start_dialogs_all)


one_dialogs_all = list()
one_dialogs_all.extend(one_dialogs_train)
one_dialogs_all.extend(one_dialogs_val)

one_dialogs_all.extend(one_dialogs_test_oot)

one_dialogs_all.extend(one_dialogs_turn_compression_test)
one_dialogs_all.extend(one_dialogs_turn_compression_test_oot)

one_dialogs_all.extend(one_dialogs_new_api_test)
one_dialogs_all.extend(one_dialogs_new_api_test_oot)

one_dialogs_all.extend(one_dialogs_re_order_test)
one_dialogs_all.extend(one_dialogs_re_order_test_oot)

one_dialogs_all.extend(one_dialogs_another_slot_test)
one_dialogs_all.extend(one_dialogs_another_slot_test_oot)

one_dialogs_all.extend(one_dialogs_audit_more_test)
one_dialogs_all.extend(one_dialogs_audit_more_test_oot)

one_dialogs_all.extend(start_dialogs_all)

random.shuffle(one_dialogs_all)

transaction_dialogs_all = list()
transaction_dialogs_all.extend(transaction_dialogs["train"])
transaction_dialogs_all.extend(transaction_dialogs["val"])

transaction_dialogs_all.extend(transaction_dialogs["test"])
transaction_dialogs_all.extend(transaction_dialogs["test_oot"])

transaction_dialogs_all.extend(transaction_dialogs_turn_compression["test"])
transaction_dialogs_all.extend(transaction_dialogs_turn_compression["test_oot"])

transaction_dialogs_all.extend(transaction_dialogs_new_api["test"])
transaction_dialogs_all.extend(transaction_dialogs_new_api["test_oot"])

transaction_dialogs_all.extend(transaction_dialogs_re_order["test"])
transaction_dialogs_all.extend(transaction_dialogs_re_order["test_oot"])

transaction_dialogs_all.extend(transaction_dialogs_another_slot["test"])
transaction_dialogs_all.extend(transaction_dialogs_another_slot["test_oot"])

transaction_dialogs_all.extend(transaction_dialogs_audit_more["test"])
transaction_dialogs_all.extend(transaction_dialogs_audit_more["test_oot"])

random.shuffle(transaction_dialogs_all)



account_balance_dialogs_all = list()

account_balance_dialogs_all.extend(account_balance_dialogs["train"])
account_balance_dialogs_all.extend(account_balance_dialogs["val"])

account_balance_dialogs_all.extend(account_balance_dialogs["test"])
account_balance_dialogs_all.extend(account_balance_dialogs["test_oot"])

account_balance_dialogs_all.extend(account_balance_dialogs_turn_compression["test"])
account_balance_dialogs_all.extend(account_balance_dialogs_turn_compression["test_oot"])

account_balance_dialogs_all.extend(account_balance_dialogs_new_api["test"])
account_balance_dialogs_all.extend(account_balance_dialogs_new_api["test_oot"])

account_balance_dialogs_all.extend(account_balance_dialogs_re_order["test"])
account_balance_dialogs_all.extend(account_balance_dialogs_re_order["test_oot"])

account_balance_dialogs_all.extend(account_balance_dialogs_another_slot["test"])
account_balance_dialogs_all.extend(account_balance_dialogs_another_slot["test_oot"])

account_balance_dialogs_all.extend(account_balance_dialogs_audit_more["test"])
account_balance_dialogs_all.extend(account_balance_dialogs_audit_more["test_oot"])

random.shuffle(account_balance_dialogs_all)



account_limit_dialogs_all = list()

account_limit_dialogs_all.extend(account_limit_dialogs["train"])
account_limit_dialogs_all.extend(account_limit_dialogs["val"])

account_limit_dialogs_all.extend(account_limit_dialogs["test"])
account_limit_dialogs_all.extend(account_limit_dialogs["test_oot"])

account_limit_dialogs_all.extend(account_limit_dialogs_turn_compression["test"])
account_limit_dialogs_all.extend(account_limit_dialogs_turn_compression["test_oot"])

account_limit_dialogs_all.extend(account_limit_dialogs_new_api["test"])
account_limit_dialogs_all.extend(account_limit_dialogs_new_api["test_oot"])

account_limit_dialogs_all.extend(account_limit_dialogs_re_order["test"])
account_limit_dialogs_all.extend(account_limit_dialogs_re_order["test_oot"])

account_limit_dialogs_all.extend(account_limit_dialogs_another_slot["test"])
account_limit_dialogs_all.extend(account_limit_dialogs_another_slot["test_oot"])

account_limit_dialogs_all.extend(account_limit_dialogs_audit_more["test"])
account_limit_dialogs_all.extend(account_limit_dialogs_audit_more["test_oot"])

random.shuffle(account_limit_dialogs_all)


block_card_dialogs_all = list()

block_card_dialogs_all.extend(block_card_dialogs["train"])
block_card_dialogs_all.extend(block_card_dialogs["val"])

block_card_dialogs_all.extend(block_card_dialogs["test"])
block_card_dialogs_all.extend(block_card_dialogs["test_oot"])

block_card_dialogs_all.extend(block_card_dialogs_turn_compression["test"])
block_card_dialogs_all.extend(block_card_dialogs_turn_compression["test_oot"])

block_card_dialogs_all.extend(block_card_dialogs_new_api["test"])
block_card_dialogs_all.extend(block_card_dialogs_new_api["test_oot"])

block_card_dialogs_all.extend(block_card_dialogs_re_order["test"])
block_card_dialogs_all.extend(block_card_dialogs_re_order["test_oot"])

block_card_dialogs_all.extend(block_card_dialogs_another_slot["test"])
block_card_dialogs_all.extend(block_card_dialogs_another_slot["test_oot"])

block_card_dialogs_all.extend(block_card_dialogs_audit_more["test"])
block_card_dialogs_all.extend(block_card_dialogs_audit_more["test_oot"])

random.shuffle(block_card_dialogs_all)


cancel_transaction_dialogs_all = list()

cancel_transaction_dialogs_all.extend(cancel_transaction_dialogs["train"])
cancel_transaction_dialogs_all.extend(cancel_transaction_dialogs["val"])

cancel_transaction_dialogs_all.extend(cancel_transaction_dialogs["test"])
cancel_transaction_dialogs_all.extend(cancel_transaction_dialogs["test_oot"])

cancel_transaction_dialogs_all.extend(cancel_transaction_dialogs_turn_compression["test"])
cancel_transaction_dialogs_all.extend(cancel_transaction_dialogs_turn_compression["test_oot"])

cancel_transaction_dialogs_all.extend(cancel_transaction_dialogs_new_api["test"])
cancel_transaction_dialogs_all.extend(cancel_transaction_dialogs_new_api["test_oot"])

cancel_transaction_dialogs_all.extend(cancel_transaction_dialogs_re_order["test"])
cancel_transaction_dialogs_all.extend(cancel_transaction_dialogs_re_order["test_oot"])

cancel_transaction_dialogs_all.extend(cancel_transaction_dialogs_another_slot["test"])
cancel_transaction_dialogs_all.extend(cancel_transaction_dialogs_another_slot["test_oot"])

cancel_transaction_dialogs_all.extend(cancel_transaction_dialogs_audit_more["test"])
cancel_transaction_dialogs_all.extend(cancel_transaction_dialogs_audit_more["test_oot"])

random.shuffle(cancel_transaction_dialogs_all)



search_note_dialogs_all = list()

search_note_dialogs_all.extend(search_note_dialogs["train"])
search_note_dialogs_all.extend(search_note_dialogs["val"])

search_note_dialogs_all.extend(search_note_dialogs["test"])
search_note_dialogs_all.extend(search_note_dialogs["test_oot"])

search_note_dialogs_all.extend(search_note_dialogs_turn_compression["test"])
search_note_dialogs_all.extend(search_note_dialogs_turn_compression["test_oot"])

search_note_dialogs_all.extend(search_note_dialogs_new_api["test"])
search_note_dialogs_all.extend(search_note_dialogs_new_api["test_oot"])

search_note_dialogs_all.extend(search_note_dialogs_re_order["test"])
search_note_dialogs_all.extend(search_note_dialogs_re_order["test_oot"])

search_note_dialogs_all.extend(search_note_dialogs_another_slot["test"])
search_note_dialogs_all.extend(search_note_dialogs_another_slot["test_oot"])

search_note_dialogs_all.extend(search_note_dialogs_audit_more["test"])
search_note_dialogs_all.extend(search_note_dialogs_audit_more["test_oot"])

random.shuffle(search_note_dialogs_all)


special_dialogs_train = create_special_dialog(dialogs=dialogs_train)
special_dialogs_val = create_special_dialog(dialogs=dialogs_val)


special_dialogs_test = create_special_dialog(dialogs=dialogs_test)
special_dialogs_test_oot = create_special_dialog(dialogs=dialogs_test_oot)

special_dialogs_turn_compression_test = create_special_dialog(dialogs=dialogs_turn_compression_test)
special_dialogs_turn_compression_test_oot = create_special_dialog(dialogs=dialogs_turn_compression_test_oot)

special_dialogs_new_api_test = create_special_dialog(dialogs=dialogs_new_api_test)
special_dialogs_new_api_test_oot = create_special_dialog(dialogs=dialogs_new_api_test_oot)

special_dialogs_re_order_test = create_special_dialog(dialogs=dialogs_re_order_test)
special_dialogs_re_order_test_oot = create_special_dialog(dialogs=dialogs_re_order_test_oot)

special_dialogs_another_slot_test = create_special_dialog(dialogs=dialogs_another_slot_test)
special_dialogs_another_slot_test_oot = create_special_dialog(dialogs=dialogs_another_slot_test_oot)

special_dialogs_audit_more_test = create_special_dialog(dialogs=dialogs_audit_more_test)
special_dialogs_audit_more_test_oot = create_special_dialog(dialogs=dialogs_audit_more_test_oot)


special_transaction_dialogs_train = create_special_dialog(dialogs=transaction_dialogs["train"])
special_transaction_dialogs_val = create_special_dialog(dialogs=transaction_dialogs["val"])



special_transaction_dialogs_test = create_special_dialog(dialogs=transaction_dialogs["test"])
special_transaction_dialogs_test_oot = create_special_dialog(dialogs=transaction_dialogs["test_oot"])

special_transaction_dialogs_turn_compression_test = create_special_dialog(dialogs=transaction_dialogs_turn_compression["test"])
special_transaction_dialogs_turn_compression_test_oot = create_special_dialog(dialogs=transaction_dialogs_turn_compression["test_oot"])

special_transaction_dialogs_new_api_test = create_special_dialog(dialogs=transaction_dialogs_new_api["test"])
special_transaction_dialogs_new_api_test_oot = create_special_dialog(dialogs=transaction_dialogs_new_api["test_oot"])

special_transaction_dialogs_re_order_test = create_special_dialog(dialogs=transaction_dialogs_re_order["test"])
special_transaction_dialogs_re_order_test_oot = create_special_dialog(dialogs=transaction_dialogs_re_order["test_oot"])

special_transaction_dialogs_another_slot_test = create_special_dialog(dialogs=transaction_dialogs_another_slot["test"])
special_transaction_dialogs_another_slot_test_oot = create_special_dialog(dialogs=transaction_dialogs_another_slot["test_oot"])

special_transaction_dialogs_audit_more_test = create_special_dialog(dialogs=transaction_dialogs_audit_more["test"])
special_transaction_dialogs_audit_more_test_oot = create_special_dialog(dialogs=transaction_dialogs_audit_more["test_oot"])



special_account_balance_dialogs_train = create_special_dialog(dialogs=account_balance_dialogs["train"])
special_account_balance_dialogs_val = create_special_dialog(dialogs=account_balance_dialogs["val"])




special_account_balance_dialogs_test = create_special_dialog(dialogs=account_balance_dialogs["test"])
special_account_balance_dialogs_test_oot = create_special_dialog(dialogs=account_balance_dialogs["test_oot"])

special_account_balance_dialogs_turn_compression_test = create_special_dialog(dialogs=account_balance_dialogs_turn_compression["test"])
special_account_balance_dialogs_turn_compression_test_oot = create_special_dialog(dialogs=account_balance_dialogs_turn_compression["test_oot"])

special_account_balance_dialogs_new_api_test = create_special_dialog(dialogs=account_balance_dialogs_new_api["test"])
special_account_balance_dialogs_new_api_test_oot = create_special_dialog(dialogs=account_balance_dialogs_new_api["test_oot"])

special_account_balance_dialogs_re_order_test = create_special_dialog(dialogs=account_balance_dialogs_re_order["test"])
special_account_balance_dialogs_re_order_test_oot = create_special_dialog(dialogs=account_balance_dialogs_re_order["test_oot"])

special_account_balance_dialogs_another_slot_test = create_special_dialog(dialogs=account_balance_dialogs_another_slot["test"])
special_account_balance_dialogs_another_slot_test_oot = create_special_dialog(dialogs=account_balance_dialogs_another_slot["test_oot"])

special_account_balance_dialogs_audit_more_test = create_special_dialog(dialogs=account_balance_dialogs_audit_more["test"])
special_account_balance_dialogs_audit_more_test_oot = create_special_dialog(dialogs=account_balance_dialogs_audit_more["test_oot"])



special_account_limit_dialogs_train = create_special_dialog(dialogs=account_limit_dialogs["train"])
special_account_limit_dialogs_val = create_special_dialog(dialogs=account_limit_dialogs["val"])


special_account_limit_dialogs_test = create_special_dialog(dialogs=account_limit_dialogs["test"])
special_account_limit_dialogs_test_oot = create_special_dialog(dialogs=account_limit_dialogs["test_oot"])

special_account_limit_dialogs_turn_compression_test = create_special_dialog(dialogs=account_limit_dialogs_turn_compression["test"])
special_account_limit_dialogs_turn_compression_test_oot = create_special_dialog(dialogs=account_limit_dialogs_turn_compression["test_oot"])

special_account_limit_dialogs_new_api_test = create_special_dialog(dialogs=account_limit_dialogs_new_api["test"])
special_account_limit_dialogs_new_api_test_oot = create_special_dialog(dialogs=account_limit_dialogs_new_api["test_oot"])

special_account_limit_dialogs_re_order_test = create_special_dialog(dialogs=account_limit_dialogs_re_order["test"])
special_account_limit_dialogs_re_order_test_oot = create_special_dialog(dialogs=account_limit_dialogs_re_order["test_oot"])

special_account_limit_dialogs_another_slot_test = create_special_dialog(dialogs=account_limit_dialogs_another_slot["test"])
special_account_limit_dialogs_another_slot_test_oot = create_special_dialog(dialogs=account_limit_dialogs_another_slot["test_oot"])

special_account_limit_dialogs_audit_more_test = create_special_dialog(dialogs=account_limit_dialogs_audit_more["test"])
special_account_limit_dialogs_audit_more_test_oot = create_special_dialog(dialogs=account_limit_dialogs_audit_more["test_oot"])


special_block_card_dialogs_train = create_special_dialog(dialogs=block_card_dialogs["test"])
special_block_card_dialogs_val = create_special_dialog(dialogs=block_card_dialogs["test_oot"])



special_block_card_dialogs_test = create_special_dialog(dialogs=block_card_dialogs["test"])
special_block_card_dialogs_test_oot = create_special_dialog(dialogs=block_card_dialogs["test_oot"])

special_block_card_dialogs_turn_compression_test = create_special_dialog(dialogs=block_card_dialogs_turn_compression["test"])
special_block_card_dialogs_turn_compression_test_oot = create_special_dialog(dialogs=block_card_dialogs_turn_compression["test_oot"])

special_block_card_dialogs_new_api_test = create_special_dialog(dialogs=block_card_dialogs_new_api["test"])
special_block_card_dialogs_new_api_test_oot = create_special_dialog(dialogs=block_card_dialogs_new_api["test_oot"])

special_block_card_dialogs_re_order_test = create_special_dialog(dialogs=block_card_dialogs_re_order["test"])
special_block_card_dialogs_re_order_test_oot = create_special_dialog(dialogs=block_card_dialogs_re_order["test_oot"])

special_block_card_dialogs_another_slot_test = create_special_dialog(dialogs=block_card_dialogs_another_slot["test"])
special_block_card_dialogs_another_slot_test_oot = create_special_dialog(dialogs=block_card_dialogs_another_slot["test_oot"])

special_block_card_dialogs_audit_more_test = create_special_dialog(dialogs=block_card_dialogs_audit_more["test"])
special_block_card_dialogs_audit_more_test_oot = create_special_dialog(dialogs=block_card_dialogs_audit_more["test_oot"])


special_cancel_transaction_dialogs_train = create_special_dialog(dialogs=cancel_transaction_dialogs["train"])
special_cancel_transaction_dialogs_val = create_special_dialog(dialogs=cancel_transaction_dialogs["val"])


special_cancel_transaction_dialogs_test = create_special_dialog(dialogs=cancel_transaction_dialogs["test"])
special_cancel_transaction_dialogs_test_oot = create_special_dialog(dialogs=cancel_transaction_dialogs["test_oot"])

special_cancel_transaction_dialogs_turn_compression_test = create_special_dialog(dialogs=cancel_transaction_dialogs_turn_compression["test"])
special_cancel_transaction_dialogs_turn_compression_test_oot = create_special_dialog(dialogs=cancel_transaction_dialogs_turn_compression["test_oot"])

special_cancel_transaction_dialogs_new_api_test = create_special_dialog(dialogs=cancel_transaction_dialogs_new_api["test"])
special_cancel_transaction_dialogs_new_api_test_oot = create_special_dialog(dialogs=cancel_transaction_dialogs_new_api["test_oot"])

special_cancel_transaction_dialogs_re_order_test = create_special_dialog(dialogs=cancel_transaction_dialogs_re_order["test"])
special_cancel_transaction_dialogs_re_order_test_oot = create_special_dialog(dialogs=cancel_transaction_dialogs_re_order["test_oot"])

special_cancel_transaction_dialogs_another_slot_test = create_special_dialog(dialogs=cancel_transaction_dialogs_another_slot["test"])
special_cancel_transaction_dialogs_another_slot_test_oot = create_special_dialog(dialogs=cancel_transaction_dialogs_another_slot["test_oot"])

special_cancel_transaction_dialogs_audit_more_test = create_special_dialog(dialogs=cancel_transaction_dialogs_audit_more["test"])
special_cancel_transaction_dialogs_audit_more_test_oot = create_special_dialog(dialogs=cancel_transaction_dialogs_audit_more["test_oot"])


special_search_note_dialogs_train = create_special_dialog(dialogs=search_note_dialogs["train"])
special_search_note_dialogs_val = create_special_dialog(dialogs=search_note_dialogs["val"])


special_search_note_dialogs_test = create_special_dialog(dialogs=search_note_dialogs["test"])
special_search_note_dialogs_test_oot = create_special_dialog(dialogs=search_note_dialogs["test_oot"])

special_search_note_dialogs_turn_compression_test = create_special_dialog(dialogs=search_note_dialogs_turn_compression["test"])
special_search_note_dialogs_turn_compression_test_oot = create_special_dialog(dialogs=search_note_dialogs_turn_compression["test_oot"])

special_search_note_dialogs_new_api_test = create_special_dialog(dialogs=search_note_dialogs_new_api["test"])
special_search_note_dialogs_new_api_test_oot = create_special_dialog(dialogs=search_note_dialogs_new_api["test_oot"])

special_search_note_dialogs_re_order_test = create_special_dialog(dialogs=search_note_dialogs_re_order["test"])
special_search_note_dialogs_re_order_test_oot = create_special_dialog(dialogs=search_note_dialogs_re_order["test_oot"])

special_search_note_dialogs_another_slot_test = create_special_dialog(dialogs=search_note_dialogs_another_slot["test"])
special_search_note_dialogs_another_slot_test_oot = create_special_dialog(dialogs=search_note_dialogs_another_slot["test_oot"])

special_search_note_dialogs_audit_more_test = create_special_dialog(dialogs=search_note_dialogs_audit_more["test"])
special_search_note_dialogs_audit_more_test_oot = create_special_dialog(dialogs=search_note_dialogs_audit_more["test_oot"])



create_raw_data(file_directory="../data/transaction_data/",file_name="raw_data_train.txt",dialogs=transaction_dialogs["train"])
create_raw_data(file_directory="../data/transaction_data/",file_name="raw_data_val.txt",dialogs=transaction_dialogs["val"])


create_raw_data(file_directory="../data/transaction_data/test/",file_name="raw_data_test.txt",dialogs=transaction_dialogs["test"])
create_raw_data(file_directory="../data/transaction_data/test/",file_name="raw_data_test_oot.txt",dialogs=transaction_dialogs["test_oot"])

create_raw_data(file_directory="../data/transaction_data/test/",file_name="raw_data_turn_compression_test.txt",dialogs=transaction_dialogs_turn_compression["test"])
create_raw_data(file_directory="../data/transaction_data/test/",file_name="raw_data_turn_compression_test_oot.txt",dialogs=transaction_dialogs_turn_compression["test_oot"])

create_raw_data(file_directory="../data/transaction_data/test/",file_name="raw_data_new_api_test.txt",dialogs=transaction_dialogs_new_api["test"])
create_raw_data(file_directory="../data/transaction_data/test/",file_name="raw_data_new_api_test_oot.txt",dialogs=transaction_dialogs_new_api["test_oot"])

create_raw_data(file_directory="../data/transaction_data/test/",file_name="raw_data_re_order_test.txt",dialogs=transaction_dialogs_re_order["test"])
create_raw_data(file_directory="../data/transaction_data/test/",file_name="raw_data_re_order_test_oot.txt",dialogs=transaction_dialogs_re_order["test_oot"])

create_raw_data(file_directory="../data/transaction_data/test/",file_name="raw_data_another_slot_test.txt",dialogs=transaction_dialogs_another_slot["test"])
create_raw_data(file_directory="../data/transaction_data/test/",file_name="raw_data_another_slot_test_oot.txt",dialogs=transaction_dialogs_another_slot["test_oot"])

create_raw_data(file_directory="../data/transaction_data/test/",file_name="raw_data_audit_more_test.txt",dialogs=transaction_dialogs_audit_more["test"])
create_raw_data(file_directory="../data/transaction_data/test/",file_name="raw_data_audit_more_test_oot.txt",dialogs=transaction_dialogs_audit_more["test_oot"])


create_raw_data(file_directory="../data/account_balance_data/",file_name="raw_data_train.txt",dialogs=account_balance_dialogs["train"])
create_raw_data(file_directory="../data/account_balance_data/",file_name="raw_data_val.txt",dialogs=account_balance_dialogs["val"])


create_raw_data(file_directory="../data/account_balance_data/test/",file_name="raw_data_test.txt",dialogs=account_balance_dialogs["test"])
create_raw_data(file_directory="../data/account_balance_data/test/",file_name="raw_data_test_oot.txt",dialogs=account_balance_dialogs["test_oot"])

create_raw_data(file_directory="../data/account_balance_data/test/",file_name="raw_data_turn_compression_test.txt",dialogs=account_balance_dialogs_turn_compression["test"])
create_raw_data(file_directory="../data/account_balance_data/test/",file_name="raw_data_turn_compression_test_oot.txt",dialogs=account_balance_dialogs_turn_compression["test_oot"])

create_raw_data(file_directory="../data/account_balance_data/test/",file_name="raw_data_new_api_test.txt",dialogs=account_balance_dialogs_new_api["test"])
create_raw_data(file_directory="../data/account_balance_data/test/",file_name="raw_data_new_api_test_oot.txt",dialogs=account_balance_dialogs["test_oot"])

create_raw_data(file_directory="../data/account_balance_data/test/",file_name="raw_data_re_order_test.txt",dialogs=account_balance_dialogs_re_order["test"])
create_raw_data(file_directory="../data/account_balance_data/test/",file_name="raw_data_re_order_test_oot.txt",dialogs=account_balance_dialogs_re_order["test_oot"])

create_raw_data(file_directory="../data/account_balance_data/test/",file_name="raw_data_another_slot_test.txt",dialogs=account_balance_dialogs_another_slot["test"])
create_raw_data(file_directory="../data/account_balance_data/test/",file_name="raw_data_another_slot_test_oot.txt",dialogs=account_balance_dialogs_another_slot["test_oot"])

create_raw_data(file_directory="../data/account_balance_data/test/",file_name="raw_data_audit_more_test.txt",dialogs=account_balance_dialogs_audit_more["test"])
create_raw_data(file_directory="../data/account_balance_data/test/",file_name="raw_data_audit_more_test_oot.txt",dialogs=account_balance_dialogs_audit_more["test_oot"])


create_raw_data(file_directory="../data/account_limit_data/",file_name="raw_data_train.txt",dialogs=account_limit_dialogs["train"])
create_raw_data(file_directory="../data/account_limit_data/",file_name="raw_data_val.txt",dialogs=account_limit_dialogs["val"])


create_raw_data(file_directory="../data/account_limit_data/test/",file_name="raw_data_test.txt",dialogs=account_limit_dialogs["test"])
create_raw_data(file_directory="../data/account_limit_data/test/",file_name="raw_data_test_oot.txt",dialogs=account_limit_dialogs["test_oot"])

create_raw_data(file_directory="../data/account_limit_data/test/",file_name="raw_data_turn_compression_test.txt",dialogs=account_limit_dialogs_turn_compression["test"])
create_raw_data(file_directory="../data/account_limit_data/test/",file_name="raw_data_turn_compression_test_oot.txt",dialogs=account_limit_dialogs_turn_compression["test_oot"])

create_raw_data(file_directory="../data/account_limit_data/test/",file_name="raw_data_new_api_test.txt",dialogs=account_limit_dialogs_new_api["test"])
create_raw_data(file_directory="../data/account_limit_data/test/",file_name="raw_data_new_api_test_oot.txt",dialogs=account_limit_dialogs_new_api["test_oot"])

create_raw_data(file_directory="../data/account_limit_data/test/",file_name="raw_data_re_order_test.txt",dialogs=account_limit_dialogs_re_order["test"])
create_raw_data(file_directory="../data/account_limit_data/test/",file_name="raw_data_re_order_test_oot.txt",dialogs=account_limit_dialogs_re_order["test_oot"])

create_raw_data(file_directory="../data/account_limit_data/test/",file_name="raw_data_another_slot_test.txt",dialogs=account_limit_dialogs_another_slot["test"])
create_raw_data(file_directory="../data/account_limit_data/test/",file_name="raw_data_another_slot_test_oot.txt",dialogs=account_limit_dialogs_another_slot["test_oot"])

create_raw_data(file_directory="../data/account_limit_data/test/",file_name="raw_data_audit_more_test.txt",dialogs=account_limit_dialogs_audit_more["test"])
create_raw_data(file_directory="../data/account_limit_data/test/",file_name="raw_data_audit_more_test_oot.txt",dialogs=account_limit_dialogs_audit_more["test_oot"])



create_raw_data(file_directory="../data/block_card_data/",file_name="raw_data_train.txt",dialogs=block_card_dialogs["train"])
create_raw_data(file_directory="../data/block_card_data/",file_name="raw_data_val.txt",dialogs=block_card_dialogs["val"])



create_raw_data(file_directory="../data/block_card_data/test/",file_name="raw_data_test.txt",dialogs=block_card_dialogs["test"])
create_raw_data(file_directory="../data/block_card_data/test/",file_name="raw_data_test_oot.txt",dialogs=block_card_dialogs["test_oot"])

create_raw_data(file_directory="../data/block_card_data/test/",file_name="raw_data_test_turn_compression.txt",dialogs=block_card_dialogs_turn_compression["test"])
create_raw_data(file_directory="../data/block_card_data/test/",file_name="raw_data_test_turn_compression_oot.txt",dialogs=block_card_dialogs_turn_compression["test_oot"])

create_raw_data(file_directory="../data/block_card_data/test",file_name="raw_data_test_new_api.txt",dialogs=block_card_dialogs_new_api["test"])
create_raw_data(file_directory="../data/block_card_data/test/",file_name="raw_data_test_new_api_oot.txt",dialogs=block_card_dialogs_new_api["test_oot"])

create_raw_data(file_directory="../data/block_card_data/test/",file_name="raw_data_test_re_order.txt",dialogs=block_card_dialogs_re_order["test"])
create_raw_data(file_directory="../data/block_card_data/test/",file_name="raw_data_test_re_order_oot.txt",dialogs=block_card_dialogs_re_order["test_oot"])

create_raw_data(file_directory="../data/block_card_data/test/",file_name="raw_data_test_another_slot.txt",dialogs=block_card_dialogs_another_slot["test"])
create_raw_data(file_directory="../data/block_card_data/test/",file_name="raw_data_test_another_slot_oot.txt",dialogs=block_card_dialogs_another_slot["test_oot"])

create_raw_data(file_directory="../data/block_card_data/test/",file_name="raw_data_test_audit_more.txt",dialogs=block_card_dialogs_audit_more["test"])
create_raw_data(file_directory="../data/block_card_data/test/",file_name="raw_data_test_audit_more_oot.txt",dialogs=block_card_dialogs_audit_more["test_oot"])


create_raw_data(file_directory="../data/cancel_transaction_data/",file_name="raw_data_train.txt",dialogs=cancel_transaction_dialogs["train"])
create_raw_data(file_directory="../data/cancel_transaction_data/",file_name="raw_data_val.txt",dialogs=cancel_transaction_dialogs["val"])


create_raw_data(file_directory="../data/cancel_transaction_data/test/",file_name="raw_data_test.txt",dialogs=cancel_transaction_dialogs["test"])
create_raw_data(file_directory="../data/cancel_transaction_data/test/",file_name="raw_data_test_oot.txt",dialogs=cancel_transaction_dialogs["test_oot"])

create_raw_data(file_directory="../data/cancel_transaction_data/test/",file_name="raw_data_turn_compression_test.txt",dialogs=cancel_transaction_dialogs_turn_compression["test"])
create_raw_data(file_directory="../data/cancel_transaction_data/test/",file_name="raw_data_turn_compression_test_oot.txt",dialogs=cancel_transaction_dialogs_turn_compression["test_oot"])

create_raw_data(file_directory="../data/cancel_transaction_data/test/",file_name="raw_data_new_api_test.txt",dialogs=cancel_transaction_dialogs_new_api["test"])
create_raw_data(file_directory="../data/cancel_transaction_data/test/",file_name="raw_data_new_api_test_oot.txt",dialogs=cancel_transaction_dialogs_new_api["test_oot"])

create_raw_data(file_directory="../data/cancel_transaction_data/test/",file_name="raw_data_re_order_test.txt",dialogs=cancel_transaction_dialogs_re_order["test"])
create_raw_data(file_directory="../data/cancel_transaction_data/test/",file_name="raw_data_re_order_test_oot.txt",dialogs=cancel_transaction_dialogs_re_order["test_oot"])

create_raw_data(file_directory="../data/cancel_transaction_data/test/",file_name="raw_data_another_slot_test.txt",dialogs=cancel_transaction_dialogs_another_slot["test"])
create_raw_data(file_directory="../data/cancel_transaction_data/test/",file_name="raw_data_another_slot_test_oot.txt",dialogs=cancel_transaction_dialogs_another_slot["test_oot"])

create_raw_data(file_directory="../data/cancel_transaction_data/test/",file_name="raw_data_audit_more_test.txt",dialogs=cancel_transaction_dialogs_audit_more["test"])
create_raw_data(file_directory="../data/cancel_transaction_data/test/",file_name="raw_data_audit_more_test_oot.txt",dialogs=cancel_transaction_dialogs_audit_more["test_oot"])


create_raw_data(file_directory="../data/search_note_data/",file_name="raw_data_train.txt",dialogs=search_note_dialogs["train"])
create_raw_data(file_directory="../data/search_note_data/",file_name="raw_data_val.txt",dialogs=search_note_dialogs["val"])


create_raw_data(file_directory="../data/search_note_data/test/",file_name="raw_data_test.txt",dialogs=search_note_dialogs["test"])
create_raw_data(file_directory="../data/search_note_data/test/",file_name="raw_data_test_oot.txt",dialogs=search_note_dialogs["test_oot"])

create_raw_data(file_directory="../data/search_note_data/test/",file_name="raw_data_turn_compression_test.txt",dialogs=search_note_dialogs_turn_compression["test"])
create_raw_data(file_directory="../data/search_note_data/test/",file_name="raw_data_turn_compression_test_oot.txt",dialogs=search_note_dialogs_turn_compression["test_oot"])

create_raw_data(file_directory="../data/search_note_data/test/",file_name="raw_data_new_api_test.txt",dialogs=search_note_dialogs_new_api["test"])
create_raw_data(file_directory="../data/search_note_data/test/",file_name="raw_data_new_api_test_oot.txt",dialogs=search_note_dialogs_new_api["test_oot"])

create_raw_data(file_directory="../data/search_note_data/test/",file_name="raw_data_re_order_test.txt",dialogs=search_note_dialogs_re_order["test"])
create_raw_data(file_directory="../data/search_note_data/test/",file_name="raw_data_re_order_test_oot.txt",dialogs=search_note_dialogs_re_order["test_oot"])

create_raw_data(file_directory="../data/search_note_data/test/",file_name="raw_data_another_slot_test.txt",dialogs=search_note_dialogs_another_slot["test"])
create_raw_data(file_directory="../data/search_note_data/test/",file_name="raw_data_another_slot_test_oot.txt",dialogs=search_note_dialogs_another_slot["test_oot"])

create_raw_data(file_directory="../data/search_note_data/test/",file_name="raw_data_audit_more_test.txt",dialogs=search_note_dialogs_audit_more["test"])
create_raw_data(file_directory="../data/search_note_data/test/",file_name="raw_data_audit_more_test_oot.txt",dialogs=search_note_dialogs_audit_more["test_oot"])



create_raw_data(file_directory="../data/start_data/",file_name="raw_data_train.txt",dialogs=start_dialogs_train)
create_raw_data(file_directory="../data/start_data/",file_name="raw_data_val.txt",dialogs=start_dialogs_val)


create_raw_data(file_directory="../data/start_data/test/",file_name="raw_data_test.txt",dialogs=start_dialogs_test)
create_raw_data(file_directory="../data/start_data/test/",file_name="raw_data_test_oot.txt",dialogs=start_dialogs_test_oot)

create_raw_data(file_directory="../data/start_data/test/",file_name="raw_data_turn_compression_test.txt",dialogs=start_dialogs_turn_compression_test)
create_raw_data(file_directory="../data/start_data/test/",file_name="raw_data_turn_compression_test_oot.txt",dialogs=start_dialogs_turn_compression_test_oot)

create_raw_data(file_directory="../data/start_data/test/",file_name="raw_data_new_api_test.txt",dialogs=start_dialogs_new_api_test)
create_raw_data(file_directory="../data/start_data/test/",file_name="raw_data_new_api_test_oot.txt",dialogs=start_dialogs_new_api_test_oot)

create_raw_data(file_directory="../data/start_data/test/",file_name="raw_data_re_order_test.txt",dialogs=start_dialogs_re_order_test)
create_raw_data(file_directory="../data/start_data/test/",file_name="raw_data_re_order_test_oot.txt",dialogs=start_dialogs_re_order_test_oot)

create_raw_data(file_directory="../data/start_data/test/",file_name="raw_data_another_slot_test.txt",dialogs=start_dialogs_another_slot_test)
create_raw_data(file_directory="../data/start_data/test/",file_name="raw_data_another_slot_test_oot.txt",dialogs=start_dialogs_another_slot_test_oot)

create_raw_data(file_directory="../data/start_data/test/",file_name="raw_data_audit_more_test.txt",dialogs=start_dialogs_audit_more_test)
create_raw_data(file_directory="../data/start_data/test/",file_name="raw_data_audit_more_test_oot.txt",dialogs=start_dialogs_audit_more_test_oot)


create_raw_data(file_directory="../data/one_data/",file_name="raw_data_train.txt",dialogs=one_dialogs_train)
create_raw_data(file_directory="../data/one_data/",file_name="raw_data_val.txt",dialogs=one_dialogs_val)


create_raw_data(file_directory="../data/one_data/test/",file_name="raw_data_test.txt",dialogs=one_dialogs_test)
create_raw_data(file_directory="../data/one_data/test/",file_name="raw_data_test_oot.txt",dialogs=one_dialogs_test_oot)

create_raw_data(file_directory="../data/one_data/test/",file_name="raw_data_turn_compression_test.txt",dialogs=one_dialogs_turn_compression_test)
create_raw_data(file_directory="../data/one_data/test/",file_name="raw_data_turn_compression_test_oot.txt",dialogs=one_dialogs_turn_compression_test_oot)

create_raw_data(file_directory="../data/one_data/test/",file_name="raw_data_new_api_test.txt",dialogs=one_dialogs_new_api_test)
create_raw_data(file_directory="../data/one_data/test/",file_name="raw_data_new_api_test_oot.txt",dialogs=one_dialogs_new_api_test_oot)

create_raw_data(file_directory="../data/one_data/test/",file_name="raw_data_re_order_test.txt",dialogs=one_dialogs_re_order_test)
create_raw_data(file_directory="../data/one_data/test/",file_name="raw_data_re_order_test_oot.txt",dialogs=one_dialogs_re_order_test_oot)

create_raw_data(file_directory="../data/one_data/test/",file_name="raw_data_another_slot_test.txt",dialogs=one_dialogs_another_slot_test)
create_raw_data(file_directory="../data/one_data/test/",file_name="raw_data_another_slot_test_oot.txt",dialogs=one_dialogs_another_slot_test_oot)

create_raw_data(file_directory="../data/one_data/test/",file_name="raw_data_test_audit_more.txt",dialogs=one_dialogs_audit_more_test)
create_raw_data(file_directory="../data/one_data/test/",file_name="raw_data_test_audit_more_oot.txt",dialogs=one_dialogs_audit_more_test_oot)



create_training_data(file_directory="../data/transaction_data/",file_name="train_data.txt",dialogs=transaction_dialogs["train"])
create_training_data(file_directory="../data/transaction_data/",file_name="val_data.txt",dialogs=transaction_dialogs["val"])


create_training_data(file_directory="../data/transaction_data/test/",file_name="test_data.txt",dialogs=transaction_dialogs["test"])
create_training_data(file_directory="../data/transaction_data/test/",file_name="test_data_oot.txt",dialogs=transaction_dialogs["test_oot"])

create_training_data(file_directory="../data/transaction_data/test/",file_name="test_data_turn_compression_test.txt",dialogs=transaction_dialogs_turn_compression["test"])
create_training_data(file_directory="../data/transaction_data/test",file_name="test_data_turn_compression_test_oot.txt",dialogs=transaction_dialogs_turn_compression["test_oot"])

create_training_data(file_directory="../data/transaction_data/test/",file_name="test_data_new_api_test.txt",dialogs=transaction_dialogs_new_api["test"])
create_training_data(file_directory="../data/transaction_data/test",file_name="test_data_new_api_test_oot.txt",dialogs=transaction_dialogs_new_api["test_oot"])

create_training_data(file_directory="../data/transaction_data/test/",file_name="test_data_re_order_test.txt",dialogs=transaction_dialogs_re_order["test"])
create_training_data(file_directory="../data/transaction_data/test",file_name="test_data_re_order_test_oot.txt",dialogs=transaction_dialogs_re_order["test_oot"])

create_training_data(file_directory="../data/transaction_data/test/",file_name="test_data_another_slot_test.txt",dialogs=transaction_dialogs_another_slot["test"])
create_training_data(file_directory="../data/transaction_data/test/",file_name="test_data_another_slot_test_oot.txt",dialogs=transaction_dialogs_another_slot["test_oot"])

create_training_data(file_directory="../data/transaction_data/test/",file_name="test_data_audit_more_test.txt",dialogs=transaction_dialogs_audit_more["test"])
create_training_data(file_directory="../data/transaction_data/test/",file_name="test_data_audit_more_test_oot.txt",dialogs=transaction_dialogs_audit_more["test_oot"])



create_training_data(file_directory="../data/account_balance_data/",file_name="train_data.txt",dialogs=account_balance_dialogs["train"])
create_training_data(file_directory="../data/account_balance_data/",file_name="val_data.txt",dialogs=account_balance_dialogs["val"])



create_training_data(file_directory="../data/account_balance_data/test/",file_name="test_data.txt",dialogs=account_balance_dialogs["test"])
create_training_data(file_directory="../data/account_balance_data/test/",file_name="test_data_oot.txt",dialogs=account_balance_dialogs["test_oot"])

create_training_data(file_directory="../data/account_balance_data/test/",file_name="test_data_turn_compression.txt",dialogs=account_balance_dialogs_turn_compression["test"])
create_training_data(file_directory="../data/account_balance_data/test/",file_name="test_data_turn_compression_oot.txt",dialogs=account_balance_dialogs_turn_compression["test_oot"])

create_training_data(file_directory="../data/account_balance_data/test/",file_name="test_data_new_api.txt",dialogs=account_balance_dialogs_new_api["test"])
create_training_data(file_directory="../data/account_balance_data/test/",file_name="test_data_new_api_oot.txt",dialogs=account_balance_dialogs_new_api["test_oot"])

create_training_data(file_directory="../data/account_balance_data/test/",file_name="test_data_re_order.txt",dialogs=account_balance_dialogs_re_order["test"])
create_training_data(file_directory="../data/account_balance_data/test/",file_name="test_data_re_order_oot.txt",dialogs=account_balance_dialogs_re_order["test_oot"])

create_training_data(file_directory="../data/account_balance_data/test/",file_name="test_data_another_slot.txt",dialogs=account_balance_dialogs_another_slot["test"])
create_training_data(file_directory="../data/account_balance_data/test/",file_name="test_data_another_slot_oot.txt",dialogs=account_balance_dialogs_another_slot["test_oot"])

create_training_data(file_directory="../data/account_balance_data/test/",file_name="test_data_audit_more.txt",dialogs=account_balance_dialogs_audit_more["test"])
create_training_data(file_directory="../data/account_balance_data/test/",file_name="test_data_audit_more_oot.txt",dialogs=account_balance_dialogs_audit_more["test_oot"])


create_training_data(file_directory="../data/account_limit_data/",file_name="train_data.txt",dialogs=account_limit_dialogs["train"])
create_training_data(file_directory="../data/account_limit_data/",file_name="val_data.txt",dialogs=account_limit_dialogs["val"])


create_training_data(file_directory="../data/account_limit_data/test/",file_name="test_data.txt",dialogs=account_limit_dialogs["test"])
create_training_data(file_directory="../data/account_limit_data/test/",file_name="test_data_oot.txt",dialogs=account_limit_dialogs["test_oot"])

create_training_data(file_directory="../data/account_limit_data/test/",file_name="test_data_turn_compression.txt",dialogs=account_limit_dialogs_turn_compression["test"])
create_training_data(file_directory="../data/account_limit_data/test/",file_name="test_data_turn_compression_oot.txt",dialogs=account_limit_dialogs_turn_compression["test_oot"])

create_training_data(file_directory="../data/account_limit_data/test/",file_name="test_data_new_api.txt",dialogs=account_limit_dialogs_new_api["test"])
create_training_data(file_directory="../data/account_limit_data/test/",file_name="test_data_new_api_oot.txt",dialogs=account_limit_dialogs_new_api["test_oot"])

create_training_data(file_directory="../data/account_limit_data/test/",file_name="test_data_re_order.txt",dialogs=account_limit_dialogs_re_order["test"])
create_training_data(file_directory="../data/account_limit_data/test/",file_name="test_data_re_order_oot.txt",dialogs=account_limit_dialogs_re_order["test_oot"])

create_training_data(file_directory="../data/account_limit_data/test/",file_name="test_data_another_slot.txt",dialogs=account_limit_dialogs_another_slot["test"])
create_training_data(file_directory="../data/account_limit_data/test/",file_name="test_data_another_slot_oot.txt",dialogs=account_limit_dialogs_another_slot["test_oot"])

create_training_data(file_directory="../data/account_limit_data/test/",file_name="test_data_audit_more.txt",dialogs=account_limit_dialogs_audit_more["test"])
create_training_data(file_directory="../data/account_limit_data/test/",file_name="test_data_audit_more_oot.txt",dialogs=account_limit_dialogs_audit_more["test_oot"])



create_training_data(file_directory="../data/block_card_data/",file_name="train_data.txt",dialogs=block_card_dialogs["train"])
create_training_data(file_directory="../data/block_card_data/",file_name="val_data.txt",dialogs=block_card_dialogs["val"])


create_training_data(file_directory="../data/block_card_data/test/",file_name="test_data.txt",dialogs=block_card_dialogs["test"])
create_training_data(file_directory="../data/block_card_data/test/",file_name="test_data_oot.txt",dialogs=block_card_dialogs["test_oot"])

create_training_data(file_directory="../data/block_card_data/test/",file_name="test_data_turn_compression.txt",dialogs=block_card_dialogs_turn_compression["test"])
create_training_data(file_directory="../data/block_card_data/test/",file_name="test_data_turn_compression_oot.txt",dialogs=block_card_dialogs_turn_compression["test_oot"])

create_training_data(file_directory="../data/block_card_data/test/",file_name="test_data_new_api.txt",dialogs=block_card_dialogs_new_api["test"])
create_training_data(file_directory="../data/block_card_data/test/",file_name="test_data_new_api_oot.txt",dialogs=block_card_dialogs_new_api["test_oot"])

create_training_data(file_directory="../data/block_card_data/test/",file_name="test_data_re_order.txt",dialogs=block_card_dialogs_re_order["test"])
create_training_data(file_directory="../data/block_card_data/test/",file_name="test_data_re_order_oot.txt",dialogs=block_card_dialogs_re_order["test_oot"])

create_training_data(file_directory="../data/block_card_data/test/",file_name="test_data_another_slot.txt",dialogs=block_card_dialogs_another_slot["test"])
create_training_data(file_directory="../data/block_card_data/test/",file_name="test_data_another_slot_oot.txt",dialogs=block_card_dialogs_another_slot["test_oot"])

create_training_data(file_directory="../data/block_card_data/test/",file_name="test_data_audit_more.txt",dialogs=block_card_dialogs_audit_more["test"])
create_training_data(file_directory="../data/block_card_data/test/",file_name="test_data_audit_more_oot.txt",dialogs=block_card_dialogs_audit_more["test_oot"])


create_training_data(file_directory="../data/cancel_transaction_data/",file_name="train_data.txt",dialogs=cancel_transaction_dialogs["train"])
create_training_data(file_directory="../data/cancel_transaction_data/",file_name="val_data.txt",dialogs=cancel_transaction_dialogs["val"])


create_training_data(file_directory="../data/cancel_transaction_data/test/",file_name="test_data.txt",dialogs=cancel_transaction_dialogs["test"])
create_training_data(file_directory="../data/cancel_transaction_data/test/",file_name="test_data_oot.txt",dialogs=cancel_transaction_dialogs["test_oot"])

create_training_data(file_directory="../data/cancel_transaction_data/test/",file_name="test_data_turn_compression.txt",dialogs=cancel_transaction_dialogs_turn_compression["test"])
create_training_data(file_directory="../data/cancel_transaction_data/test/",file_name="test_data_turn_compression_oot.txt",dialogs=cancel_transaction_dialogs_turn_compression["test_oot"])

create_training_data(file_directory="../data/cancel_transaction_data/test/",file_name="test_data_new_api.txt",dialogs=cancel_transaction_dialogs_new_api["test"])
create_training_data(file_directory="../data/cancel_transaction_data/test/",file_name="test_data_new_api_oot.txt",dialogs=cancel_transaction_dialogs_new_api["test_oot"])

create_training_data(file_directory="../data/cancel_transaction_data/test/",file_name="test_data_re_order.txt",dialogs=cancel_transaction_dialogs_re_order["test"])
create_training_data(file_directory="../data/cancel_transaction_data/test/",file_name="test_data_re_order_oot.txt",dialogs=cancel_transaction_dialogs_re_order["test_oot"])

create_training_data(file_directory="../data/cancel_transaction_data/test/",file_name="test_data_another_slot.txt",dialogs=cancel_transaction_dialogs_another_slot["test"])
create_training_data(file_directory="../data/cancel_transaction_data/test/",file_name="test_data_another_slot_oot.txt",dialogs=cancel_transaction_dialogs_another_slot["test_oot"])

create_training_data(file_directory="../data/cancel_transaction_data/test/",file_name="test_data_audit_more.txt",dialogs=cancel_transaction_dialogs_audit_more["test"])
create_training_data(file_directory="../data/cancel_transaction_data/test/",file_name="test_data_audit_more_oot.txt",dialogs=cancel_transaction_dialogs_audit_more["test_oot"])



create_training_data(file_directory="../data/search_note_data/",file_name="train_data.txt",dialogs=search_note_dialogs["train"])
create_training_data(file_directory="../data/search_note_data/",file_name="val_data.txt",dialogs=search_note_dialogs["val"])


create_training_data(file_directory="../data/search_note_data/test/",file_name="test_data.txt",dialogs=search_note_dialogs["test"])
create_training_data(file_directory="../data/search_note_data/test/",file_name="test_data_oot.txt",dialogs=search_note_dialogs["test_oot"])

create_training_data(file_directory="../data/search_note_data/test/",file_name="test_data_turn_compression_test.txt",dialogs=search_note_dialogs_turn_compression["test"])
create_training_data(file_directory="../data/search_note_data/test/",file_name="test_data_turn_compression_test_oot.txt",dialogs=search_note_dialogs_turn_compression["test_oot"])

create_training_data(file_directory="../data/search_note_data/test/",file_name="test_data_new_api_test.txt",dialogs=search_note_dialogs_new_api["test"])
create_training_data(file_directory="../data/search_note_data/test/",file_name="test_data_new_api_test_oot.txt",dialogs=search_note_dialogs_new_api["test_oot"])

create_training_data(file_directory="../data/search_note_data/test/",file_name="test_data_re_order_test.txt",dialogs=search_note_dialogs_re_order["test"])
create_training_data(file_directory="../data/search_note_data/test/",file_name="test_data_re_order_test_oot.txt",dialogs=search_note_dialogs_re_order["test_oot"])

create_training_data(file_directory="../data/search_note_data/test/",file_name="test_data_another_slot_test.txt",dialogs=search_note_dialogs_another_slot["test"])
create_training_data(file_directory="../data/search_note_data/test/",file_name="test_data_another_slot_test_oot.txt",dialogs=search_note_dialogs_another_slot["test_oot"])

create_training_data(file_directory="../data/search_note_data/test/",file_name="test_data_audit_more_test.txt",dialogs=search_note_dialogs_audit_more["test"])
create_training_data(file_directory="../data/search_note_data/test/",file_name="test_data_audit_more_test_oot.txt",dialogs=search_note_dialogs_audit_more["test_oot"])



create_training_data(file_directory="../data/start_data/",file_name="train_data.txt",dialogs=start_dialogs_train)
create_training_data(file_directory="../data/start_data/",file_name="val_data.txt",dialogs=start_dialogs_val)


create_training_data(file_directory="../data/start_data/test/",file_name="test_data.txt",dialogs=start_dialogs_test)
create_training_data(file_directory="../data/start_data/test/",file_name="test_data_oot.txt",dialogs=start_dialogs_test_oot)

create_training_data(file_directory="../data/start_data/test/",file_name="test_data_turn_compression.txt",dialogs=start_dialogs_turn_compression_test)
create_training_data(file_directory="../data/start_data/test/",file_name="test_data_turn_compression_oot.txt",dialogs=start_dialogs_turn_compression_test_oot)

create_training_data(file_directory="../data/start_data/test/",file_name="test_data_new_api.txt",dialogs=start_dialogs_new_api_test)
create_training_data(file_directory="../data/start_data/test/",file_name="test_data_new_api_oot.txt",dialogs=start_dialogs_new_api_test_oot)

create_training_data(file_directory="../data/start_data/test/",file_name="test_data_re_order.txt",dialogs=start_dialogs_re_order_test)
create_training_data(file_directory="../data/start_data/test/",file_name="test_data_re_order_oot.txt",dialogs=start_dialogs_re_order_test_oot)

create_training_data(file_directory="../data/start_data/test/",file_name="test_data_another_slot.txt",dialogs=start_dialogs_another_slot_test)
create_training_data(file_directory="../data/start_data/test/",file_name="test_data_another_slot.txt",dialogs=start_dialogs_another_slot_test_oot)

create_training_data(file_directory="../data/start_data/test/",file_name="test_data_audit_more.txt",dialogs=start_dialogs_audit_more_test)
create_training_data(file_directory="../data/start_data/test/",file_name="test_data_audit_more_oot.txt",dialogs=start_dialogs_audit_more_test_oot)


create_training_data(file_directory="../data/special_data/",file_name="train_data.txt",dialogs=special_dialogs_val)
create_training_data(file_directory="../data/special_data/",file_name="val_data.txt",dialogs=special_dialogs_val)


create_training_data(file_directory="../data/special_data/test/",file_name="test_data.txt",dialogs=special_dialogs_test)
create_training_data(file_directory="../data/special_data/test/",file_name="test_data_oot.txt",dialogs=special_dialogs_test_oot)

create_training_data(file_directory="../data/special_data/test/",file_name="test_data_turn_compression.txt",dialogs=special_dialogs_turn_compression_test)
create_training_data(file_directory="../data/special_data/test/",file_name="test_data_turn_compression_oot.txt",dialogs=special_dialogs_turn_compression_test_oot)

create_training_data(file_directory="../data/special_data/test/",file_name="test_data_new_api.txt",dialogs=special_dialogs_new_api_test)
create_training_data(file_directory="../data/special_data/test/",file_name="test_data_new_api_oot.txt",dialogs=special_dialogs_new_api_test_oot)

create_training_data(file_directory="../data/special_data/test/",file_name="test_data_re_order.txt",dialogs=special_dialogs_re_order_test)
create_training_data(file_directory="../data/special_data/test/",file_name="test_data_re_order_oot.txt",dialogs=special_dialogs_re_order_test_oot)

create_training_data(file_directory="../data/special_data/test/",file_name="test_data_another_slot.txt",dialogs=special_dialogs_another_slot_test)
create_training_data(file_directory="../data/special_data/test/",file_name="test_data_another_slot_oot.txt",dialogs=special_dialogs_another_slot_test_oot)

create_training_data(file_directory="../data/special_data/test/",file_name="test_data_audit_more.txt",dialogs=special_dialogs_audit_more_test)
create_training_data(file_directory="../data/special_data/test/",file_name="test_data_audit_more_oot.txt",dialogs=special_dialogs_audit_more_test_oot)



create_training_data(file_directory="../data/special_transaction_data/",file_name="train_data.txt",dialogs=special_transaction_dialogs_train)
create_training_data(file_directory="../data/special_transaction_data/",file_name="val_data.txt",dialogs=special_transaction_dialogs_val)



create_training_data(file_directory="../data/special_transaction_data/test/",file_name="test_data.txt",dialogs=special_transaction_dialogs_test)
create_training_data(file_directory="../data/special_transaction_data/test/",file_name="test_data_oot.txt",dialogs=special_transaction_dialogs_test_oot)

create_training_data(file_directory="../data/special_transaction_data/test/",file_name="test_data_turn_compression_test.txt",dialogs=special_transaction_dialogs_turn_compression_test)
create_training_data(file_directory="../data/special_transaction_data/test",file_name="test_data_turn_compression_test_oot.txt",dialogs=special_transaction_dialogs_turn_compression_test_oot)

create_training_data(file_directory="../data/special_transaction_data/test/",file_name="test_data_new_api_test.txt",dialogs=special_transaction_dialogs_new_api_test)
create_training_data(file_directory="../data/special_transaction_data/test",file_name="test_data_new_api_test_oot.txt",dialogs=special_transaction_dialogs_new_api_test_oot)

create_training_data(file_directory="../data/special_transaction_data/test/",file_name="test_data_re_order_test.txt",dialogs=special_transaction_dialogs_re_order_test)
create_training_data(file_directory="../data/special_transaction_data/test",file_name="test_data_re_order_test_oot.txt",dialogs=special_transaction_dialogs_re_order_test_oot)

create_training_data(file_directory="../data/special_transaction_data/test/",file_name="test_data_another_slot_test.txt",dialogs=special_transaction_dialogs_another_slot_test)
create_training_data(file_directory="../data/special_transaction_data/test/",file_name="test_data_another_slot_test_oot.txt",dialogs=special_transaction_dialogs_another_slot_test_oot)

create_training_data(file_directory="../data/special_transaction_data/test/",file_name="test_data_audit_more_test.txt",dialogs=special_transaction_dialogs_audit_more_test)
create_training_data(file_directory="../data/special_transaction_data/test/",file_name="test_data_audit_more_test_oot.txt",dialogs=special_transaction_dialogs_audit_more_test_oot)


create_training_data(file_directory="../data/special_account_balance_data/",file_name="train_data.txt",dialogs=special_account_balance_dialogs_train)
create_training_data(file_directory="../data/special_account_balance_data/",file_name="val_data.txt",dialogs=special_account_balance_dialogs_val)


create_training_data(file_directory="../data/special_account_balance_data/test/",file_name="test_data.txt",dialogs=special_account_balance_dialogs_test)
create_training_data(file_directory="../data/special_account_balance_data/test/",file_name="test_data_oot.txt",dialogs=special_account_balance_dialogs_test_oot)

create_training_data(file_directory="../data/special_account_balance_data/test/",file_name="test_data_turn_compression.txt",dialogs=special_account_balance_dialogs_turn_compression_test)
create_training_data(file_directory="../data/special_account_balance_data/test/",file_name="test_data_turn_compression_oot.txt",dialogs=special_account_balance_dialogs_turn_compression_test_oot)

create_training_data(file_directory="../data/special_account_balance_data/test/",file_name="test_data_new_api.txt",dialogs=special_account_balance_dialogs_new_api_test)
create_training_data(file_directory="../data/special_account_balance_data/test/",file_name="test_data_new_api_oot.txt",dialogs=special_account_balance_dialogs_new_api_test_oot)

create_training_data(file_directory="../data/special_account_balance_data/test/",file_name="test_data_re_order.txt",dialogs=special_account_balance_dialogs_re_order_test)
create_training_data(file_directory="../data/special_account_balance_data/test/",file_name="test_data_re_order_oot.txt",dialogs=special_account_balance_dialogs_re_order_test_oot)

create_training_data(file_directory="../data/special_account_balance_data/test/",file_name="test_data_another_slot.txt",dialogs=special_account_balance_dialogs_another_slot_test)
create_training_data(file_directory="../data/special_account_balance_data/test/",file_name="test_data_another_slot_oot.txt",dialogs=special_account_balance_dialogs_another_slot_test_oot)

create_training_data(file_directory="../data/special_account_balance_data/test/",file_name="test_data_audit_more.txt",dialogs=special_account_balance_dialogs_audit_more_test)
create_training_data(file_directory="../data/special_account_balance_data/test/",file_name="test_data_audit_more_oot.txt",dialogs=special_account_balance_dialogs_audit_more_test_oot)



create_training_data(file_directory="../data/special_account_limit_data/",file_name="train_data.txt",dialogs=special_account_limit_dialogs_train)
create_training_data(file_directory="../data/special_account_limit_data/",file_name="val_data.txt",dialogs=special_account_limit_dialogs_val)


create_training_data(file_directory="../data/special_account_limit_data/test/",file_name="test_data.txt",dialogs=special_account_limit_dialogs_test)
create_training_data(file_directory="../data/special_account_limit_data/test/",file_name="test_data_oot.txt",dialogs=special_account_limit_dialogs_test_oot)

create_training_data(file_directory="../data/special_account_limit_data/test/",file_name="test_data_turn_compression.txt",dialogs=special_account_limit_dialogs_turn_compression_test)
create_training_data(file_directory="../data/special_account_limit_data/test/",file_name="test_data_turn_compression_oot.txt",dialogs=special_account_limit_dialogs_turn_compression_test_oot)

create_training_data(file_directory="../data/special_account_limit_data/test/",file_name="test_data_new_api.txt",dialogs=special_account_limit_dialogs_new_api_test)
create_training_data(file_directory="../data/special_account_limit_data/test/",file_name="test_data_new_api_oot.txt",dialogs=special_account_limit_dialogs_new_api_test_oot)

create_training_data(file_directory="../data/special_account_limit_data/test/",file_name="test_data_re_order.txt",dialogs=special_account_limit_dialogs_re_order_test)
create_training_data(file_directory="../data/special_account_limit_data/test/",file_name="test_data_re_order_oot.txt",dialogs=special_account_limit_dialogs_re_order_test_oot)

create_training_data(file_directory="../data/special_account_limit_data/test/",file_name="test_data_another_slot.txt",dialogs=special_account_limit_dialogs_another_slot_test)
create_training_data(file_directory="../data/special_account_limit_data/test/",file_name="test_data_another_slot_oot.txt",dialogs=special_account_limit_dialogs_another_slot_test_oot)

create_training_data(file_directory="../data/special_account_limit_data/test/",file_name="test_data_audit_more.txt",dialogs=special_account_limit_dialogs_audit_more_test)
create_training_data(file_directory="../data/special_account_limit_data/test/",file_name="test_data_audit_more_oot.txt",dialogs=special_account_limit_dialogs_audit_more_test_oot)



create_training_data(file_directory="../data/special_block_card_data/",file_name="train_data.txt",dialogs=special_block_card_dialogs_train)
create_training_data(file_directory="../data/special_block_card_data/",file_name="val_data.txt",dialogs=special_block_card_dialogs_val)

create_training_data(file_directory="../data/special_block_card_data/test/",file_name="test_data.txt",dialogs=special_block_card_dialogs_test)
create_training_data(file_directory="../data/special_block_card_data/test/",file_name="test_data_oot.txt",dialogs=special_block_card_dialogs_test_oot)

create_training_data(file_directory="../data/special_block_card_data/test/",file_name="test_data_turn_compression.txt",dialogs=special_block_card_dialogs_turn_compression_test)
create_training_data(file_directory="../data/special_block_card_data/test/",file_name="test_data_turn_compression_oot.txt",dialogs=special_block_card_dialogs_turn_compression_test_oot)

create_training_data(file_directory="../data/special_block_card_data/test/",file_name="test_data_new_api.txt",dialogs=special_block_card_dialogs_new_api_test)
create_training_data(file_directory="../data/special_block_card_data/test/",file_name="test_data_new_api_oot.txt",dialogs=special_block_card_dialogs_new_api_test_oot)

create_training_data(file_directory="../data/special_block_card_data/test/",file_name="test_data_re_order.txt",dialogs=special_block_card_dialogs_re_order_test)
create_training_data(file_directory="../data/special_block_card_data/test/",file_name="test_data_re_order_oot.txt",dialogs=special_block_card_dialogs_re_order_test_oot)

create_training_data(file_directory="../data/special_block_card_data/test/",file_name="test_data_another_slot.txt",dialogs=special_block_card_dialogs_another_slot_test)
create_training_data(file_directory="../data/special_block_card_data/test/",file_name="test_data_another_slot_oot.txt",dialogs=special_block_card_dialogs_another_slot_test_oot)

create_training_data(file_directory="../data/special_block_card_data/test/",file_name="test_data_audit_more.txt",dialogs=special_block_card_dialogs_audit_more_test)
create_training_data(file_directory="../data/special_block_card_data/test/",file_name="test_data_audit_more_oot.txt",dialogs=special_block_card_dialogs_audit_more_test_oot)


create_training_data(file_directory="../data/special_cancel_transaction_data/",file_name="train_data.txt",dialogs=special_cancel_transaction_dialogs_train)
create_training_data(file_directory="../data/special_cancel_transaction_data/",file_name="val_data.txt",dialogs=special_cancel_transaction_dialogs_val)


create_training_data(file_directory="../data/special_cancel_transaction_data/test/",file_name="test_data.txt",dialogs=special_cancel_transaction_dialogs_test)
create_training_data(file_directory="../data/special_cancel_transaction_data/test/",file_name="test_data_oot.txt",dialogs=special_cancel_transaction_dialogs_test_oot)

create_training_data(file_directory="../data/special_cancel_transaction_data/test/",file_name="test_data_turn_compression.txt",dialogs=special_cancel_transaction_dialogs_turn_compression_test)
create_training_data(file_directory="../data/special_cancel_transaction_data/test/",file_name="test_data_turn_compression_oot.txt",dialogs=special_cancel_transaction_dialogs_turn_compression_test_oot)

create_training_data(file_directory="../data/special_cancel_transaction_data/test/",file_name="test_data_new_api.txt",dialogs=special_cancel_transaction_dialogs_new_api_test)
create_training_data(file_directory="../data/special_cancel_transaction_data/test/",file_name="test_data_new_api_oot.txt",dialogs=special_cancel_transaction_dialogs_new_api_test_oot)

create_training_data(file_directory="../data/special_cancel_transaction_data/test/",file_name="test_data_re_order.txt",dialogs=special_cancel_transaction_dialogs_re_order_test)
create_training_data(file_directory="../data/special_cancel_transaction_data/test/",file_name="test_data_re_order_oot.txt",dialogs=special_cancel_transaction_dialogs_re_order_test_oot)

create_training_data(file_directory="../data/special_cancel_transaction_data/test/",file_name="test_data_another_slot.txt",dialogs=special_cancel_transaction_dialogs_another_slot_test)
create_training_data(file_directory="../data/special_cancel_transaction_data/test/",file_name="test_data_another_slot_oot.txt",dialogs=special_cancel_transaction_dialogs_another_slot_test_oot)

create_training_data(file_directory="../data/special_cancel_transaction_data/test/",file_name="test_data_audit_more.txt",dialogs=special_cancel_transaction_dialogs_audit_more_test)
create_training_data(file_directory="../data/special_cancel_transaction_data/test/",file_name="test_data_audit_more_oot.txt",dialogs=special_cancel_transaction_dialogs_audit_more_test_oot)



create_training_data(file_directory="../data/special_search_note_data/",file_name="train_data.txt",dialogs=special_search_note_dialogs_train)
create_training_data(file_directory="../data/special_search_note_data/",file_name="val_data.txt",dialogs=special_search_note_dialogs_val)


create_training_data(file_directory="../data/special_search_note_data/test/",file_name="test_data.txt",dialogs=special_search_note_dialogs_test)
create_training_data(file_directory="../data/special_search_note_data/test/",file_name="test_data_oot.txt",dialogs=special_search_note_dialogs_test_oot)

create_training_data(file_directory="../data/special_search_note_data/test/",file_name="test_data_turn_compression_test.txt",dialogs=special_search_note_dialogs_turn_compression_test)
create_training_data(file_directory="../data/special_search_note_data/test/",file_name="test_data_turn_compression_test_oot.txt",dialogs=special_search_note_dialogs_turn_compression_test_oot)

create_training_data(file_directory="../data/special_search_note_data/test/",file_name="test_data_new_api_test.txt",dialogs=special_search_note_dialogs_new_api_test)
create_training_data(file_directory="../data/special_search_note_data/test/",file_name="test_data_new_api_test_oot.txt",dialogs=special_search_note_dialogs_new_api_test_oot)

create_training_data(file_directory="../data/special_search_note_data/test/",file_name="test_data_re_order_test.txt",dialogs=special_search_note_dialogs_re_order_test)
create_training_data(file_directory="../data/special_search_note_data/test/",file_name="test_data_re_order_test_oot.txt",dialogs=special_search_note_dialogs_re_order_test_oot)

create_training_data(file_directory="../data/special_search_note_data/test/",file_name="test_data_another_slot_test.txt",dialogs=special_search_note_dialogs_another_slot_test)
create_training_data(file_directory="../data/special_search_note_data/test/",file_name="test_data_another_slot_test_oot.txt",dialogs=special_search_note_dialogs_another_slot_test_oot)

create_training_data(file_directory="../data/special_search_note_data/test/",file_name="test_data_audit_more_test.txt",dialogs=special_search_note_dialogs_audit_more_test)
create_training_data(file_directory="../data/special_search_note_data/test/",file_name="test_data_audit_more_test_oot.txt",dialogs=special_search_note_dialogs_audit_more_test_oot)



create_training_data(file_directory="../data/one_data/",file_name="train_data.txt",dialogs=one_dialogs_train)
create_training_data(file_directory="../data/one_data/",file_name="val_data.txt",dialogs=one_dialogs_val)


create_training_data(file_directory="../data/one_data/test/",file_name="test_data.txt",dialogs=one_dialogs_test)
create_training_data(file_directory="../data/one_data/test/",file_name="test_data_oot.txt",dialogs=one_dialogs_test_oot)

create_training_data(file_directory="../data/one_data/test/",file_name="test_data_turn_compression.txt",dialogs=one_dialogs_turn_compression_test)
create_training_data(file_directory="../data/one_data/test/",file_name="test_data_turn_compression_oot.txt",dialogs=one_dialogs_turn_compression_test_oot)

create_training_data(file_directory="../data/one_data/test/",file_name="test_data_new_api.txt",dialogs=one_dialogs_new_api_test)
create_training_data(file_directory="../data/one_data/test/",file_name="test_data_new_api_oot.txt",dialogs=one_dialogs_new_api_test_oot)

create_training_data(file_directory="../data/one_data/test/",file_name="test_data_re_order.txt",dialogs=one_dialogs_re_order_test)
create_training_data(file_directory="../data/one_data/test/",file_name="test_data_re_order_oot.txt",dialogs=one_dialogs_re_order_test_oot)

create_training_data(file_directory="../data/one_data/test/",file_name="test_data_another_slot.txt",dialogs=one_dialogs_another_slot_test)
create_training_data(file_directory="../data/one_data/test/",file_name="test_data_another_slot_oot.txt",dialogs=one_dialogs_another_slot_test_oot)

create_training_data(file_directory="../data/one_data/test/",file_name="test_data_audit_more.txt",dialogs=one_dialogs_audit_more_test)
create_training_data(file_directory="../data/one_data/test/",file_name="test_data_audit_more_oot.txt",dialogs=one_dialogs_audit_more_test_oot)



create_candidates(file_directory="../data/transaction_data/",file_name="candidates.txt",dialogs=transaction_dialogs_all)




create_candidates(file_directory="../data/account_balance_data/",file_name="candidates.txt",dialogs=account_balance_dialogs_all)




create_candidates(file_directory="../data/account_limit_data/",file_name="candidates.txt",dialogs=account_limit_dialogs_all)




create_candidates(file_directory="../data/block_card_data/",file_name="candidates.txt",dialogs=block_card_dialogs_all)




create_candidates(file_directory="../data/cancel_transaction_data/",file_name="candidates.txt",dialogs=cancel_transaction_dialogs_all)




create_candidates(file_directory="../data/search_note_data/",file_name="candidates.txt",dialogs=search_note_dialogs_all)



create_candidates(file_directory="../data/start_data/",file_name="candidates.txt",dialogs=start_dialogs_all)




create_candidates(file_directory="../data/one_data/",file_name="candidates.txt",dialogs=one_dialogs_all)





find_generic_responses(actor="User",dialogs=transaction_dialogs_all,file_directory="../data/transaction_data/",file_name="user_generic_responses.txt")
find_generic_responses(actor="Bot",dialogs=transaction_dialogs_all,file_directory="../data/transaction_data/",file_name="bot_generic_responses.txt")



find_generic_responses(actor="User",dialogs=account_balance_dialogs_all,file_directory="../data/account_balance_data/",file_name="user_generic_responses.txt")
find_generic_responses(actor="Bot",dialogs=account_balance_dialogs_all,file_directory="../data/account_balance_data/",file_name="bot_generic_responses.txt")


find_generic_responses(actor="User",dialogs=account_limit_dialogs_all,file_directory="../data/account_limit_data/",file_name="user_generic_responses.txt")
find_generic_responses(actor="Bot",dialogs=account_limit_dialogs_all,file_directory="../data/account_limit_data/",file_name="bot_generic_responses.txt")


find_generic_responses(actor="User",dialogs=block_card_dialogs_all,file_directory="../data/block_card_data/",file_name="user_generic_responses.txt")
find_generic_responses(actor="Bot",dialogs=block_card_dialogs_all,file_directory="../data/block_card_data/",file_name="bot_generic_responses.txt")


find_generic_responses(actor="User",dialogs=cancel_transaction_dialogs_all,file_directory="../data/cancel_transaction_data/",file_name="user_generic_responses.txt")
find_generic_responses(actor="Bot",dialogs=cancel_transaction_dialogs_all,file_directory="../data/cancel_transaction_data/",file_name="bot_generic_responses.txt")


find_generic_responses(actor="User",dialogs=search_note_dialogs_all,file_directory="../data/search_note_data/",file_name="user_generic_responses.txt")
find_generic_responses(actor="Bot",dialogs=search_note_dialogs_all,file_directory="../data/search_note_data/",file_name="bot_generic_responses.txt")

