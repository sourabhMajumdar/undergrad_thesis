
# coding: utf-8

# ## All in One Note-book
# 
# This notebook tries to create all the data in one go so that you don't need to look somewhere else
# 
# To Summarize, this notebook combines all the notebooks dedicated for the Dialog Generation, hence running this file gives all the train, validation and test files to train the various memory networks.

# The Following code is ispired from the [Dialog Self-Play](https://arxiv.org/abs/1801.04871) Paper from google.
# 
# Below I have tried to add as much explanation to the cells as I could. However if you feel anything is confusing then feel free to drop a main to me at smajumdar@fbk.eu

# **Importing Libraries**

# In[1]:


import numpy as np # no use until now
import random # used for random sampling of values where applicable
import math # no use untill now
import pandas as pd # to read the excel file 
import os # to carry os operations


# ### Below is the Code for storing the template sentences
# **What does it do ?**
# 
# The cell below reads the excel and extracts the template sentences to store them in a dictionary where the key is the **LABEL** 
# 
# **Why do you need a dictionary ?**
# 
# It is because in the later stages of constructing the dialog, I will need to refer this dictionary to select an appropriate template sentences

# In[2]:


def make_templates(file_name="templates_for_dialogue_self_play.xlsx",sheet_name="MAKE_TRANSACTION",previous_dictionary=None) :
    if previous_dictionary == None :
        template_dictionary = dict()
    else :
        template_dictionary = previous_dictionary
    
    df = pd.read_excel(file_name,sheet_name)
    for index,row in df.iterrows() :
        if not pd.isnull(row["LABEL"]) :
            if row["LABEL"] not in template_dictionary.keys() :
                template_sentences = list()
            else :
                template_sentences = template_dictionary[row["LABEL"]]
                
            if not pd.isnull(row["TEXT-EN (Marco)"]) :
                template_sentences.append(row["TEXT-EN (Marco)"])
            if not pd.isnull(row["TEXT-EN (Sourabh)"]) :
                template_sentences.append(row["TEXT-EN (Sourabh)"])
                
            template_dictionary[row["LABEL"]] = template_sentences
    
    return template_dictionary
    


# **DICTIONARY FOR MAKING TRANSACTION**

# In[3]:


template_dictionary = make_templates(file_name="templates_for_dialogue_self_play.xlsx",
                                     sheet_name="MAKE_TRANSACTION",
                                     previous_dictionary=None)


# **DICTIONARY FOR CHECKING ACCOUNT BALANCE**

# In[4]:


template_dictionary = make_templates(file_name="templates_for_dialogue_self_play.xlsx",
                                     sheet_name="ACCOUNT_BALANCE",
                                     previous_dictionary=template_dictionary)


# **DICTIONARY FOR CHECKING TRANSACTION HISTORY**

# In[5]:


template_dictionary = make_templates(file_name="templates_for_dialogue_self_play.xlsx",
                                     sheet_name="TRANS_HISTORY",
                                     previous_dictionary=template_dictionary)


# ### Below is the Description of the Action class
# 
# **What is the Action Class ?**
# 
# Action class creates objects that intend to capture the various aspects of the conversation for e.g "What action is performed ?", "What were the values provided ?","Was there a warning that was provided ?" etc.
# 
# **Why need the Action Class, Can't you just write simple sentences like "inform date, request amount etc." ?**
# 
# While it's a good idea to write simple sentences to make a dialog, we need to remeber that there are more things happening within the dialog apart from the conversation. Like the task of keeping track of all the values that are being provided and executing some specific api based on action etc. Also not all the actions are meant to be said, some are there for the **api_call** and **end_call**. If I go for slicing each sentence to find out what to say, it becomes more complex and difficult and also we loose that ability of scaling.

# In[6]:


class Action(object) :
    def __init__(self,actor=None,action=None,slots=None,values=None,message=None,description=None) :
        
        self.actor = actor # who performed the action
        self.action = action # what action was performed
        self.slots = slots # what slot was dealt with 
        self.values = values # what was the value with this slot
        self.message = message # Any particular message related to the action
        self.description = description # This contain the description of the action and is never intended to be shown or appear in the actual conversation
        
        dictionary_key = self.action
        
        if self.slots :
            if len(self.slots) > 0 :
                for slot in self.slots :
                    
                    if slot == "intent" :
                        
                        if self.actor == "User" :
                            
                            dictionary_key += "-" + slot + "_" + self.values["intent"]
                            
                        else :
                            
                            dictionary_key += "-" + slot
                    else :
                        
                        dictionary_key += "-" + slot
        
        
        # if the dictionary_key exists in the template dictionary then get a template other wise set template = the action message
        if dictionary_key in template_dictionary.keys() :
            self.template = random.sample(template_dictionary[dictionary_key],1)[0]
        else :
            self.template = self.message
        
    # standard actions to perform
    def get_actor(self) :
        return self.actor
    
    def get_action(self) :
        return self.action
    
    def get_slots(self) :
        return self.slots
    
    def get_values(self) :
        return self.values
    
    def get_message(self) :
        return self.message
    
    def get_description(self) :
        return self.description
    
    # when called , construct a dialog from the slots and give it to the user
    def get_dialog(self,with_actor=True) :
        
        # first split the template into a list of words
        words = self.template.strip().split()
        sentence = None
        
        # only go to this loop if the actor is a User or Bot , in case of API go to else statement which will just append action and message
        if self.actor == "User" or self.actor == "Bot" :
            if self.values :
                for slot,value in self.values.items() :
                    search_slot = "{" + slot + "}"
                    if search_slot in words :
                        slot_index = words.index(search_slot)
                        words.insert(slot_index,str(value))
                
                        words.pop(slot_index+1)
                    sentence = " ".join(words)
                
            # if it's a request action then get a template requesting the slots
            elif self.action == "request" :
                
                sentence = self.template
            
            # if it's a end_call then show the action and the message given
            elif self.action == "end_call" :
                
                sentence = self.action + " " + self.message
            
            else :
                
                sentence = self.message
        
        else:
            
            sentence = self.action + " " + self.message
        if with_actor :
            return self.actor + " : " + sentence
        else :
            return sentence


# ### The User Class
# 
# **Who is the User Class ?**
# 
# The _User_ class our custom user who in the right sense represents our _dummy customer_ who will come to the bank for a transaction
# 
# **How is he working ?**
# 
# The _User_ Class adopts a certain _"personality"_ (a set of values) when instantiated, whenever the bot performs a specific action, it looks for the kind of request and respondes using it's _speak_ function
# 
# **Assumptions**
# 
# 1. It is possible that the user has multiple accounts and different transfer limits and balances on each of them, we assume that each account has the same set of transfer limits and balances

# **Creating the Transaction User**
# 
# This class creates a User that converses - communicates through actions - in the transaction domain.

# In[7]:


