import random
import sys
import copy
sys.path.append("..")
from utils import Action

class Cancel_transaction_user() :
    def __init__(self,
                 templates=None,
                 list_of_user_profiles=None,
                 user_values=None,
                 turn_compression=False,
                 new_api=False,
                 another_slot=False,
                 audit_more=False) :
        
        # Below is the available pool of values from which we will create a Custom user for the transaction
        
        
        
        self.slots = ["transaction_id"]
        
        
        # slots for cacelling transaction
        self.user_accounts = user_values["user_accounts"]
        self.partner_names = user_values["partner_names"]
        self.money_transfered = user_values["amount_values"]
        self.templates = templates
        
        self.priority_states = list()
        self.priority_actions = dict()
        
        self.turn_compression = turn_compression
        self.new_api = new_api
        self.another_slot = another_slot
        self.audit_more = audit_more
        
        self.override = False
        self.state_track = dict()
        self.state_track["CHANGE_TRANSACTION_ID"] = 0
        self.state_track["CHANGE_PARTNER_NAME"] = 0
        
        # create the custom user
        self.user = dict()
        
        row_chosen = random.randint(0,len(list_of_user_profiles)-1)
        user_chosen = list_of_user_profiles[row_chosen]
        
        self.create_user_profile(user_chosen)
    
    def sort_my_slots(self,slots_given) :
        slots_sorted = list()
        
        if "transaction_id" in slots_given :
            slots_sorted.append("transaction_id")
            slots_given.remove("transaction_id")
        
        
        for slot in slots_given :
            slots_sorted.append(slot)
        
        return slots_sorted
    
    def create_user_profile(self,user_chosen) :
        
        
        #number_of_account = random.randint(1,len(self.user_accounts))
        
        #self.user["user_accounts"] = random.sample(self.user_accounts,number_of_account)
        #self.user["user_accounts"].sort()
        self.user["user_accounts"] = user_chosen["user_accounts"].strip().split(',')
        
        self.user["partner_name"] = random.sample(self.partner_names,1)[0]
        #number_of_partner_names = random.randint(0,len(self.partner_names))
        #self.user["partner_names"] = random.sample(self.partner_names,number_of_partner_names)
        self.user["partner_names"] = user_chosen["partner_names"].strip().split(',')
        # select a list of accounts from the given sample
        
        self.user["user_account"] = random.sample(self.user_accounts,1)[0]
        
        # creating a card id for the user
        r_account = random.sample(self.user_accounts,1)[0]        
        r_partner_name = random.sample(self.partner_names,1)[0]
        r_money_transfered = random.sample(self.money_transfered,1)[0]
        
        self.user["transaction_id"] = "{}-{}-{}".format(r_account,r_money_transfered,r_partner_name)
        
        self.partner_name_with_transaction_id = list()
        self.transaction_dictionary = dict()
        
        self.user["transaction_ids"] = user_chosen["transaction_ids"].strip().split(',')
        
        
        for transaction_id in self.user["transaction_ids"] :
            partner_name, money_transfered, account = transaction_id.split('-')
            if partner_name not in self.partner_name_with_transaction_id :
                self.partner_name_with_transaction_id.append(partner_name)
                
            self.transaction_dictionary[partner_name] = transaction_id
        
        
        
        #number_of_partners_to_transaction = random.randint(1,len(self.partner_names))
        #self.partner_name_with_transaction_id = random.sample(self.partner_names,number_of_partners_to_transaction)
        
        #self.transaction_dictionary = dict()
        #self.user["transaction_ids"] = list()
        
        
        #for partner in self.partner_name_with_transaction_id :
        #    r_account = random.sample(self.user_accounts,1)[0]
        #    self.transaction_dictionary[partner] = "{}-{}".format(r_account,partner)
        #    self.user["transaction_ids"].append("{}-{}".format(r_account,partner))
        
        number_of_blockable_transactions = random.randint(0,len(self.user["transaction_ids"]))
        
        
        self.blockable_transactions = random.sample(self.user["transaction_ids"],number_of_blockable_transactions)             
        # setting up the intent
        self.user["intent"] = "cancel_transaction"
        self.user["domain_description"] = "cancel_transaction_memory_network"
    
    # Returns the respective value of the slot
    def get_value(self,slot_asked) :
        
        return self.user[slot_asked]
    
    def remove_slot(self,slot_given) :
        if slot_given in self.slots :
            self.slots.remove(slot_given)
    
    # This function is called when the bot has made a request but no slots have been provided, hence we look at the description of the action to figure out what the request is
    def perform_random_action(self,bot_action) :
        
        user_action = None
        actual_actor = None
        actual_action = None
        accept_message = str()
        reject_message = str()
        values_to_give = dict()
        pattern_to_give = list()
        
            
        if bot_action.get_description() == "API_CALL" :
            
            actual_actor = "API"
            actual_action = "api_response"
            
            accept_key = "cancel_transaction_success"
            accept_message = self.templates[accept_key][0]
            
            reject_key = "cancel_transaction_failed"
            reject_message = self.templates[reject_key][0]
            
            #accept_message = "api_response:cancel_transaction_api, api_result:success"
            #reject_message = "api_response:cancel_transaction_api, api_result:failed"
                
            
        elif bot_action.get_description() == "CHANGE_TRANSACTION_ID" :
                
            
            
            n_account = random.sample(self.user_accounts,1)[0]
            n_partner_name = random.sample(self.partner_names,1)[0]
            
            new_transaction_id = "{}-{}".format(n_account,n_partner_name)
            while new_transaction_id == self.user["transaction_id"] :
                n_account = random.sample(self.user_accounts,1)[0]
                n_partner_name = random.sample(self.partner_names,1)[0]
                
                new_transaction_id = "{}-{}".format(n_account,n_partner_name)
                
            self.user["transaction_id"] = new_transaction_id
            
            if self.state_track["CHANGE_TRANSACTION_ID"] > 2 :
                self.override = True
                new_transaction_id = random.sample(self.user["transaction_ids"],1)[0]
                self.user["transaction_id"] = new_transaction_id
            
            actual_actor = "User"
            actual_action = "inform"
            
            accept_key = "change_transaction_id_accept"
            accept_message = self.templates[accept_key][0]
            
            
            reject_key = "change_transaction_id_reject"
            reject_message = self.templates[reject_key][0]
            
            #accept_message = "accept"
            #reject_message = "reject"
            
            if self.turn_compression :
                
                accept_key = "change_transaction_id_accept_turn_compression"
                accept_message = self.templates[accept_key][0]
                accept_message = accept_message.format(new_transaction_id)
                
                #accept_message = "accept use {}".format(new_transaction_id)
                pattern_to_give.append("turn_compression")
                
            values_to_give = {"transaction_id" : new_transaction_id}
            
            self.state_track["CHANGE_TRANSACTION_ID"] += 1
            
                
        elif bot_action.get_description() == "CHANGE_PARTNER_NAME" :
            
            
            
            new_partner_name = random.sample(self.partner_names,1)[0]
            
            while new_partner_name == self.user["partner_name"] :
                new_partner_name = random.sample(self.partner_names,1)[0]
            
            self.user["partner_name"] = new_partner_name
            
            if self.state_track["CHANGE_PARTNER_NAME"] > 2 :
                self.override = True
                new_partner_name = random.sample(self.partner_name_with_transaction_id,1)[0]
                
                self.user["partner_name"] = new_partner_name
                #print("partner name chosen : {}".format(self.user["partner_name"]))
                
            actual_actor = "User"
            actual_action = "inform"
            
            accept_key = "change_partner_name_accept"
            accept_message = self.templates[accept_key][0]
            
            reject_key = "change_partner_name_reject"
            reject_message = self.templates[reject_key][0]
            
            #accept_message = "accept"
            #reject_message = "reject"
            
            if self.turn_compression :
                accept_key = "change_partner_name_accept_turn_compression"
                accept_message = self.templates[accept_key][0]
                accept_message = accept_message.format(new_partner_name)
                
                #accept_message = "accept use {}".format(new_partner_name)
                pattern_to_give.append("turn_compression")
            
            values_to_give = {"partner_name" : new_partner_name}
            
            self.state_track["CHANGE_PARTNER_NAME"] += 1
            
        
        elif bot_action.get_description() == "CONFIRM_CANCEL_TRANSACTION" :
            actual_actor = "User"
            actual_action = None
            
            accept_key = "confirm_cancel_transaction_accept"
            accept_message = self.templates[accept_key][0]
            
            reject_key ="confirm_cancel_transaction_reject"
            reject_message = self.templates[reject_key][0]
            
        else :
            
            actual_actor = "User"
            actual_action = "inform"
            
            accept_key = "general_accept"
            accept_message = self.templates[accept_key][0]
            
            reject_key = "general_reject"
            reject_message = self.templates[reject_key][0]
            
            #accept_message = "accept"
            #reject_message = "reject"
        
        toss = random.randint(0,100)
        if toss > 10 or self.override :
            self.override = False
            user_action = Action(actor=actual_actor,
                                 action=actual_action,
                                 slots=None,
                                 values=values_to_give,
                                 message=accept_message,
                                 description="ACCEPT_REQUEST",
                                 templates=self.templates,
                                 pattern_marker=pattern_to_give)
        else :
            
            user_action = Action(actor=actual_actor,
                                 action=actual_action,
                                slots=None,
                                values=values_to_give,
                                message=reject_message,
                                 description="REJECT_REQUEST",
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
                    
                    if "transaction_id" in bot_action.get_slots() :
                        toss = random.randint(0,100)
                        
                        if toss > 10 :
                            user_value = self.get_value("transaction_id")
                            user_action = Action(actor="User",
                                                 action="inform",
                                                 slots=["transaction_id"],
                                                 values={"transaction_id" : user_value},
                                                 message="providing value for transaction id ",
                                                 templates=self.templates)
                        else :
                            
                            user_action = Action(actor="User",
                                                 action="transaction_id_not_know",
                                                 slots=None,
                                                 values={"partner_name" : self.user["partner_name"]},
                                                 message="Providing value for {}".format(bot_action.get_slots()[0]),
                                                 description="TRANSACTION_ID_NOT_KNOW",
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
                                                 templates=self.templates,
                                                 pattern_marker=["another_slot"])
                            
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
                    while number_of_slots % 2 != rem :
                        number_of_slots = random.randint(0,len(self.slots))
                        
                    slots_to_inform = random.sample(self.slots,number_of_slots)
                    all_slots = ["intent","domain_description"] + self.sort_my_slots(slots_to_inform)
                    values_to_inform = dict()
                    
                    for slot in all_slots :
                        values_to_inform[slot] = self.user[slot]
                        
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
            
        if bot_action.get_description() == "API_INITIAL_SLOT_CHECK" :
            flag = False
            error_message = list()
            order_of_slots = list()
            if "transaction_id" in bot_action.get_slots() :
                
                if self.user["transaction_id"] not in self.user["transaction_ids"] :
                    
                    self.priority_states.append("change_transaction_id")
                    order_of_slots.append("change_transaction_id")
                    #slot_message = ",".join(self.user["user_accounts"])
                    #bot_message = "It seems that you have not entered a valid account, you available accounts are {}, would you like change the source account ?".format(slot_message)
                    key = "change_transaction_id"
                    
                    bot_message = self.templates[key][0]
                    self.priority_actions["change_transaction_id"] = Action(actor="Bot",
                                                                    action="request",
                                                                    slots=None,
                                                                    values=None,
                                                                    #message="I am sorry, the transaction you entered is incorrect, would you like to change transaction id ?",
                                                                    message=bot_message,
                                                                    description="CHANGE_TRANSACTION_ID",
                                                                    templates=self.templates)
                    
                elif self.user["transaction_id"] in self.blockable_transactions :
                    self.priority_states.append("change_transaction_id")
                    order_of_slots.append("change_transaction_id")
                    
                    key = "end_call_transaction_not_blockable"
                    
                    bot_message = self.templates[key][0]
                    self.priority_actions["end_call"] = Action(actor="Bot",
                                                                            action="end_call",
                                                                            slots=None,
                                                                            values=None,
                                                                            #message="I am sorry, but that transaction can't be blocked now, do you want to block another one ?",
                                                               message=bot_message,
                                                                            description="CHANGE_TRANSACTION_ID",
                                                                            templates=self.templates)
                
            if self.priority_states :
                
                order_message = ','.join(order_of_slots)
                key = "check_initial_slot_failed"
                user_message = self.templates[key][0]
                user_message = user_message.format(order_message)
                user_action = Action(actor="API",
                                     action=None,
                                     slots=self.priority_states,
                                     values=self.priority_actions,
                                     #message="api_response:initial_slot_check_api, api_result:failed, message:'{}'".format(order_message),
                                     message=user_message,
                                     templates=self.templates)
            else :
                
                key = "check_initial_slot_success"
                user_message = self.templates[key][0]
                
                user_action = Action(actor="API",
                                     action="api_response",
                                     slots=bot_action.get_slots(),
                                     values=None,
                                     #message="api_response:initial_slot_check_api, api_result:success",
                                     message=user_message,
                                     templates=self.templates)
                
        elif bot_action.get_description() == "API_PARTNER_NAME_CHECK" :
            
            #print("checking account")
            if self.user["partner_name"] in self.user["partner_names"] :
                
                #print("list of partner names : {}".format(self.partner_name_with_transaction_id))
                if self.user["partner_name"] in self.partner_name_with_transaction_id :
                    
                    
                    key = "check_partner_name_success"
                    user_message = self.templates[key][0]
                    
                    transaction_id = self.transaction_dictionary[self.user["partner_name"]]
                    user_action = Action(actor="API",
                                         action="api_response",
                                         slots=None,
                                         values={"transaction_id" : transaction_id},
                                         #message="api_response:check_partner_name_api, api_result:success",
                                         message=user_message,
                                         templates=self.templates)
                else :
                    
                    slot_message = ','.join(self.partner_name_with_transaction_id)
                    
                    key = "check_partner_name_failed_partner_with_no_transaction_id"
                    api_message = self.templates[key][0]
                    api_message = api_message.format(slot_message)
                    
                    #api_message = "api_response:check_partner_name_api, api_result:failed, message:'avalilable list of partners are : {}'".format(slot_message)
                    user_action = Action(actor="API",
                                         action="api_response",
                                         slots=None,
                                         values={"partner_names" : self.partner_name_with_transaction_id},
                                         message=api_message,
                                         description="NO_TRANSACTION_FOR_USER_ACCOUNT",
                                         templates=self.templates)
                    
            else :
                
                slot_message = ','.join(self.user["partner_names"])
                
                key = "check_partner_name_failed_invalid_partner_name"
                api_message = self.templates[key][0]
                api_message = api_message.format(slot_message)
                
                #api_message = "api_response:check_partner_name_api, api_result:failed, message:'available list of partner names are : {}'".format(slot_message)
                user_action = Action(actor="API",
                                     action="api_response",
                                     slots=None,
                                     values={"partner_names" : self.user["partner_names"]},
                                     message=api_message,
                                     description="NO_USER_ACCOUNT",
                                     templates=self.templates)
                
        elif bot_action.get_description() == "API_TRANSACTION_ID_CHECK" :
            
            
            if self.user["transaction_id"] in self.user["transaction_ids"] :
                
                
                key = "check_transaction_id_success"
                user_message = self.templates[key][0]
                
                user_action = Action(actor="API",
                                     action="api_response",
                                     slots=None,
                                     values=None,
                                     #message="api_response:check_transaction_id_check_api, api_result:success",
                                     message=user_message,
                                     templates=self.templates)
            else :
                
                
                key = "check_transaction_id_failed"
                user_message = self.templates[key][0]
                
                user_action = Action(actor="API",
                                     action="api_response",
                                     slots=None,
                                     values=None,
                                     #message="api_response:cehck_transaction_id_api, api_result:failed",
                                     message=user_message,
                                     templates=self.templates)
                
        elif bot_action.get_description() == "API_TRANSACTION_BLOCKABLE_CHECK" :
            
            if self.user["transaction_id"] in self.blockable_transactions :
                
                key = "check_transaction_blockable_success"
                user_message = self.templates[key][0]
                
                user_action = Action(actor="API",
                                     action="api_response",
                                     slots=None,
                                     values=None,
                                     #message="api_response:transaction_blockable_api, api_result:success",
                                     message=user_message,
                                     templates=self.templates)
                
            else :
                
                key = "check_transaction_blockable_failed"
                user_message = self.templates[key][0]
                
                user_action = Action(actor="API",
                                     action="api_response",
                                     slots=None,
                                     values=None,
                                     #message="api_response:transaction_blockable_api, api_result:failed",
                                     message=user_message,
                                     templates=self.templates)


            
        else :
            
            user_action = self.perform_random_action(bot_action)
        
        
        return user_action            