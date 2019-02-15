import random
import sys
sys.path.append("..")
from utils import Action
class Block_card_bot(object) :
    
    def __init__(self,
                 templates=None,
                 turn_compression=False,
                 re_order=False,
                 audit_more=False) :
        
        self.last_slot = None
        self.list_of_slots = ["user_account"]
        self.slots_to_ask = ["card_id"]
        self.user_values = dict()
        
        self.states = {"initial" : self.initial_state ,
                       "check_initial" : self.check_initial_state,
                       "card_id" : self.card_id_state,
                       "check_card_id" : self.check_card_id_state,
                       "change_card_id" : self.change_card_id_state,
                       "request_account" : self.request_account_state,
                       "check_account" : self.check_account_state,
                       "change_account" : self.change_account_state,
                       "select_card" : self.select_card_state,
                       "check_card_name" : self.check_card_state,
                       "change_card_name" : self.change_card_state,
                       "confirmation_state" : self.confirmation_state,
                       "api_call" : self.api_call_state,
                       "end_call" : self.end_call_state}
        
        self.priority_states = list()
        self.priority_actions = dict()
        
        self.turn_compression = turn_compression
        self.re_order = re_order
        self.audit_more = audit_more
        
        self.templates = templates
        
        self.current_state = self.initial_state
    
    def sort_my_slots(self,slots_given) :
        slots_sorted = list()
        
        if "card_id" in slots_given :
            slots_sorted.append("card_id")
            slots_given.remove("card_id")
        
        
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
                    
                    
    # Below is the main speak function used by the Bot
                
    def speak(self,user_action) :
        
        if user_action == None :
            
            print("user_action received is None")
        
        next_state , bot_action = self.current_state(user_action)
        #print("next_state is {}".format(next_state))
        self.current_state = self.states[next_state]
        
        return bot_action
        
    # meet the initial state, here the user may provide one or more than one values
    # request intent if not given already
    
    
    
    # Below is the initial state, it is the first state of the bot and it determines what state to go next
    def initial_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if user_action.get_slots() :
            
            if "intent" in user_action.get_slots() and len(user_action.get_slots()) > 2 :
                
                next_state = "check_initial"
                slots_given = user_action.get_slots()[1:]
                '''slot_message = "api_call:initial_slot_check_api,"'''
                key = "initial_slot_check"
                
                slot_message = self.templates[key][0]
                
                for slot in slots_given :
                    if slot == "domain_description" :
                        continue
                    else :
                        slot_message += " {}:{},".format(slot,self.user_values[slot])
                
                bot_action = Action(actor="Bot",
                                    action="api_call",
                                    slots=user_action.get_slots(),
                                    values=None,
                                    message=slot_message[:-1],
                                    description="API_INITIAL_SLOT_CHECK",
                                    templates=self.templates)
                
            else :
                
                next_state = "card_id"
                bot_action = Action(actor="Bot",
                                   action="request",
                                   slots=["card_id"],
                                   values=None,
                                   message="requesting user for card id",
                                   description="REQUEST_CARD_ID",
                                   templates=self.templates)
        else :
            
            next_state = "initial"
            bot_action = Action(actor="Bot",
                               action="request",
                               slots=["intent"],
                               values=None,
                               message="requesting the intent from the user",
                               templates=self.templates)
        return next_state , bot_action
    
    def check_initial_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "api_result:success" in user_action.get_message() :
                
            next_state = "confirmation_state"
            
            key = "confirm_block_card"
            
            bot_message = self.templates[key][0]
            
            bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=None,
                                values=None,
                                message=bot_message,
                                description="API_CALL",
                                templates=self.templates)
                
        else :
            
            self.priority_states = user_action.get_slots()
            self.priority_actions = user_action.get_values()
            
            next_state = self.priority_states[0]
            bot_action = self.priority_actions[next_state]
            
            self.priority_states.remove(next_state)
            
        return next_state , bot_action
    
    
    
    
    
    # Below is the card id state, assuming user has not provided the card id, we have requested for one and we see, what progress 
    # has been made till now
    
    def card_id_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if user_action.get_description() == "CARD_ID_NOT_KNOW" :
            
            next_state = "request_account"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=["user_account"],
                                values=None,
                                message="requesting for user account",
                                description="REQUEST_ACCOUNTS",
                                templates=self.templates)
            
        else :
            
            if "card_id" in user_action.get_slots() :
                
                next_state = "check_card_id"
                
                key = "check_card_id"
                bot_message = self.templates[key][0]
                bot_message = bot_message.format(self.user_values["card_id"])
                
                bot_action = Action(actor="Bot",
                                    action="api_call",
                                    slots=["card_id"],
                                    values={"card_id" : self.user_values["card_id"]},
                                    #message="api_call:check_card_id_api, card_id:{}".format(self.user_values["card_id"]),
                                    message=bot_message,
                                    description="API_CARD_ID_CHECK",
                                    templates=self.templates)
                
            else :
                
                if user_action.get_description() == "ANOTHER_SLOT_VALUE" :
                    slot_given = user_action.get_slots()[0]
                    appropriate_state = self.states[slot_given]
                    
                    next_state, bot_action = appropriate_state(user_action)
                else :
                        
                    next_state = "card_id"
                    bot_action = Action(actor="Bot",
                                        action="request",
                                        slots=["card_id"],
                                        values=None,
                                        message="requesting for slot card id",
                                        templates=self.templates)
                
        return next_state, bot_action
    
    def check_card_id_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "api_result:success" in user_action.get_message() :
            
            next_state = "confirmation_state"
            
            key = "confirm_block_card"
            
            bot_message = self.templates[key][0]
            
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=None,
                                values=None,
                                message=bot_message,
                                description="CONFIRM_BLOCK_CARD",
                                slot_concerned="api",
                                templates=self.templates)
        else :
            
            next_state = "change_card_id"
            
            key = "change_card_id"
            bot_message = self.templates[key][0]
            
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=None,
                                values=None,
                                #message="It seems that the card id you gave is incorrect, would you like to change ?",
                                message=bot_message,
                                description="CHANGE_CARD_ID",
                                templates=self.templates)
            
        return next_state, bot_action
    
    
    def change_card_id_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "accept" in user_action.get_message() :
            
            #self.slots_to_ask.insert(0,"card_id")
            
            if self.turn_compression :
                next_state = "check_card_id"
                
                key = "check_card_id"
                bot_message = self.templates[key][0]
                bot_message = bot_message.format(self.user_values["card_id"])
                
                bot_action = Action(actor="Bot",
                                    action="api_call",
                                    slots=["card_id"],
                                    values={"card_id" : self.user_values["card_id"]},
                                    #message="api_call:check_card_id_api, card_id:{}".format(self.user_values["card_id"]),
                                    message=bot_message,
                                    description="API_CARD_ID_CHECK",
                                    templates=self.templates)
                
            else :
                next_state = "card_id"
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=["card_id"],
                                    values=None,
                                    message="Requesting for card_id",
                                    description="REQUEST_CARD_ID",
                                    templates=self.templates)
        else :
            
            next_state = "end_call"
            
            key = "end_call_denied_change_card_id"
            
            bot_message = self.templates[key][0]
            
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                #message="you denied to change card_id",
                                message=bot_message,
                                templates=self.templates)
            
        return next_state, bot_action
    
    # below is the description of all the states in the user_account
            
    def request_account_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "user_account" in user_action.get_slots() :
            
            next_state = "check_account"
            
            key = "check_account"
            bot_message = self.templates[key][0]
            bot_message = bot_message.format(self.user_values["user_account"])
            
            bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=["user_account"],
                                values={"user_account" : self.user_values["user_account"]},
                                #message="api_call:check_account_api, user_account:{}".format(self.user_values["user_account"]),
                                message=bot_message,
                                description="API_ACCOUNT_CHECK",
                                templates=self.templates)
        else :
            
            if user_action.get_description() == "ANOTHER_SLOT_VALUE" :
                slot_given = user_action.get_slots()[0]
                appropriate_state = self.states[slot_given]
                
                next_state, bot_action = appropriate_state(user_action)
            
            else :
                
                next_state = "request_account"
                bot_action = Action(user="Bot",
                                    action="request",
                                    slots=["user_account"],
                                    values=None,
                                    message="requesting for user account ",
                                    templates=self.templates)
            
        return next_state, bot_action
    
    def check_account_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "api_result:success" in user_action.get_message() :
            
            next_state = "select_card"
            card_list = ','.join(self.user_values["card_names"])
            bot_action = Action(actor="Bot",
                                action="select_from",
                                slots=["card_list"],
                                values={"card_names" : self.user_values["card_names"],
                                        "card_list" : card_list},
                                message="requesting to select a card",
                                description="SELECT_CARD",
                                templates=self.templates)
            
        else :
            if user_action.get_description() == "NO_CARD_FOR_USER_ACCOUNT" :
                
                next_state = "change_account"
                
                key = "change_account_no_card_associated"
                bot_message = self.templates[key][0]
                
                slot_message = ','.join(user_action.get_slots())
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=None,
                                    values=None,
                                    #message="you have no cards asscociated with this user account, available list of accounts : {}".format(slot_message),
                                    message=bot_message,
                                    description="CHANGE_ACCOUNT",
                                    templates=self.templates)
            else :
                next_state = "change_account"
                
                slot_message = ','.join(self.user_values["user_accounts"])
                
                key = "change_account_invalid_account"
                bot_message = self.templates[key][0]
                bot_message = bot_message.format(slot_message)
                
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=None,
                                    values=None,
                                    #message="User account given is invalid, available list of accounts : {}".format(slot_message),
                                    message=bot_message,
                                    description="CHANGE_ACCOUNT",
                                    templates=self.templates)
            
        return next_state, bot_action
    
    def change_account_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if user_action.get_description() == "ACCEPT_REQUEST" :
            
            self.slots_to_ask.insert(0,"user_account")
            
            if self.turn_compression :
                
                next_state = "check_account"
                
                key = "check_account"
                bot_message = self.templates[key][0]
                bot_message = bot_message.format(self.user_values["user_account"])
                
                bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=["user_account"],
                                values={"user_account" : self.user_values["user_account"]},
                                #message="api_call:check_account_api, user_account:{}".format(self.user_values["user_account"]),
                                message=bot_message,
                                description="API_ACCOUNT_CHECK",
                                templates=self.templates)
            else :
                next_state = "request_account"
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=["user_account"],
                                    values=None,
                                    message="requesting for user account",
                                    templates=self.templates)
            
        else :
            next_state = "end_call"
            
            key = "end_call_denied_change_account"
            bot_message = self.templates[key][0]
            
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                #message="you denied to change the account",
                                message=bot_message,
                                templates=self.templates)
            
        return next_state, bot_action
    
    
    
    # below are all the states that appear after we have determined the account
    
    def select_card_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "card_name" in user_action.get_slots() :
            
            next_state = "check_card_name"
            
            key = "check_card_name"
            bot_message = self.templates[key][0]
            bot_message = bot_message.format(self.user_values["card_name"])
            
            bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=None,
                                values=None,
                                #message="api_call:check_card_name_api, card_name:{}".format(self.user_values["card_name"]),
                                message=bot_message,
                                description="API_CARD_NAME_CHECK",
                                templates=self.templates)
            
        else :
            
            if user_action.get_description() == "ANOTHER_SLOT_VALUE" :
                slot_given = user_action.get_slots()[0]
                appropriate_state = self.states[slot_given]
                
                next_state, bot_action = appropriate_state(user_action)
            else :
                
                next_state = "card_name"
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=None,
                                    values=None,
                                    message="requesting for card name",
                                    templates=self.templates)
            
        return next_state, bot_action
    
    def check_card_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "api_result:success" in user_action.get_message() :
            next_state = "api_call"
            
            next_state = "confirmation_state"
            key = "confirm_block_card"
            
            bot_message = self.templates[key][0]
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=None,
                                values=None,
                                message=bot_message,
                                description="CONFIRM_BLOCK_CARD",
                                slot_concerned="api",
                                templates=self.templates)
        else :
            
            slot_message = ','.join(self.user_values["card_names"])
            next_state = "change_card_name"
            key = "change_card_name"
            bot_message = self.templates[key][0]
            bot_message = bot_message.format(slot_message)
            
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=None,
                                values=None,
                                #message="The card you provided is no correct, avalilable list of cards are : {}".format(self.user_values["card_names"]),
                                message=bot_message,
                                description="CHANGE_CARD_NAME",
                                templates=self.templates)
        
        return next_state, bot_action
    
    def change_card_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if user_action.get_description() == "ACCEPT_REQUEST" :
            
            self.slots_to_ask.insert(0,"card_name")
            
            if self.turn_compression :
                next_state = "check_card_name"
                
                key = "check_card_name"
                bot_message = self.templates[key][0]
                bot_message = bot_message.format(self.user_values["card_name"])
                
                bot_action = Action(actor="Bot",
                                    action="api_call",
                                    slots=None,
                                    values=None,
                                    #message="api_call:check_card_name_api, card_name:{}".format(self.user_values["card_name"]),
                                    message=bot_message,
                                    description="API_CARD_NAME_CHECK",
                                    templates=self.templates)
            else :
                next_state = "select_card"
                bot_action = Action(actor="Bot",
                                    action="select_from",
                                    slots=['card_list'],
                                    values=None,
                                    message="request to select a card",
                                    description="SELECT_CARD",
                                    templates=self.templates)
            
        else :
            
            next_state = "end_call"
            
            key = "end_call_denied_change_card_name"
            bot_message = self.templates[key][0]
            
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                #message="you denied to change the card",
                                message=bot_message,
                                templates=self.templates)
            
        return next_state, bot_action
    
    def confirmation_state(self,user_action) :
        
        if user_action.get_description() == "ACCEPT_REQUEST" :
            next_state = "api_call"
            key = "block_card_call"
            bot_message = self.templates[key][0]
            bot_message = bot_message.format(self.user_values["card_id"])
            
            bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=None,
                                values=None,
                                ##message="api_call:block_card_api, card_id:{}".format(self.user_values["card_id"]),
                                message=bot_message,
                                description="API_CALL",
                                templates=self.templates)
        else :
            
            next_state = "api_call"
            key = "end_call_denied_confirm_block_card"
            bot_message = self.templates[key][0]
            
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                #message="User refused to confirm transaction",
                                message=bot_message,
                                slot_concerned="api",
                                templates=self.templates)
            
        return next_state, bot_action
            
    def api_call_state(self,user_action) :
        
        if "api_result:success" in user_action.get_message() :
            
            key = "block_card_call_success"
            bot_message = self.templates[key][0]
            
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="blocked card successfully",
                                templates=self.templates)
        else :
            
            key = "block_card_call_failed"
            bot_message = self.templates[key][0]
            
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="error in processing blocking card, please try again",
                                templates=self.templates)
            
        next_state = "end_call"
        return next_state, bot_action
    
    def end_call_state(self,user_action) :
        
        print("Reached the end of transaction")
        return None, None