class Transaction_user() :
    def __init__(self) :
        
        # Below is the available pool of values from which we will create a Custom user for the transaction
        self.user_names = ["Sourabh","Serra","Simone","Marco","Vevake","Matteo","Tahir","Samuel"]
        self.user_accounts = ["Savings","Credit","Checkin"]
        self.transaction_limit = [1000,2000,5000]
        self.user_balances = [400,1300,3000,8000]
        self.transfer_amt = [200,800,1200,1600,2400,4500,9000]
        self.slots = ["user_account","destination_name","amount"]
        
        self.priority_states = list()
        self.priority_actions = dict()
        
        # create the custom user
        self.user = dict()
        self.create_user_profile()
    
    def sort_my_slots(self,slots_given) :
        slots_sorted = list()
        
        if "user_account" in slots_given :
            slots_sorted.append("user_account")
            slots_given.remove("user_account")
        
        if "destination_name" in slots_given :
            slots_sorted.append("destination_name")
            slots_given.remove("destination_name")
        
        if "amount" in slots_given :
            slots_sorted.append("amount")
            slots_given.remove("amount")
        
        for slot in slots_given :
            slots_sorted.append(slot)
        
        return slots_sorted
    
    def create_user_profile(self) :
        
        # Every value is assigned randomly 
        
        # selectinng name of sender and reciever
        
        names = random.sample(self.user_names,2)
        
        self.user["name"] = names[0]
        
        self.user["destination_name"] = names[1]
        number_of_destination_names = random.randint(1,len(self.user_names)-1)
        self.user["destination_names"] = random.sample(self.user_names,number_of_destination_names)
        
        #selecting the usr_account to make the transaction from
        self.user["user_account"] = random.sample(self.user_accounts,1)[0]
        
        number_of_user_accounts = random.randint(1,len(self.user_accounts) - 1)
        self.user["user_accounts"] = random.sample(self.user_accounts,number_of_user_accounts)
        
        # selecting the amount to be transfered
        self.user["amount"] = random.sample(self.transfer_amt,1)[0]
        
        # selecting the balance of the user
        self.user["balance"] = random.sample(self.user_balances,1)[0]
        
        # selecting the limit of the user
        self.user["limit"] = random.sample(self.transaction_limit,1)[0]
        
        # setting up the max_transferable amount
        self.user["max_transferable_amt"] = min(self.user["limit"],self.user["balance"])
        
        # setting up the intent
        self.user["intent"] = "transaction"
    
    # Returns the respective value of the slot
    def get_value(self,slot_asked) :
        
        return self.user[slot_asked]
    
    def perform_random_action(self,bot_action) :
        
        if bot_action.get_description() == "API_CALL" :
            
            actual_actor = "API_RESP"
            accept_message = "api_call success"
            reject_message = "api_call failed"
        
        elif bot_action.get_description() == "CHANGE_ACCOUNT" :
            
            actual_actor = "User"
            accept_message = "accept"
            reject_message = "reject"
            
            new_account = random.sample(self.user_accounts,1)[0]
            while new_account == self.user["user_account"] :
                new_account = random.sample(self.user_accounts,1)[0]
                
            self.user["user_account"] = new_account
        
        elif bot_action.get_description() == "CHANGE_AMOUNT" :
            
            actual_actor = "User"
            accept_message = "accept"
            reject_message = "reject"
            self.user["amount"] = self.user["max_transferable_amt"]
        
        elif bot_action.get_description() == "CHANGE_DESTINATION_NAME" :
            
            actual_actor = "User"
            accept_message = "accept"
            reject_message = "reject"
            
            new_destination_name = random.sample(self.user_names,1)[0]
            
            while new_destination_name == self.user["name"] or new_destination_name == self.user["destination_name"] :
                new_destination_name = random.sample(self.user_names,1)[0]
                
            self.user["destination_name"] = new_destination_name
        
        else :
            actual_actor = "User"
            accept_message = "accept"
            reject_message = "reject"
            
        toss = random.randint(0,1)
        if toss == 1 :
            user_action = Action(actor=actual_actor,
                                 action="inform",
                                 slots=None,
                                 values=None,
                                 message=accept_message)
        else :
            user_action = Action(actor=actual_actor,
                                 action="inform",
                                 slots=None,
                                 values=None,
                                 message=reject_message)
        return user_action
    # This is the function that converses with the bot through 'Action' Objects
    def speak(self,bot_action) :
        
        if bot_action.get_actor() == "API" :
            
            user_action = self.api_response(bot_action)            

        elif bot_action.get_action() == "request" :
            
            if bot_action.get_slots() != None :
                
                if bot_action.get_slots()[0] != "intent" :
                    
                    user_value = self.get_value(bot_action.get_slots()[0])
                    user_action = Action(actor="User",
                                         action="inform",
                                         slots=bot_action.get_slots(),
                                         values={bot_action.get_slots()[0] : user_value},
                                         message="Providing value for {}".format(bot_action.get_slots()[0]))
                
                else :
                    
                    number_of_slots = random.randint(0,len(self.slots)-1)
                    slots_to_inform = random.sample(self.slots,number_of_slots)
                    all_slots = ["intent"] + slots_to_inform
                    
                    values_to_inform = dict()
                    
                    for slot in all_slots :
                        values_to_inform[slot] = self.user[slot]
                    
                    user_action = Action(actor="User",
                                         action="inform",
                                         slots=all_slots,
                                         values=values_to_inform,
                                         message="Providing intent")
            else:
                
                user_action = self.perform_random_action(bot_action)
        
        elif bot_action.get_action() == "api_call" :
            
            user_action = self.perform_random_action(bot_action) 
        
        else :
            
            user_action = Action(actor="User",
                                 action=None,
                                 slots=None,
                                 values=None,
                                 message="<SILENCE>")
        
        return user_action
    
    # when the bot takes the role of API then, the User should assume the role of API_RESP (i.e API_RESPONSE)
    def api_response(self,bot_action) :
    
        user_action = None
        
        # if the API action asks for a account check
        if bot_action.get_action() == "amount_check" :
            
            if self.user["amount"] > self.user["max_transferable_amt"] :
                
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=["limit","balance","max_transferable_amt"],
                                     values={"limit" : self.user["limit"],
                                             "balance" : self.user["balance"],
                                             "max_transferable_amt" : self.user["max_transferable_amt"]},
                                     message="limit:{},balance:{},maxi_transferable_amt:{} message='change to max_transferable_amt ?'".format(self.user["limit"],
                                                                                                                                   self.user["balance"],
                                                                                                                                   self.user["max_transferable_amt"]))
            
            else :
                
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=["limit","balance","max_transferable_amt"],
                                     values={"limit" : self.user["limit"],
                                             "balance" : self.user["balance"],
                                             "max_transferable_amt" : self.user["max_transferable_amt"]},
                                     message="amount_check : success")
        
        # if the API action askes for a initial state check
        elif bot_action.get_action() == "initial_slots_check" :
            
            # if the flag becomes true at the end of this segment then it means that one or more than one slots are incorrect
            flag = False
            error_message = list()
            
            # if user account is given in the initial slots then check if it is appropriate
            if "user_account" in bot_action.get_slots() and self.user["user_account"] not in self.user["user_accounts"] :
                
                self.priority_states.append("check_account")
                self.priority_actions["check_account"] =  Action(actor="API",
                                                                action="account_check",
                                                                slots=["user_account"],
                                                                values=None,
                                                                message="user_account:{}".format(self.user["user_account"]))
            
            # if destination name is given in the initial slots then check if it is appropriate
            if "destination_name" in bot_action.get_slots() and self.user["destination_name"] not in self.user["destination_names"] :
                
                self.priority_states.append("check_destination")
                self.priority_actions["check_destination"] = Action(actor="API",
                                                                   action="destination_name_check",
                                                                   slots=["destination_name"],
                                                                   values=None,
                                                                   message="destination_name:{}".format(self.user["destination_name"]))
            
            # if both user_account and amount are present then check if the amount satisfies the criteria
            if "user_account" in bot_action.get_slots() and "amount" in bot_action.get_slots() and self.user["amount"] > self.user["max_transferable_amt"] :
                
                self.priority_states.append("check_amount")
                self.priority_actions["check_amount"] = Action(actor="API",
                                              action="amount_check",
                                              slots=["limit","balance"],
                                              values=None,
                                              message="user_account:{} , amount:{}".format(self.user["user_account"],
                                                                      self.user["amount"]))
            
            # if self.priority_states is no empty then one or more than one value is incorrect then send appropriate error message
            if self.priority_states :
                
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=self.priority_states,
                                     values=self.priority_actions,
                                     message="initial_slots_check : failed, message='one or more slots are faulty'")
            
            # if everything is okay then send the correct message
            else :
                
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=bot_action.get_slots(),
                                     values=None,
                                     message="initial_slots_check : success")
        
        # if the requested action is an account check
        elif bot_action.get_action() == "account_check" :
            
            if self.user["user_account"] in self.user["user_accounts"] :
                
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=["account"],
                                     values=self.user,
                                     message="account_check : success")
            
            else :
                
                slot_message = ','.join(self.user["user_accounts"])
                api_message = "account_check : failed , message='availbale list of user accounts : " + slot_message + "'"
                
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=self.user["user_accounts"],
                                     values=self.user,
                                     message=api_message)
        
        # if the requested action is destination name check
        elif bot_action.get_action() == "destination_name_check" :
            
            if self.user["destination_name"] in self.user["destination_names"] :
                
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=["destination_name"],
                                     values=None,
                                     message="destination_name_check : success")
            
            else :
                
                slot_message = ','.join(self.user["destination_names"])
                api_message = "destination_name_check : failed , message='available list of names : " + slot_message + "'"
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=self.user["destination_names"],
                                     values={"destination_names" : self.user["destination_names"]},
                                     message=api_message)
        
        return user_action            


