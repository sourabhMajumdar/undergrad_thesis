import random
import sys
import copy
sys.path.append("..")
from utils import Action

class Block_card_user(object) :
    def __init__(self,
                 templates=None,
                 list_of_user_profiles=None,
                 user_values=None,
                 turn_compression=False,
                 new_api=False,
                 another_slot=False,
                 audit_more=False) :
        
        # Below is the available pool of values from which we will create a Custom user for the transaction
        #self.user_names = ["Sourabh","Serra","Simone","Marco","Vevake","Matteo","Tahir","Samuel"]
        self.user_accounts = user_values["user_accounts"]
        self.user_card_names = user_values["card_names"]
        self.slots = ["card_id"]
        self.templates = templates
        
        self.priority_states = list()
        self.priority_actions = dict()
        
        self.turn_compression = turn_compression
        self.new_api = new_api
        self.another_slot = another_slot
        self.audit_more = audit_more
        
        self.override = False
        self.state_track = dict()
        self.state_track["CHANGE_CARD_ID"] = 0
        self.state_track["CHANGE_CARD_NAME"] = 0
        self.state_track["CHANGE_ACCOUNT"] = 0
        
        # create the custom user
        self.user = dict()
        
        row_chosen = random.randint(0,len(list_of_user_profiles)-1)
        user_chosen = list_of_user_profiles[row_chosen]
        
        self.create_user_profile(user_chosen)
    
    def sort_my_slots(self,slots_given) :
        slots_sorted = list()
        
        if "card_id" in slots_given :
            slots_sorted.append("card_id")
            slots_given.remove("card_id")
        
        
        for slot in slots_given :
            slots_sorted.append(slot)
        
        return slots_sorted
    
    def create_user_profile(self,user_chosen) :
        
        # Every value is assigned randomly 
        
        # selectinng name of sender and reciever
        
        self.user["name"] = user_chosen["name"]
                
        #selecting the usr_account to make the transaction from
        
        
        # select at random the number of account the user has.
        #number_of_account = random.randint(1,len(self.user_accounts))
        
        #self.user["user_accounts"] = random.sample(self.user_accounts,number_of_account)
        #self.user["user_accounts"].sort()
        
        
        
        self.user["user_accounts"] = user_chosen["user_accounts"].strip().split(',')
        
        # select a list of accounts from the given sample
        
        self.user["user_account"] = random.sample(self.user_accounts,1)[0]
        
        # creating a card id for the user
        r_account = random.sample(self.user_accounts,1)[0]
        r_card_name = random.sample(self.user_card_names,1)[0]
        
        self.user["card_id"] = "{}-{}".format(r_account,r_card_name)
        self.user["card_names"] = self.user_card_names
        self.user["card_name"] = random.sample(self.user_card_names,1)[0]
        
        
        #number_of_accounts_with_cards = random.randint(0,len(self.user_accounts))
        
        self.user_account_card_name_pair = dict()
        self.user_account_with_cards = list()
        
        self.user["card_ids"] = user_chosen["card_ids"].strip().split(',')
        
        for card_id in self.user["card_ids"] :
            card_name, linked_account = card_id.split('-')
            if linked_account not in self.user_account_with_cards :
                self.user_account_with_cards.append(linked_account)
            
            if linked_account in self.user_account_card_name_pair.keys() :
                list_of_cards = self.user_account_card_name_pair[linked_account]
            else :
                list_of_cards = list()
                
            list_of_cards.append(card_name)
            self.user_account_card_name_pair[linked_account] = list_of_cards
        
        
        
                        
        # setting up the intent
        self.user["intent"] = "block_card"
        self.user["domain_description"] = "block_card_memory_network"
    
    # Returns the respective value of the slot
    
    def remove_slot(self,slot_given) :
        if slot_given in self.slots :
            self.slots.remove(slot_given)
            
    def get_value(self,slot_asked) :
        
        return self.user[slot_asked]
    
    # This function is called when the bot has made a request but no slots have been provided, hence we look at the description of the action to figure out what the request is
    def perform_random_action(self,bot_action) :
        
        user_action = None
        actual_actor = None
        actual_action = None
        accept_message = str()
        reject_message = str()
        values_to_give = dict()
        pattern_to_give = list()
        
        if bot_action.get_description() == "SELECT_ACCOUNT" :
               
            self.user["user_account"] = random.sample(self.user_accounts,1)[0]
            
            user_action = Action(actor="User",
                                action="inform",
                                slots=["user_account"],
                                values={"user_account" : self.user["user_account"]},
                                message="providing value for user_account",
                                templates=self.templates)
            
        elif bot_action.get_description() == "SELECT_CARD" :
            
            user_action = Action(actor="User",
                                 action="inform",
                                 slots=["card_name"],
                                 values={"card_name" : self.user["card_name"]},
                                 message="providing the card name to the bot",
                                 templates=self.templates)
        
        else :
            
            if bot_action.get_description() == "API_CALL" :
                
                actual_actor = "API"
                actual_action = "api_response"
                accept_message = "api_response:block_card_api, api_result:success"
                reject_message = "api_response:block_card_api, api_result:failed"
                
            
            elif bot_action.get_description() == "CHANGE_ACCOUNT" :
                
                
                
                new_account = random.sample(self.user_accounts,1)[0]
                
                while new_account == self.user["user_account"] :
                    new_account = random.sample(self.user_accounts,1)[0]
                
                self.user["user_account"] = new_account
                
                if self.state_track["CHANGE_ACCOUNT"] > 2 :
                    self.override = True
                    new_account = random.sample(self.user["user_accounts"],1)[0]
                    self.user["user_account"] = new_account
                
                actual_actor = "User"
                actual_action = "inform"
                accept_message = "accept"
                reject_message = "reject"
                
                if self.turn_compression :
                    accept_message = "accept use {}".format(new_account)
                    pattern_to_give.append("turn_compression")
                    
                values_to_give = {"user_account" : new_account}
                self.state_track["CHANGE_ACCOUNT"] += 1
                
            elif bot_action.get_description() == "CHANGE_CARD_NAME" :
                
                
                new_card_name = random.sample(self.user_card_names,1)[0]
                
                while new_card_name == self.user["card_name"] :
                    new_card_name = random.sample(self.user_card_names,1)[0]
                    
                self.user["card_name"] = new_card_name
                if self.state_track["CHANGE_CARD_NAME"] > 2 :
                    self.override = True
                    new_card_name = random.sample(self.user["card_names"],1)[0]
                    self.user["card_name"] = new_card_name
                
                actual_actor = "User"
                actual_action = "inform"
                accept_message = "accept"
                reject_message = "reject"
                
                if self.turn_compression :
                    accept_message = "accept use {}".format(new_card_name)
                    pattern_to_give.append("turn_compression")
                    
                values_to_give = {"card_name" : new_card_name}
                
                self.state_track["CHANGE_CARD_NAME"] += 1
                
            elif bot_action.get_description() == "CHANGE_CARD_ID" :
                
                r_account = random.sample(self.user_accounts,1)[0]
                r_card_name = random.sample(self.user_card_names,1)[0]
                
                new_card_id = "{}-{}".format(r_account,r_card_name)
                
                while new_card_id == self.user["card_id"] :
                    r_account = random.sample(self.user_accounts,1)[0]
                    r_card_name = random.sample(self.user_card_names,1)[0]
                    
                    new_card_id = "{}-{}".format(r_account,r_card_name)
                    
                if self.state_track["CHANGE_CARD_ID"] > 2 :
                    self.override = True
                    
                    new_card_id = random.sample(self.user["card_ids"],1)[0]
                    self.user["card_id"] = new_card_id
                    #print("new card id chosen is : {}".format(new_card_id))
                    
                actual_actor = "User"
                actual_action = "inform"
                accept_message = "accept"
                reject_message = "reject"
                
                if self.turn_compression :
                    accept_message = "accept use {}".format(new_card_id)
                    pattern_to_give.append("turn_compression")
                    
                values_to_give = {"card_id" : new_card_id}
                self.state_track["CHANGE_CARD_ID"] += 1
            else :
                
                actual_actor = "User"
                actual_action = "inform"
                accept_message = "accept"
                reject_message = "reject"
            
            toss = random.randint(0,100)
            if toss > 10 or self.override :
                self.override = False
                user_action = Action(actor=actual_actor,
                                     action=actual_action,
                                     slots=None,
                                     values=values_to_give,
                                     message=accept_message,
                                     templates=self.templates,
                                     pattern_marker=pattern_to_give)
            else :
                
                user_action = Action(actor=actual_actor,
                                     action=actual_action,
                                     slots=None,
                                     values=values_to_give,
                                     message=reject_message,
                                     templates=self.templates)
        return user_action
    # This is the function that converses with the bot through 'Action' Objects
    def speak(self,bot_action) :
        user_action = None
        if bot_action.get_action() == "api_call" :
            
            user_action = self.api_response(bot_action)            

        elif bot_action.get_action() == "request" :
            
            if bot_action.get_slots() != None :
                
                if bot_action.get_slots()[0] != "intent" :
                    
                    if "card_id" in bot_action.get_slots() :
                        toss = random.randint(0,100)
                        
                        if toss > 20 :
                            user_value = self.get_value("card_id")
                            user_action = Action(actor="User",
                                                 action="inform",
                                                 slots=["card_id"],
                                                 values={"card_id" : user_value},
                                                 message="providing value for card_id",
                                                 templates=self.templates)
                        else :
                            
                            user_action = Action(actor="User",
                                                 action="card_id_not_know",
                                                 slots=None,
                                                 values={"user_account" : self.user["user_account"]},
                                                 message="Providing value for {}".format(bot_action.get_slots()[0]),
                                                 description="CARD_ID_NOT_KNOW",
                                                 templates=self.templates)
                    else :
                        
                        slot_to_inform = bot_action.get_slots()[0]
                    
                        if self.another_slot and self.slots :
                            slots_to_choose_from = copy.deepcopy(self.slots)
                            if len(slots_to_choose_from) > 1 :
                                self.remove_slot(slot_to_inform)
                                #slots_to_choose_from.remove(slot_to_inform)
                            
                            slot_chosen_to_inform = random.sample(slots_to_choose_from,1)[0]
                            value_for_other_slot = self.get_value(slot_chosen_to_inform)
                            
                            user_action = Action(actor="User",
                                                 action="inform",
                                                 slots=[slot_chosen_to_inform],
                                                 values={slot_chosen_to_inform : value_for_other_slot},
                                                 message="Providing value for {}".format(slot_chosen_to_inform),
                                                 description="ANOTHER_SLOT_VALUE",
                                                 templates=self.templates)
                            
                            self.remove_slot(slot_chosen_to_inform)
                            #self.slots.remove(slot_chosen_to_inform)
                        else :
                            
                            user_value = self.get_value(slot_to_inform)
                        
                            user_action = Action(actor="User",
                                                 action="inform",
                                                 slots=bot_action.get_slots(),
                                                 values={bot_action.get_slots()[0] : user_value},
                                                 message="Providing value for {}".format(bot_action.get_slots()[0]),
                                                 slot_concerned=bot_action.get_slots()[0],
                                                 templates=self.templates)
                            
                            self.remove_slot(slot_to_inform)
                            #self.slots.remove(slot_to_inform)
                
                else :
                    
                    rem = 0
                    pattern_to_give = list()
                    if self.new_api :
                        rem = 1
                        pattern_to_give.append("new_api")
                    
                    number_of_slots = random.randint(0,len(self.slots))
                    
                    while number_of_slots %2 != rem :
                        number_of_slots = random.randint(0,len(self.slots))
                        
                    slots_to_inform = random.sample(self.slots,number_of_slots)
                    all_slots = ["intent","domain_description"] + self.sort_my_slots(slots_to_inform)
                    values_to_inform = dict()
                    
                    for slot in all_slots :
                        values_to_inform[slot] = self.user[slot]
                    
                    values_to_inform["name"] = self.user["name"]
                        
                    user_action = Action(actor="User",
                                         action="inform",
                                         slots=all_slots,
                                         values=values_to_inform,
                                         message="Providing value for intent",
                                         templates=self.templates,
                                         pattern_marker=pattern_to_give)
            else:
                
                user_action = self.perform_random_action(bot_action)
        
        
        else :
            
            if bot_action.get_action() != None :
                user_action = self.perform_random_action(bot_action)
            else :
                user_action = Action(actor="User",
                                     action=None,
                                     slots=None,
                                     values=None,
                                     message="<SILENCE>",
                                     templates=self.templates)
        
        return user_action
    
    # when the bot takes the role of API then, the User should assume the role of API_RESP (i.e API_RESPONSE)
    def api_response(self,bot_action) :
    
        user_action = None
        
        # if the API action asks for a account check
        if bot_action.get_description() == "REQUEST_ACCOUNTS" :
            
            slot_message = ",".join(self.user["user_accounts"])
            bot_message = "api_response:request_accounts_api, list_of_accounts:{}".format(slot_message)
            user_action = Action(actor="API",
                                action=None,
                                slots = self.user["user_accounts"],
                                values=None,
                                message=bot_message,
                                description="LIST_OF_SLOTS",
                                templates=self.templates)
            
        elif bot_action.get_description() == "API_INITIAL_SLOT_CHECK" :
            flag = False
            error_message = list()
            order_of_slots = list()
            if "card_id" in bot_action.get_slots() and self.user["card_id"] not in self.user["card_ids"] :
                
                self.priority_states.append("change_card_id")
                order_of_slots.append("change_card_id")
                slot_message = ",".join(self.user["user_accounts"])
                bot_message = "It seems that you have not entered a valid account, you available accounts are {}, would you like change the source account ?".format(slot_message)
                self.priority_actions["change_card_id"] = Action(actor="Bot",
                                                                action="request",
                                                                slots=None,
                                                                values=None,
                                                                message=bot_message,
                                                                description="CHANGE_ACCOUNT",
                                                                templates=self.templates)
                
            if self.priority_states :
                order_message = ','.join(order_of_slots)
                user_action = Action(actor="API",
                                     action=None,
                                     slots=self.priority_states,
                                     values=self.priority_actions,
                                     message="api_response:initial_slot_check_api, api_result:failed, message:'{}'".format(order_message),
                                     templates=self.templates)
            else :
                user_action = Action(actor="API",
                                     action="api_response",
                                     slots=bot_action.get_slots(),
                                     values=None,
                                     message="api_response:initial_slot_check_api, api_result:success",
                                     templates=self.templates)
                
        elif bot_action.get_description() == "API_CARD_ID_CHECK" :
            
            #print("card ids allowed : {}".format(self.user["card_id"]))
            if self.user["card_id"] in self.user["card_ids"] :
                
                user_action = Action(actor="API",
                                     action="api_response",
                                     slots=["card_id"],
                                     values=None,
                                     message="api_response:check_card_id_api, api_result:success",
                                     templates=self.templates)
            else :
                
                user_action = Action(actor="API",
                                     action="api_response",
                                     slots=["card_id"],
                                     values=None,
                                     message="api_response:check_card_id_api, api_result:failed, message:'change_card_id'",
                                     templates=self.templates)
                
        elif bot_action.get_description() == "API_ACCOUNT_CHECK" :
            
            #print("checking account")
            if self.user["user_account"] in self.user_account_with_cards :
                
                if self.user["user_account"] in self.user["user_accounts"] :
                    
                    user_action = Action(actor="API",
                                         action="api_response",
                                         slots=["user_account"],
                                         values={"card_names" : self.user["card_names"]},
                                         message="api_response:account_check_api, api_result:success",
                                         templates=self.templates)
                else :
                    
                    slot_message = ','.join(self.user_account_with_cards)
                    api_message = "api_response:account_check_api, api_result:failed, message:'avalilable list of accounts : {}'".format(slot_message)
                    user_action = Action(actor="API",
                                         action="api_response",
                                         slots=self.user_account_with_cards,
                                         values={"user_accounts" : self.user_account_with_cards},
                                         message=api_message,
                                         description="NO_CARD_FOR_USER_ACCOUNT",
                                         templates=self.templates)
                    
            else :
                
                slot_message = ','.join(self.user["user_accounts"])
                api_message = "api_response:account_check_api, api_result:failed, message:'available list of accounts : {}'".format(slot_message)
                user_action = Action(actor="API",
                                     action="api_response",
                                     slots=self.user["user_accounts"],
                                     values={"user_accounts" : self.user["user_accounts"]},
                                     message=api_message,
                                     description="NO_USER_ACCOUNT",
                                     templates=self.templates)
                
        elif bot_action.get_description() == "API_CARD_NAME_CHECK" :
            
            
            if self.user["user_account"] in self.user_account_with_cards and self.user["card_name"] in self.user_account_card_name_pair[self.user["user_account"]] :
                
                card_id = "{}-{}".format(self.user["user_account"],self.user["card_name"])
                user_action = Action(actor="API",
                                     action="api_response",
                                     slots=["card_id"],
                                     values={"card_id" : card_id},
                                     message="api_response:card_name_check_api, api_result:success",
                                     templates=self.templates)
            else :
                
                slot_message = ','.join(self.user_account_card_name_pair[self.user["user_account"]])
                user_action = Action(actor="API",
                                     action="api_response",
                                     slots=self.user_account_card_name_pair[self.user["user_account"]],
                                     values={"card_names" : self.user_account_card_name_pair[self.user["user_account"]]},
                                     message="api_response:card_name_api, api_result:failed, message:'available list of cards is : {}'".format(slot_message),
                                     templates=self.templates)


            
        else :
            
            user_action = self.perform_random_action(bot_action)
        
        
        return user_action            