# **Creating Account User**
# 
# This class creates a user capable of conversing - communicating through actions - in the Account Domain

# In[8]:


class Account_user() :
    def __init__(self) :
        
        # Below is the available pool of values from which we will create a Custom user for the transaction
        self.user_names = ["Sourabh","Serra","Simone","Marco","Vevake","Matteo","Tahir","Samuel"]
        self.user_accounts = ["Savings","Credit","Checkin"]
        self.user_balances = [400,1300,3000,8000]
        
        
        self.priority_states = list()
        self.priority_actions = dict()
        
        # create the custom user
        self.user = dict()
        self.create_user_profile()
    
    def sort_my_slots(self,slots_given) :
        slots_sorted = list()
        
        if "user_account" in slots_given :
            slots_sorted.append("user_account")
            slots_given.remove("user_account")
        
        if "destination_name" in slots_given :
            slots_sorted.append("destination_name")
            slots_given.remove("destination_name")
        
        if "amount" in slots_given :
            slots_sorted.append("amount")
            slots_given.remove("amount")
        
        for slot in slots_given :
            slots_sorted.append(slot)
        
        return slots_sorted
    
    def create_user_profile(self) :
        
        # Every value is assigned randomly 
        
        # selectinng name of sender and reciever
        
        self.user["name"] = random.sample(self.user_names,1)[0]
                
        #selecting the usr_account to make the transaction from
        
        
        # select at random the number of account the user has.
        number_of_account = random.randint(1,len(self.user_accounts) - 1)
        
        self.user["user_accounts"] = random.sample(self.user_accounts,number_of_account)
        
        # select a list of accounts from the given sample
        
        self.user["user_account"] = random.sample(self.user["user_accounts"],1)[0]
        
        self.user["balance"] = random.sample(self.user_balances,1)[0]
                        
        # setting up the intent
        self.user["intent"] = "account_balance"
    
    # Returns the respective value of the slot
    def get_value(self,slot_asked) :
        
        return self.user[slot_asked]
    
    # This function is called when the bot has made a request but no slots have been provided, hence we look at the description of the action to figure out what the request is
    def perform_random_action(self,bot_action) :
        
        if bot_action.get_description() == "SELECT_ACCOUNT" :
               
            self.user["user_account"] = random.sample(self.user["user_accounts"],1)[0]
            
            user_action = Action(actor="User",
                                action="inform",
                                slots=["user_account"],
                                values={"user_account" : self.user["user_account"]},
                                message="providing value for user_account")
        else :
            
            values_to_give = None
            
            if bot_action.get_description() == "API_CALL" :
                
                actual_actor = "API_RESP"
                accept_message = "api_call : success , balance : {}".format(self.user["balance"])
                reject_message = "api_call : failed"
                values_to_give = {"balance" : self.user["balance"]}
            
            else :
                actual_actor = "User"
                accept_message = "accept"
                reject_message = "reject"
            
            toss = random.randint(0,1)
            if toss == 1 :
                user_action = Action(actor=actual_actor,
                                     action="inform",
                                     slots=None,
                                     values=values_to_give,
                                     message=accept_message)
            else :
                
                user_action = Action(actor=actual_actor,
                                     action="inform",
                                     slots=None,
                                     values=values_to_give,
                                     message=reject_message)
        return user_action
    # This is the function that converses with the bot through 'Action' Objects
    def speak(self,bot_action) :
        
        if bot_action.get_actor() == "API" :
            
            user_action = self.api_response(bot_action)            

        elif bot_action.get_action() == "request" :
            
            if bot_action.get_slots() != None :
                
                if bot_action.get_slots()[0] != "intent" :
                    
                    user_value = self.get_value(bot_action.get_slots()[0])
                    user_action = Action(actor="User",
                                         action="inform",
                                         slots=bot_action.get_slots(),
                                         values={bot_action.get_slots()[0] : user_value},
                                         message="Providing value for {}".format(bot_action.get_slots()[0]))
                
                else :
                    
                    user_action = Action(actor="User",
                                       action="inform",
                                       slots=["intent"],
                                       values={"intent" : self.user["intent"],"name" : self.user["name"]},
                                       message="Providing value for intent")
            else:
                
                user_action = self.perform_random_action(bot_action)
        
        elif bot_action.get_action() == "api_call" :
            
            user_action = self.perform_random_action(bot_action) 
        
        else :
            
            user_action = Action(actor="User",
                                 action=None,
                                 slots=None,
                                 values=None,
                                 message="<SILENCE>")
        
        return user_action
    
    # when the bot takes the role of API then, the User should assume the role of API_RESP (i.e API_RESPONSE)
    def api_response(self,bot_action) :
    
        user_action = None
        
        # if the API action asks for a account check
        if bot_action.get_action() == "request_accounts" :
            
            slot_message = ",".join(self.user["user_accounts"])
            bot_message = "list_of_accounts : {}".format(slot_message)
            user_action = Action(actor="API_RESP",
                                action="inform",
                                slots = self.user["user_accounts"],
                                values=None,
                                message=bot_message,
                                description="LIST_OF_SLOTS")
        
        
        return user_action            


# **Creating User in the Transaction History Domain**
# 
# The class below creates a user that converses - communicates through actions - in the transaction history domain.

# In[9]:


class Transaction_history_user() :
    def __init__(self) :
        
        # Below is the available pool of values from which we will create a Custom user for the transaction
        self.user_names = ["Sourabh","Serra","Simone","Marco","Vevake","Matteo","Tahir","Samuel"]
        self.user_accounts = ["Savings","Credit","Checkin"]
        self.user_balances = [400,1300,3000,8000]
        self.user_transaction_types = ["credit","debit"]
        
        self.priority_states = list()
        self.priority_actions = dict()
        
        # create the custom user
        self.user = dict()
        self.create_user_profile()
    
    def sort_my_slots(self,slots_given) :
        slots_sorted = list()
        
        if "user_account" in slots_given :
            slots_sorted.append("user_account")
            slots_given.remove("user_account")
        
        if "destination_name" in slots_given :
            slots_sorted.append("destination_name")
            slots_given.remove("destination_name")
        
        if "amount" in slots_given :
            slots_sorted.append("amount")
            slots_given.remove("amount")
        
        for slot in slots_given :
            slots_sorted.append(slot)
        
        return slots_sorted
    
    def create_user_profile(self) :
        
        # Every value is assigned randomly 
        
        # selectinng name of sender and reciever
        
        names = random.sample(self.user_names,2)
        
        self.user["name"] = names[0]
        self.user["destination_name"] = names[1]
                
        #selecting the usr_account to make the transaction from
        
        
        # select at random the number of account the user has.
        number_of_account = random.randint(1,len(self.user_accounts) - 1)
        
        self.user["user_accounts"] = random.sample(self.user_accounts,number_of_account)
        
        # select a list of accounts from the given sample
        self.user["user_account"] = random.sample(self.user["user_accounts"],1)[0]
        
        number_of_recipients = random.randint(1,len(self.user_names) - 1)
        self.user["destination_names"] = random.sample(self.user_names,number_of_recipients)
        
        # select the type of transaction
        self.user["credit_debit"] = random.sample(self.user_transaction_types,1)[0]
        
        self.user["balance"] = random.sample(self.user_balances,1)[0]
                        
        # setting up the intent
        self.user["intent"] = "transaction_history"
    
    # Returns the respective value of the slot
    def get_value(self,slot_asked) :
        
        return self.user[slot_asked]
    
    # This function is called when the bot has made a request but no slots have been provided, hence we look at the description of the action to figure out what the request is
    def perform_random_action(self,bot_action) :
        
        if bot_action.get_description() == "SELECT_ACCOUNT" :
               
            self.user["user_account"] = random.sample(self.user["user_accounts"],1)[0]
            
            user_action = Action(actor="User",
                                action="inform",
                                slots=["user_account"],
                                values={"user_account" : self.user["user_account"]},
                                message="providing value for user_account")
        
            
        else :
            
            
            if bot_action.get_description() == "API_CALL" :
                
                actual_actor = "API_RESP"
                accept_message = "api_call : success"
                reject_message = "api_call : failed"
            
            elif bot_action.get_description() == "CHANGE_DESTINATION_NAME" :
                
                new_destination_name = None
                
                while new_destination_name == self.user["name"] and new_destination_name == self.user["destination_name"] :
                    new_destination_name = random.sample(self.user["destination_names"],1)[0]
                
                self.user["destination_name"] = new_destination_name
                
                actual_actor = "User"
                accept_message = "accept"
                reject_message = "reject"
            
            else :
                actual_actor = "User"
                accept_message = "accept"
                reject_message = "reject"
            
            toss = random.randint(0,1)
            
            if toss == 1 :
                user_action = Action(actor=actual_actor,
                                     action="inform",
                                     slots=None,
                                     values=None,
                                     message=accept_message)
            else :
                
                user_action = Action(actor=actual_actor,
                                     action="inform",
                                     slots=None,
                                     values=None,
                                     message=reject_message)
        return user_action
    # This is the function that converses with the bot through 'Action' Objects
    def speak(self,bot_action) :
        
        if bot_action.get_actor() == "API" :
            
            user_action = self.api_response(bot_action)            

        elif bot_action.get_action() == "request" :
            
            if bot_action.get_slots() != None :
                
                if bot_action.get_slots()[0] != "intent" :
                    
                    user_value = self.get_value(bot_action.get_slots()[0])
                    user_action = Action(actor="User",
                                         action="inform",
                                         slots=bot_action.get_slots(),
                                         values={bot_action.get_slots()[0] : user_value},
                                         message="Providing value for {}".format(bot_action.get_slots()[0]))
                
                else :
                    
                    user_action = Action(actor="User",
                                       action="inform",
                                       slots=["intent"],
                                       values={"intent" : self.user["intent"],"name" : self.user["name"]},
                                       message="Providing value for intent")
            else:
                
                user_action = self.perform_random_action(bot_action)
        
        elif bot_action.get_action() == "api_call" :
            
            user_action = self.perform_random_action(bot_action) 
        
        else :
            
            user_action = Action(actor="User",
                                 action=None,
                                 slots=None,
                                 values=None,
                                 message="<SILENCE>")
        
        return user_action
    
    # when the bot takes the role of API then, the User should assume the role of API_RESP (i.e API_RESPONSE)
    def api_response(self,bot_action) :
    
        user_action = None
        
        # if the API action asks for a account check
        if bot_action.get_action() == "request_accounts" :
            
            slot_message = ",".join(self.user["user_accounts"])
            bot_message = "list_of_accounts : {}".format(slot_message)
            user_action = Action(actor="API_RESP",
                                action="inform",
                                slots = self.user["user_accounts"],
                                values=None,
                                message=bot_message,
                                description="LIST_OF_SLOTS")
        
        elif bot_action.get_action() == "destination_name_check" :
            
            if self.user["destination_name"] in self.user["destination_names"] :
                
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=None,
                                     values=None,
                                     message="destination_name_check : success")
            else :
                
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=self.user["destination_names"],
                                     values={"destination_names" : self.user["destination_names"]},
                                     message="destination_name_check : failed")
                
        
        
        return user_action            


# ### The Bot class
# 
# **Who is the Bot Class ?**
# 
# The Bot class can be thought to immitiate the _the system agent_ (in this case, the employee dealing in transactions).
# 
# **What is this complex piece of code below , can I understand it ?**
# 
# At first glance, No. But if it would help what it represents. The Code below is nothing more than a Finite State Machine.
# 
# **Okay !! Explain how it is working ?**
# 
# The _Bot_ or the FSM is working through a pre-determined set of states where at each state we assume that the bot will perform an action related to the field. May be the diagram below will help.
# <img src="./Transaction_flow_chart.png">
# 
# 
# Each of the circles in the above diagram is repesented by a function in the _Bot_ Class.
# 
# **What is next_state and bot_action ?**
# 
# So Basically, for each of the user's action we determine what is the appropriate *bot\_action* to be performed. This done with the help of the speak function and appropriate state function.
# 
# Once we have determined this, we determine what should be the appropriate next_state in the diagram.
# 
# If you look at the speak function it selects the appropriate function (or next_state of the diagram) from the set of states

# **Creating Transaction Bot**
# 
# This bot converses and requests queries - through actions - in the transaction domain.

# In[10]:


class Transaction_bot(object) :
    
    def __init__(self) :
        
        self.last_slot = None
        self.list_of_slots = ["user_account","destination_name","amount"]
        self.slots_to_ask = ["user_account","destination_name","amount"]
        self.user_values = dict()
        self.states = {"initial" : self.initial_state ,
                       "check_initial" : self.check_initial_state,
                       "user_account" : self.account_state ,
                       "check_account" : self.check_account_state,
                       "change_account" : self.change_account_state,
                       "destination_name" : self.destination_state ,
                       "check_destination" : self.check_destination_name_state,
                       "change_destination_name" : self.change_destination_name_state,
                       "amount" : self.amount_state ,
                       "check_amount" : self.check_amount_state,
                       "change_amount" : self.change_amount_state,
                       "end_call" : self.end_call_state ,
                       "balance" : self.balance_state ,
                       "confirmation_state" : self.confirmation_state,
                       "api_call" : self.api_call_state}
        
        self.priority_states = list()
        self.priority_actions = dict()
        
        self.current_state = self.initial_state
    
    def sort_my_slots(self,slots_given) :
        slots_sorted = list()
        
        if "user_account" in slots_given :
            slots_sorted.append("user_account")
            slots_given.remove("user_account")
        
        if "destination_name" in slots_given :
            slots_sorted.append("destination_name")
            slots_given.remove("destination_name")
        
        if "amount" in slots_given :
            slots_sorted.append("amount")
            slots_given.remove("amount")
        
        for slot in slots_given :
            slots_sorted.append(slot)
        
        return slots_sorted
    
    # store any new values given by the user
    def record_user_values(self,user_action) :
        
        if type(user_action.get_values()) == dict :
            
            for slot,values in user_action.get_values().items() :
                self.user_values[slot] = values
                
     # remove the slots given from the list of slots to ask           
    def remove_informed_slots(self,user_action) :
        
        for slot in user_action.get_slots() :
            
            if slot in self.slots_to_ask :
                
                self.slots_to_ask.remove(slot)
                
    def speak(self,user_action) :
        
        if user_action == None :
            
            print("user_action received is None")
        
        next_state , bot_action = self.current_state(user_action)
        self.current_state = self.states[next_state]
        
        return bot_action
        
    # meet the initial state, here the user may provide one or more than one values
    def initial_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if user_action.get_slots() :
            
            if "intent" in user_action.get_slots() and len(user_action.get_slots()) > 1 :
                
                next_state = "check_initial"
                slots_given = user_action.get_slots()[1:] 
                slot_message = " "
                for slot in slots_given :
                    slot_message += "{}:{},".format(slot,self.user_values[slot])
                bot_action = Action(actor="API",
                                    action="initial_slots_check",
                                    slots=user_action.get_slots(),
                                    values=None,
                                    message=slot_message[:-1])
            
            else :
                
                next_state = self.slots_to_ask[0]
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=[next_state],
                                    values=None,
                                    message="requesting the values for {}".format(next_state))        
        else :           
            
            next_state = "initial"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=["intent"],
                                values=None,
                                message="Get the intent first")
        
        return next_state , bot_action
    
    def check_initial_state(self,user_action) :
        # if the below message is received then it means that initial check is successful and move on to the next appropriate slots
        
        if user_action.get_message() == "initial_slots_check : success" :
            
            if not self.slots_to_ask :
                
                next_state = "confirmation_state"
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=None,
                                    values=None,
                                    message="confirm transaction ?")
            
            else :
                
                next_state = self.slots_to_ask[0]
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=[next_state],
                                    values=None,
                                    message="request for {} ".format(next_state))
        
        else :
            
            self.priority_states = user_action.get_slots()
            self.priority_actions = user_action.get_values()
            
            next_state = self.priority_states[0]
            bot_action = self.priority_actions[next_state]
            
            self.priority_states.remove(next_state)
        
        return next_state , bot_action
    
    def account_state(self,user_action) :
        
        # if user account has been given then 
        if "user_account" in user_action.get_slots() :
            
            # remove the slot which has already been asked
            self.remove_informed_slots(user_action)
                
            # update user infomation
            user_values = user_action.get_values()
            
            # record and store all the values given by the user
            self.record_user_values(user_action)
            
            
            # pick a slot to ask randomly from the remaining slots_to_ask
            next_state = "check_account"
            
            # perform the corresponding bot information
            bot_action = Action(actor="API",
                                action="account_check",
                                slots=["user_account"],
                                values=None,
                                message="user_account:{}".format(self.user_values["user_account"]))
                    
        else :
            
            next_state = "user_account"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=["user_account"],
                                values=None,
                                message="requesting user to specify the account")
            
        return next_state , bot_action
    
    def check_account_state(self,user_action) :
        
        if user_action.get_message() == "account_check : success" :
            
            if "amount" in self.user_values.keys() :
                
                next_state = "check_amount"
                bot_action = Action(actor="API",
                                    action="amount_check",
                                    slots=["limit","balance"],
                                    values=None,
                                    message=" user_account:{} amount:{}".format(self.user_values["user_account"],self.user_values["amount"]))
            
            else :
                
                if self.priority_states :
                    next_state = self.priority_states[0]
                    bot_action = self.priority_actions[next_state]
                
                    self.priority_states.remove(next_state)
            
                elif not self.slots_to_ask :
                    
                    next_state = "confirmation_state"
                    bot_action = Action(actor="Bot",
                                        action="request",
                                        slots=None,
                                        values=None,
                                        message="confirm transaction ?")
            
                else :
                    
                    next_state = self.slots_to_ask[0]
                    bot_action = Action(actor="Bot",
                                        action="request",
                                        slots=[next_state],
                                        values=None,
                                        message="request for {} ".format(next_state))        
        else :
            
            next_state = "change_account"
            slot_message = ",".join(user_action.get_slots())
            bot_message = "It seems that you have not entered a valid account, you available accounts are {}, would you like change the source account ?".format(slot_message)
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=None,
                                values=None,
                                message=bot_message,
                                description="CHANGE_ACCOUNT")
        
        return next_state , bot_action
    
    def change_account_state(self,user_action) :
        
        if user_action.get_message() == "accept" :
            
            next_state = "user_account"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=[next_state],
                                values=None,
                                message="Requesting user to provide new user account")
        
        else :
            
            next_state = "end_call"
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="You denied to change the account")
        
        return next_state , bot_action 
    
    def destination_state(self,user_action) :
        # remove the slot already asked
        self.remove_informed_slots(user_action)
            
        # update the user information with the new values got
        self.record_user_values(user_action)
        
        if "destination_name" in user_action.get_slots() :
            
            # sample out a new state based on the remaining slots to ask
            next_state = "check_destination"
            bot_action = Action(actor="API",
                                action="destination_name_check",
                                slots=["destination_name"],
                                values=None,
                                message="destination_name:{}".format(self.user_values["destination_name"]))
        
        else :
            
            next_state = "destination_name"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=["destination_name"],
                                values=None,
                                message="Provide the Name of the Receiver")
        
        return next_state , bot_action
    
    def check_destination_name_state(self,user_action) :
        
        if user_action.get_message() == "destination_name_check : success" :
            
            if self.priority_states :
                next_state = self.priority_states[0]
                bot_action = self.priority_actions[next_state]
                
                self.priority_states.remove(next_state)
                
            elif not self.slots_to_ask :
                
                next_state = "confirmation_state"
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=None,
                                    values=None,
                                    message="confirm transaction ?")
                
            else :
                next_state = self.slots_to_ask[0]
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=[next_state],
                                    values=None,
                                    message="Requesting the name for {}".format(next_state))
        
        else :
            
            next_state = "change_destination_name"
            slot_message = ",".join(user_action.get_slots())
            bot_message = "The recipient you are trying to provide doesn't exist, available list of recipients is {}, would you like to change the recipient ?".format(slot_message)
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=None,
                                values=None,
                                message=bot_message,
                                description="CHANGE_DESTINATION_NAME")
        
        return next_state , bot_action
    
    def change_destination_name_state(self,user_action) :
        
        if user_action.get_message() == "accept" :
            
            next_state = "destination_name"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=[next_state],
                                values=None,
                                message="Requesting user to provide new user account")
        
        else :
            
            next_state = "end_call"
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="User failed to change the account")
        
        return next_state , bot_action
    
    def amount_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "amount" in user_action.get_slots() :
             
            if "user_account" in self.user_values.keys() :
                
                # No random check this time because we have to check if the amount given is correct or not
                next_state = "check_amount"
                bot_action = Action(actor="API",
                                    action="amount_check",
                                    slots=["limit","balance"],
                                    values=None,
                                    message="user_account:{} amount:{}".format(self.user_values["user_account"],self.user_values["amount"]))
            
            else :
                
                next_state = self.slots_to_ask[0]
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=[next_state],
                                    values=None,
                                    message="requesting user to provide {} ".format(next_state))
        
        else :
            
            next_state = "amount"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=["amount"],
                                values=None,
                                message="requesting the user to provide the Amount")
            
        return next_state , bot_action

    
    def check_amount_state(self,user_action) :
        
        self.record_user_values(user_action)
        
        if user_action.get_message() == "amount_check : success" :
            
            if self.priority_states :
                next_state = self.priority_states[0]
                bot_action = self.priority_actions[next_state]
                
                self.priority_states.remove(next_state)
            
            elif not self.slots_to_ask :
                
                next_state = "confirmation_state"
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=None,
                                    values=None,
                                    message="confirm transaction ?")
            
            else :
                
                next_state = self.slots_to_ask[0]
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=[next_state],
                                    values=None,
                                    message="request for {} ".format(next_state))

        else :
            
            next_state = "change_amount"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=None,
                                values=None,
                                message="It seems the amount you provided can't be processed because your transaction limit is {} and your current balance is {} so the maximum you can transfer is {}, would you like to reduce your amount to this amount ?".format(self.user_values["limit"],self.user_values["balance"],self.user_values["max_transferable_amt"]),
                                description="CHANGE_TO_MAX_TRANSFERABLE_AMT")
        
        return next_state , bot_action
    
    
    def change_amount_state(self,user_action) :
        
        if user_action.get_message() == "accept" :
            
            self.user_values["amount"] = self.user_values["max_transferable_amt"]
            
            if self.priority_states :
                next_state = self.priority_states[0]
                bot_action = self.priority_actions[next_state]
                
                self.priority_states.remove(next_state)
            
            elif not self.slots_to_ask :
                
                next_state = "confirmation_state"
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=None,
                                    values=None,
                                    message="confirm transaction ?")
            
            else :
                
                next_state = self.slots_to_ask[0]
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=[next_state],
                                    values=None,
                                    message="request for {} ".format(next_state))
        
        else :
            
            next_state = "end_call"
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="Rejected to change the decision")
        
        return next_state , bot_action
    
    # This is a dead state and I don't know why it is here , but I don't know what will happen if I remove this function
    def balance_state(self,user_action) :
        return
    
    # ask for confirmation
    def confirmation_state(self,user_action) :
        
        if user_action.get_message() == "accept" :
            
            next_state = "api_call"
            api_value = self.user_values["user_account"] + " " + self.user_values["destination_name"] + " "  + str(self.user_values["amount"])
            bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=None,
                                values={"api_call" : api_value},
                                message="API_CALL",
                                description="API_CALL")
        
        else :
            
            next_state = "end_call"
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="User refused to confirm transaction")
        
        return next_state, bot_action

    # end the call
    def end_call_state(self,user_action) :
        
        print("inside end_call state")
        
        return
    
    # Api call state
    def api_call_state(self,user_action) :
        
        if user_action.get_message() == "api_call success" :
            
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="{} conducted successfully, ciao !!".format(self.user_values["intent"]))
        
        else :
            
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="error in processing {}".format(self.user_values["intent"]))
        
        next_state = "end_call"
        
        return next_state , bot_action


# **Creating Account Balance Bot**
# 
# The class below, creates a bot capable on conversing - through actions - in the Account Balance Domain.

# In[11]:


class Account_bot(object) :
    
    def __init__(self) :
        
        self.last_slot = None
        self.list_of_slots = ["user_account","destination_name","amount"]
        self.slots_to_ask = ["user_account","destination_name","amount"]
        self.user_values = dict()
        self.states = {"initial" : self.initial_state ,
                       "list_accounts" : self.list_accounts_state,
                       "select_account" : self.select_account_state,
                       "api_call" : self.api_call_state,
                       "end_call" : self.end_call_state}
        
        self.priority_states = list()
        self.priority_actions = dict()
        
        self.current_state = self.initial_state
    
    def sort_my_slots(self,slots_given) :
        slots_sorted = list()
        
        if "user_account" in slots_given :
            slots_sorted.append("user_account")
            slots_given.remove("user_account")
        
        if "destination_name" in slots_given :
            slots_sorted.append("destination_name")
            slots_given.remove("destination_name")
        
        if "amount" in slots_given :
            slots_sorted.append("amount")
            slots_given.remove("amount")
        
        for slot in slots_given :
            slots_sorted.append(slot)
        
        return slots_sorted
    
    # store any new values given by the user
    def record_user_values(self,user_action) :
        
        if type(user_action.get_values()) == dict :
            
            for slot,values in user_action.get_values().items() :
                self.user_values[slot] = values
                
     # remove the slots given from the list of slots to ask           
    def remove_informed_slots(self,user_action) :
        
        if user_action.get_slots() :
            for slot in user_action.get_slots() :
                if slot in self.slots_to_ask :
                    self.slots_to_ask.remove(slot)
                
    def speak(self,user_action) :
        
        if user_action == None :
            
            print("user_action received is None")
        
        next_state , bot_action = self.current_state(user_action)
        self.current_state = self.states[next_state]
        
        return bot_action
        
    # meet the initial state, here the user may provide one or more than one values
    # request intent if not given already
    def initial_state(self,user_action) :
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "intent" in user_action.get_slots() :
            next_state = "list_accounts"
            bot_action = Action(actor="API",
                               action="request_accounts",
                               slots=["name"],
                               values=None,
                               message="accounts:{}".format(self.user_values["name"]))
        else :
            next_state = "initial"
            bot_action = Action(actor="Bot",
                               action="request",
                               slots=["intent"],
                               values=None,
                               message="requesting the intent from the user")
        return next_state , bot_action
    
    def list_accounts_state(self,user_action) :
        
        if user_action.get_description() == "LIST_OF_SLOTS" :
            next_state = "select_account"
            slot_message = ",".join(user_action.get_slots())
            bot_message = "You have the following accounts : {} , which one do you wish ?".format(slot_message)
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=None,
                                values=None,
                                message=bot_message,
                                description="SELECT_ACCOUNT")
        else : 
            next_state = "list_accounts"
            bot_action = Action(actor="API",
                               action="request_accounts",
                               slots=["name"],
                               values=None,
                               message="accounts:{}".format(self.user_values["name"]))
            
        return next_state , bot_action
        
    def select_account_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "user_account" in user_action.get_slots() :
            next_state = "api_call"
            api_value = self.user_values["user_account"]
            bot_action = Action(actor="Bot",
                               action="api_call",
                               slots=None,
                               values={"api_call" : api_value},
                               message="API_CALL",
                               description="API_CALL")
        else :
            next_state = "select_account"
            bot_action = Action(actor="Bot",
                               action="request",
                               slots=None,
                               values=None,
                               message="Please select an account")
        
        return next_state , bot_action
    
    def api_call_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if user_action.get_message().startswith("api_call : success") :
            next_state = "end_call"
            bot_message = "your current balance for account:{} is {}".format(self.user_values["user_account"],self.user_values["balance"])
            bot_action = Action(actor="Bot",
                                action="end_call",
                               slots=None,
                               values=None,
                               message=bot_message)
        else :
            next_state = "end_call"
            bot_action = Action(actor="Bot",
                               action="end_call",
                               slots=None,
                               values=None,
                               message="error in processing request !!")
        
        return next_state , bot_action
    
    def end_call_state(self,user_action) :
        print("Reached end of transaction")
        return


# **Creating Transaction History Domain**
# 
# This bot creates a bot capable of conversing - through actions - in the Transaction History Domain.

# In[12]:


class Transaction_history_bot(object) :
    
    def __init__(self) :
        
        self.last_slot = None
        self.list_of_slots = ["user_account","destination_name","amount"]
        self.slots_to_ask = ["user_account","destination_name","amount"]
        self.user_values = dict()
        self.states = {"initial" : self.initial_state ,
                       "list_accounts" : self.list_accounts_state,
                       "select_account" : self.select_account_state,
                       "credit_debit" : self.credit_debit_state,
                       "destination_name" : self.destination_name_state,
                       "destination_check" : self.check_destination_name_state,
                       "change_destination_name" : self.change_destination_name_state,
                       "api_call" : self.api_call_state,
                       "end_call" : self.end_call_state}
        
        self.priority_states = list()
        self.priority_actions = dict()
        
        self.current_state = self.initial_state
    
    def sort_my_slots(self,slots_given) :
        slots_sorted = list()
        
        if "user_account" in slots_given :
            slots_sorted.append("user_account")
            slots_given.remove("user_account")
        
        if "destination_name" in slots_given :
            slots_sorted.append("destination_name")
            slots_given.remove("destination_name")
        
        if "amount" in slots_given :
            slots_sorted.append("amount")
            slots_given.remove("amount")
        
        for slot in slots_given :
            slots_sorted.append(slot)
        
        return slots_sorted
    
    # store any new values given by the user
    def record_user_values(self,user_action) :
        
        if type(user_action.get_values()) == dict :
            
            for slot,values in user_action.get_values().items() :
                self.user_values[slot] = values
                
     # remove the slots given from the list of slots to ask           
    def remove_informed_slots(self,user_action) :
        
        if user_action.get_slots() :
            for slot in user_action.get_slots() :
                if slot in self.slots_to_ask :
                    self.slots_to_ask.remove(slot)
                
    def speak(self,user_action) :
        
        if user_action == None :
            
            print("user_action received is None")
        
        next_state , bot_action = self.current_state(user_action)
        self.current_state = self.states[next_state]
        
        return bot_action
        
    # meet the initial state, here the user may provide one or more than one values
    # request intent if not given already
    def initial_state(self,user_action) :
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "intent" in user_action.get_slots() :
            next_state = "list_accounts"
            bot_action = Action(actor="API",
                               action="request_accounts",
                               slots=["name"],
                               values=None,
                               message="accounts:{}".format(self.user_values["name"]))
        else :
            next_state = "initial"
            bot_action = Action(actor="Bot",
                               action="request",
                               slots=["intent"],
                               values=None,
                               message="requesting the intent from the user")
        return next_state , bot_action
    
    def list_accounts_state(self,user_action) :
        
        if user_action.get_description() == "LIST_OF_SLOTS" :
            next_state = "select_account"
            slot_message = ",".join(user_action.get_slots())
            bot_message = "You have the following accounts : {} , which one do you wish ?".format(slot_message)
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=None,
                                values=None,
                                message=bot_message,
                                description="SELECT_ACCOUNT")
        else : 
            next_state = "list_accounts"
            bot_action = Action(actor="API",
                               action="request_accounts",
                               slots=["name"],
                               values=None,
                               message="accounts:{}".format(self.user_values["name"]))
            
        return next_state , bot_action
        
    def select_account_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "user_account" in user_action.get_slots() :
            next_state = "credit_debit"
            bot_action = Action(actor="Bot",
                               action="request",
                               slots=["credit_debit"],
                               values=None,
                               message="requesting credit or debit information",
                               description="credit or debit information")
        else :
            next_state = "select_account"
            bot_action = Action(actor="Bot",
                               action="request",
                               slots=None,
                               values=None,
                               message="Please select an account")
        
        return next_state , bot_action
    
    def credit_debit_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "credit_debit" in user_action.get_slots() :
            next_state = "destination_name"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=["destination_name"],
                                values=None,
                                message="requesting the user to provide the destination name")
        else :
            next_state = "credit_debit"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=["credit_debit"],
                                values=None,
                                message="requesting credit or debit information")
        
        return next_state , bot_action
    
    def destination_name_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "destination_name" in user_action.get_slots() :
            
            next_state = "destination_check"
            bot_action = Action(actor="API",
                                action="destination_name_check",
                                slots=None,
                                values=None,
                                message="destination_name:{}".format(self.user_values["destination_name"]))
            
        else :
            next_state = "destination_name"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=["destination_name"],
                                values=None,
                                message="requesting user to provide destination_name")
        
        return next_state , bot_action
            
    def check_destination_name_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if user_action.get_message() == "destination_name_check : success" :
            
            next_state = "api_call"
            api_value = self.user_values["user_account"] + " " + self.user_values["credit_debit"] + " " + self.user_values["destination_name"]
            bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=None,
                                values={"api_call" : api_value},
                                message="API_CALL",
                                description="API_CALL")
        else :
            
            next_state = "change_destination_name"
            slot_message = ",".join(self.user_values["destination_names"])
            bot_message = "The recipient you provided is not registered, available list of recipients are : {}".format(slot_message)
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=None,
                                values=None,
                                message=bot_message,
                                description="CHANGE_DESTINATION_NAME")
            
        return next_state , bot_action
    
    def change_destination_name_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if user_action.get_message() == "accept" :
            next_state = "destination_name"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=["destination_name"],
                                values=None,
                                message="requesting user to give new destination name")
        else :
            next_state = "end_call"
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="User denied to change destination name",
                                description="NO_CHANGE_IN_DESTINATION_NAME")
        
        return next_state , bot_action
    
    def api_call_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if user_action.get_message().startswith("api_call : success") :
            next_state = "end_call"
            bot_action = Action(actor="Bot",
                                action="end_call",
                               slots=None,
                               values=None,
                               message="api_call successful !!")
        else :
            next_state = "end_call"
            bot_action = Action(actor="Bot",
                               action="end_call",
                               slots=None,
                               values=None,
                               message="error in processing request !!")
        
        return next_state , bot_action
    
    def end_call_state(self,user_action) :
        print("Reached end of transaction")
        return


# ### The dialog generator (the simplest piece of the code)
# 
# Here we are generating dialogs based on "Actions".
# We always keep track of the last transaction performed. If last_action is an *"end_call"* then we conclude our dialog.
# We do this for each of the 50 dialogs

# In[13]:


transaction_dialogs = list()
for i in range(1000) :
    
    dialog = list()
    user_bot = Transaction_user()
    transaction_bot = Transaction_bot()
    
    user_action = Action(actor="User",action=None,slots=None,values=None,message="<SILENCE>")
    bot_action = Action(actor="Bot",action="request",slots=["intent"],values=None,message="Get the intent first")
    dialog.append(user_action)
    dialog.append(bot_action)
    
    latest_action = None
    
    while latest_action != "end_call" :
        user_action = user_bot.speak(bot_action)
        bot_action = transaction_bot.speak(user_action)
        latest_action = bot_action.get_action()
        dialog.append(user_action)
        dialog.append(bot_action)
    
    transaction_dialogs.append(dialog)


# In[14]:


account_dialogs = list()
for i in range(1000) :
    
    dialog = list()
    user_bot = Account_user()
    transaction_bot = Account_bot()
    
    user_action = Action(actor="User",action=None,slots=None,values=None,message="<SILENCE>")
    bot_action = Action(actor="Bot",action="request",slots=["intent"],values=None,message="Get the intent first")
    dialog.append(user_action)
    dialog.append(bot_action)
    
    latest_action = None
    
    while latest_action != "end_call" :
        user_action = user_bot.speak(bot_action)
        bot_action = transaction_bot.speak(user_action)
        latest_action = bot_action.get_action()
        dialog.append(user_action)
        dialog.append(bot_action)
    
    account_dialogs.append(dialog)


# In[15]:


transaction_history_dialogs = list()
for i in range(1000) :
    
    dialog = list()
    user_bot = Transaction_history_user()
    transaction_bot = Transaction_history_bot()
    
    user_action = Action(actor="User",action=None,slots=None,values=None,message="<SILENCE>")
    bot_action = Action(actor="Bot",action="request",slots=["intent"],values=None,message="Get the intent first")
    dialog.append(user_action)
    dialog.append(bot_action)
    
    latest_action = None
    
    while latest_action != "end_call" :
        user_action = user_bot.speak(bot_action)
        bot_action = transaction_bot.speak(user_action)
        latest_action = bot_action.get_action()
        dialog.append(user_action)
        dialog.append(bot_action)
    
    transaction_history_dialogs.append(dialog)


# ### Printing the dialogs
# 
# We have to remeber that the dialog is a set of action and so to format them into a useful information here is the protocol that we will follow :
# 1. if its a request or inform action then we check if there is a slot associated.
#     
#     a. if there is then we know that the action is a request/inform with a slot and value associated.
#     
#     b. If there is no slot then we are assuming it's the case when there is an unexpected action occuring and in this case we print the message associated with the action.
#     
# 2. If it's an api call then print the api_call with the appropriate values
# 
# 3. If it's an end_call then print the message that is given with the ending of the call.

# ### How to Read the Data :
# 
# Every dialog is a set of actions.
# 
# When printing it is printed as :
# 
# {actor} : {action} {slots_asked} ==> {slots_given(if any)}
# 
# So the Bot actions are printed as follows 
# 
# Bot : { request/api_call/end_call }  {[slots asked]/message given(if any)}
# 
# And the User actions are printed as follows
# 
# User : {inform} {[slots given]} {[slot values]/message}
# 
# On Similar lines, the Transaction_Check_Software and Balance_check_Software follow the format of Bot action and Software follows the format of User action

# ### How to Write the Data to File
# 
# There are three files that are used for the puprose here :
# a. raw_data.txt
# b. train_data.txt
# c. candidate.txt
# 
# **a. raw_data.txt**
# 
# This file is supposed to print the data in a human-readable format. The General representation of a dialog is as folows :
#     
#     1. {Actor} : {Dialog}
#     so a good example of this format is -:
#         1. User : <SILENCE>
#         2. Bot : How can I help you today
#         3. User : I would like to know my account balance
#         4. API : request list_of_accounts:{name=Sourabh}
#         5. API_RESP : inform list_of_accounts:{Credit,Savings}
#         6. Bot : You have the following list of accounts : Credit,Savings , which one ?
#         7. User : Let's see Savings
#         8. Bot : api_call account:{Savings}
#         9. API_RESP : inform account:{Savings} balance:{xxx}
#         10.Bot : Your balance for Savings account is xxx euros, ciao !!
#       
# **b. train_data.txt**
# 
# The file is supposed to be written as the file for the training data in the conversation.
# A Sample Conversation is written below :
# 
#     1 <SILENCE>	how can i help you today ?
#     2 I would like to see my transaction history	request_accounts accounts:Simone
#     3 inform list_of_accounts : Savings	You have the following accounts : Savings , which one do you wish ?
#     4 Savings	Which information should I give credit or debit ?
#     5 let's see debit	Can I ask what is the name of the partner ?
#     6 it's for Serra	api_call Savings debit Serra
#     7 inform api_call : success	end_call api_call successful !!
#     
# **c. candidate.txt**
# 
# The file is suppose to create the candidates for the appropriate conversations.
# A Sample of candidates is written below.
# 
#     1 amount_check  user_account:Savings amount:9000
#     1 It seems the amount you provided can't be processed because your transaction limit is 5000 and your current balance is 8000 so the maximum you can transfer is 5000, would you like to reduce your amount to this amount ?
#     1 The recipient you are trying to provide doesn't exist, available list of recipients is Tahir,Sourabh,Samuel,Vevake, would you like to change the recipient ?
#     1 It seems that you have not entered a valid account, you available accounts are Savings, would you like change the source account ?
#     1 api_call Savings Marco 400
#     1 The recipient you are trying to provide doesn't exist, available list of recipients is Sourabh,Matteo, would you like to change the recipient ?
#     1 api_call Credit Samuel 400
#     1 destination_name_check destination_name:Vevake
#     1 amount_check user_account:Checkin , amount:1600
#     1 account_check user_account:Credit
#     1 amount_check  user_account:Credit amount:2400
#     1 api_call Savings Marco 4500

# In[16]:


dialogs = list()
dialogs.extend(transaction_dialogs)
dialogs.extend(account_dialogs)
dialogs.extend(transaction_history_dialogs)


# **Creating Start Dialogs**
# 
# *start_dialogs* is the set of actions till the point where we determine the intent of the conversation from the user.
# 
# We will then use this set of *start_dialogs* to create the training data for the main memory network.
# 
# For example a sample of *start_dialogs* is :
# 
# 1.User(Action=Silence)
# 
# 2.Bot(Action=Request Intent)
# 
# 3.User(Action=Inform Intent)
# 
# 4.Bot(Action=Call appropriate Memory Network)

# In[17]:


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


# **Create Raw Data**
# 
# The function below converts the given set of dialogs into a human readable file and writes it to the appropriate file

# In[18]:


def create_raw_data(file_directory="data/",file_name="data.txt",dialogs=None) :
    
    if not os.path.exists(file_directory) :
        os.makedirs(file_directory)
    
    file_handle = open(os.path.join(file_directory,file_name),"w")
    
    for dialog in dialogs :
        for action in dialog :
            file_handle.write(action.get_dialog())
            file_handle.write("\n")
        file_handle.write("\n")
    file_handle.close()


# **Writing Raw Data for the Transaction Domain**
# 
# The code below writes the training data for the Transaction Domain Memory Network in a human readable format such that one can asses the quality of the conversation.

# In[19]:


create_raw_data(file_directory="data/transaction_data/",file_name="raw_data.txt",dialogs=transaction_dialogs)


# **Writing Raw Data for the Account Balance Domain**
# 
# The code below writes the training data for the Account Balance Memory Network in a Human Readable format such that once can asses the quality of the conversation.

# In[20]:


create_raw_data(file_directory="data/account_balance_data/",file_name="raw_data.txt",dialogs=account_dialogs)


# **Writing Raw Data for The Transaction History Domain**
# 
# The code below writes the training data for the Transaction History Memory Network in a Human Readable format such that one can asses the quality of the conversation

# In[21]:


create_raw_data(file_directory="data/transaction_history_data/",file_name="raw_data.txt",dialogs=transaction_history_dialogs)


# **Writing Raw Data for The Start Memory Network**
# 
# The code below writes the training data for the Start Memory Network in a Human Readable Format such that one can asses the quality of the conversation.

# In[22]:


create_raw_data(file_directory="data/start_data/",file_name="raw_data.txt",dialogs=start_dialogs)


# **Writing Raw Data for One Memory Network**
# 
# The code below writes the training data for the One Memory Network in a Human readable format such that one can asses the quality of the conversation.

# In[23]:


one_dialogs = dialogs
random.shuffle(one_dialogs)


# In[24]:


create_raw_data(file_directory="data/one_data/",file_name="raw_data.txt",dialogs=one_dialogs)


# **Create Training Data Function**
# 
# The code below creates the training data from the provided dialogs and writes to the appropriate file

# In[25]:


def create_training_data(file_directory="data/",file_name="data.txt",dialogs=None) :
    
    if not os.path.exists(file_directory) :
        os.makedirs(file_directory)
        
    file_handle = open(os.path.join(file_directory,file_name),"w")
    for dialog in dialogs :
        count = 1
        for i in range(0,len(dialog),2) :
            file_handle.write("{} {}\t{}\n".format(str(count),dialog[i].get_dialog(with_actor=False),dialog[i+1].get_dialog(with_actor=False)))
            count += 1
        file_handle.write("\n")
    file_handle.close()


# **Training Data for Transaction Domain**
# 
# The code below creates the training data for the Transaction Memory Network(The Memory Network responsible for handling the Transaction Intent).

# In[26]:


create_training_data(file_directory="data/transaction_data/",file_name="train_data.txt",dialogs=transaction_dialogs)
create_training_data(file_directory="data/transaction_data/",file_name="val_data.txt",dialogs=transaction_dialogs)
create_training_data(file_directory="data/transaction_data/",file_name="test_data.txt",dialogs=transaction_dialogs)


# **Training Data for Account Balance Domain**
# 
# The code below creates the training data for the Account Balance Memory Network (The Memory Network responsible for handling Account Balance Intent).

# In[27]:


create_training_data(file_directory="data/account_balance_data/",file_name="train_data.txt",dialogs=account_dialogs)
create_training_data(file_directory="data/account_balance_data/",file_name="val_data.txt",dialogs=account_dialogs)
create_training_data(file_directory="data/account_balance_data/",file_name="test_data.txt",dialogs=account_dialogs)


# **Train Data for Transaction History Memory Network**
# 
# The code below creates the training data for the Transaction History Memory Network (The Memory Network responsible for handling the Transaction History Intent).

# In[28]:


create_training_data(file_directory="data/transaction_history_data/",file_name="train_data.txt",dialogs=transaction_history_dialogs)
create_training_data(file_directory="data/transaction_history_data/",file_name="val_data.txt",dialogs=transaction_history_dialogs)
create_training_data(file_directory="data/transaction_history_data/",file_name="test_data.txt",dialogs=transaction_history_dialogs)


# **Train Data for Start Memory Network**
# 
# The code below creates the training data for the Start Memory Network (The network which determines the intent of the conversation).

# In[29]:


create_training_data(file_directory="data/start_data/",file_name="train_data.txt",dialogs=start_dialogs)
create_training_data(file_directory="data/start_data/",file_name="val_data.txt",dialogs=start_dialogs)
create_training_data(file_directory="data/start_data/",file_name="test_data.txt",dialogs=start_dialogs)


# **Train Data for One Memory Network**
# 
# The code below creates the training data for the One Memory Network (The one that tries to handle all things at once).

# In[30]:


create_training_data(file_directory="data/one_data/",file_name="train_data.txt",dialogs=one_dialogs)
create_training_data(file_directory="data/one_data/",file_name="val_data.txt",dialogs=one_dialogs)
create_training_data(file_directory="data/one_data/",file_name="test_data.txt",dialogs=one_dialogs)


# **Create Candidate Function**
# 
# The function below creates the candidate list from the provided dialogs and writes it to the appropriate file

# In[31]:


def create_candidates(file_directory="data/",file_name="data.txt",dialogs=None) :
    candidate_set = set()
    if not os.path.exists(file_directory) :
        os.makedirs(file_directory)
        
    for dialog in dialogs :
        for action in dialog :
            if action.get_actor() == "Bot" or action.get_actor() == "API" :
                candidate_set.add(action.get_dialog(with_actor=False))
    file_handle = open(os.path.join(file_directory,file_name),"w")
    for candidate in candidate_set :
        file_handle.write("1 {}\n".format(candidate))
    file_handle.close()


# **Writing Transaction Dialog Candidates**
# 
# The code below creates the candidate file for the conversations in the Transaction Domain, i.e Bot Utterances in the Transaction Domain

# In[32]:


create_candidates(file_directory="data/transaction_data/",file_name="candidates.txt",dialogs=transaction_dialogs)


# **Writing Account Dialog Candidates**
# 
# The code below creates the candidate file for the conversations in the Account Balance Domain, i.e Bot Utterances in the Account Balance Domain.

# In[33]:


create_candidates(file_directory="data/account_balance_data/",file_name="candidates.txt",dialogs=account_dialogs)


# **Writing Transaction History Dialog Candidates**
# 
# The code below creates the candidate file for the conversations in the transaction history domain, i.e Bot Utterances in the Transaction History Domain.

# In[34]:


create_candidates(file_directory="data/transaction_history_data/",file_name="candidates.txt",dialogs=transaction_history_dialogs)


# **Writing Start Dialog Candidates**
# 
# The code below creates the *candidate file* for the initial conversation, i.e before determining which Memory Network to call.

# In[35]:


create_candidates(file_directory="data/start_data/",file_name="candidates.txt",dialogs=start_dialogs)


# **Writing One Dialog Candidates**
# 
# The code below creates *candidate file* for the One Memory Network, i.e the one that is handling all the intents at once

# In[36]:


create_candidates(file_directory="data/one_data/",file_name="candidates.txt",dialogs=one_dialogs)

