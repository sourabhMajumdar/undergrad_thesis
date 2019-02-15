import random
import sys
sys.path.append("..")
from utils import Action
class Cancel_transaction_bot(object) :
    
    def __init__(self,
                 templates=None,
                 turn_compression=False,
                 re_order=False,
                 audit_more=False) :
        
        self.last_slot = None
        self.list_of_slots = ["user_account"]
        self.slots_to_ask = ["transaction_id"]
        self.user_values = dict()
        
        self.states = {"initial" : self.initial_state ,
                       "check_initial" : self.check_initial_state,
                       "transaction_id" : self.transaction_id_state,
                       "check_transaction_id" : self.check_transaction_id_state,
                       "change_transaction_id" : self.change_transaction_id_state,
                       "request_partner_name" : self.request_partner_name_state,
                       "check_partner_name" : self.check_partner_name_state,
                       "change_partner_name" : self.change_partner_name_state,
                       "check_transaction_blockable" : self.check_transaction_blockable_state,
                       "confirmation_state" : self.confirmation_state,
                       "api_call" : self.api_call_state,
                       "end_call" : self.end_call_state}
        
        self.priority_states = list()
        self.priority_actions = dict()
        self.templates = templates
        
        self.turn_compression = turn_compression
        self.re_order = re_order
        self.audit_more = audit_more
        
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
                slot_message = "api_call:initial_slot_check,"
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
                
                next_state = "transaction_id"
                bot_action = Action(actor="Bot",
                                   action="request",
                                   slots=["transaction_id"],
                                   values=None,
                                   message="requesting user for transaction id",
                                   description="REQUEST_TRANSACTION_ID",
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
                
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=None,
                                values=None,
                                message="You are about to cancel a transastion with transaction id : {}".format(self.user_values["transaction_id"]),
                                description=None,
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
    
    def transaction_id_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if user_action.get_description() == "TRANSACTION_ID_NOT_KNOW" :
            
            next_state = "request_partner_name"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=["partner_name"],
                                values=None,
                                message="requesting for partner name",
                                description="REQUEST_PARTNER_NAME",
                                templates=self.templates)
            
        else :
            
            if "transaction_id" in user_action.get_slots() :
                
                next_state = "check_transaction_id"
                bot_action = Action(actor="Bot",
                                    action="api_call",
                                    slots=["transaction_id"],
                                    values={"transaction_id" : self.user_values["transaction_id"]},
                                    message="api_call:check_transaction_id_api, transaction_id:{}".format(self.user_values["transaction_id"]),
                                    description="API_TRANSACTION_ID_CHECK",
                                    templates=self.templates)
                
            else :
                
                if user_action.get_description() == "ANOTHER_SLOT_VALUE" :
                    slot_given = user_action.get_slots()[0]
                    appropriate_state = self.states[slot_given]
                    
                    next_state, bot_action = appropriate_state(user_action)
                    
                else :
                    
                    next_state = "transaction_id"
                    bot_action = Action(actor="Bot",
                                        action="request",
                                        slots=["transaction_id"],
                                        values=None,
                                        message="requesting for slot transaction id",
                                        templates=self.templates)
                
        return next_state, bot_action
    
    def check_transaction_id_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "api_result:success" in user_action.get_message() :
            
            next_state = "check_transaction_blockable"
            bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=None,
                                values=None,
                                message="api_call:transaction_blockable_api, transaction_id:{}".format(self.user_values["transaction_id"]),
                                description="API_TRANSACTION_BLOCKABLE_CHECK",
                                templates=self.templates)
        else :
            
            next_state = "change_transaction_id"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=None,
                                values=None,
                                message="It seems that the transaction id you gave is incorrect, would you like to change ?",
                                description="CHANGE_TRANSACTION_ID",
                                templates=self.templates)
            
        return next_state, bot_action
    
    
    def change_transaction_id_state(self,user_action) :
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "accept" in user_action.get_message() :
            
            self.slots_to_ask.insert(0,"transaction_id")
            
            if self.turn_compression :
                next_state = "check_transaction_id"
                bot_action = Action(actor="Bot",
                                    action="api_call",
                                    slots=["transaction_id"],
                                    values={"transaction_id" : self.user_values["transaction_id"]},
                                    message="api_call:check_transaction_id_api, transaction_id:{}".format(self.user_values["transaction_id"]),
                                    description="API_TRANSACTION_ID_CHECK",
                                    templates=self.templates)
                
            else :
                
                next_state = "transaction_id"
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=["transaction_id"],
                                    values=None,
                                    message="Requesting for transaction_id",
                                    description="REQUEST_TRANSACTION_ID",
                                    templates=self.templates)
        else :
            
            next_state = "end_call"
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="you denied to change transaction_id",
                                templates=self.templates)
            
        return next_state, bot_action
    
    # below is the description of all the states in the user_account
            
    def request_partner_name_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "partner_name" in user_action.get_slots() :
            
            next_state = "check_partner_name"
            bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=["partner_name"],
                                values={"partner_name" : self.user_values["partner_name"]},
                                message="api_call:check_partner_name_api, partner_name:{}".format(self.user_values["partner_name"]),
                                description="API_PARTNER_NAME_CHECK",
                                templates=self.templates)
        else :
            
            if user_action.get_description() == "ANOTHER_SLOT_VALUE" :
                slot_given = user_action.get_slots()[0]
                appropriate_state = self.states[slot_given]
                
                next_state, bot_action = appropriate_state(user_action)
            else :
                
                next_state = "request_partner_name"
                bot_action = Action(user="Bot",
                                    action="request",
                                    slots=["partner_name"],
                                    values=None,
                                    message="requesting for partner name",
                                    templates=self.templates)
            
        return next_state, bot_action
    
    def check_partner_name_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "api_result:success" in user_action.get_message() :
            
            next_state = "check_transaction_blockable"
            bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=None,
                                values=None,
                                message="api_call:transaction_blockable_api, transaction_id:{}".format(self.user_values["transaction_id"]),
                                description="API_TRANSACTION_BLOCKABLE",
                                templates=self.templates)
            
            
        else :
            if user_action.get_description() == "NO_TRANSACTION_FOR_PARTNER_NAME" :
                
                next_state = "change_partner_name"
                slot_message = ','.join(user_action.get_slots())
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=None,
                                    values=None,
                                    message="you have no transaction asscociated with this user account, available list of partner with transaction : {}".format(slot_message),
                                    description="CHANGE_PARTNER_NAME",
                                    templates=self.templates)
            else :
                next_state = "change_partner_name"
                slot_message = ','.join(self.user_values["partner_names"])
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=None,
                                    values=None,
                                    message="partner name given is invalid, available list of accounts : {}".format(slot_message),
                                    description="CHANGE_PARTNER_NAME",
                                    templates=self.templates)
            
        return next_state, bot_action
    
    def change_partner_name_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "accept" in user_action.get_message() :
            
            self.slots_to_ask.insert(0,"partner_name")
            
            if self.turn_compression :
                next_state = "check_partner_name"
                bot_action = Action(actor="Bot",
                                    action="api_call",
                                    slots=["partner_name"],
                                    values={"partner_name" : self.user_values["partner_name"]},
                                    message="api_call:check_partner_name_api, partner_name:{}".format(self.user_values["partner_name"]),
                                    description="API_PARTNER_NAME_CHECK",
                                    templates=self.templates)
                
            else :
                next_state = "request_partner_name"
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=["partner_name"],
                                    values=None,
                                    message="requesting for partner name",
                                    templates=self.templates)
            
        else :
            next_state = "end_call"
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="you denied to change the account",
                                templates=self.templates)
            
        return next_state, bot_action
    
    def check_transaction_blockable_state(self,user_action) :
        
        if "api_result:success" in user_action.get_message() :
            next_state = "confirmation_state"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=None,
                                values=None,
                                message="You are about to cancel transaction with transaction id : {}".format(self.user_values["transaction_id"]),
                                description=None,
                                templates=self.templates)
        else :
            
            next_state = "change_transaction_id"
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="I am sorry but that transaction is not blockable",
                                templates=self.templates)
            
        return next_state, bot_action
    
    def confirmation_state(self,user_action) :
        
        if user_action.get_message() == "accept" :
            next_state = "api_call"
            bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=None,
                                values=None,
                                message="api_call:cancel_transaction_api, transaction_id:{}".format(self.user_values["transaction_id"]),
                                description="API_CALL",
                                templates=self.templates)
        else :
            next_state = "end_call"
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="You denied to confirm cancellation ",
                                templates=self.templates)
            
        return next_state, bot_action
    
    def api_call_state(self,user_action) :
        
        if "api_result:success" in user_action.get_message() :
            
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="cancelled transaction successfully",
                                templates=self.templates)
        else :
            
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="error in processing cancelling, please try again",
                                templates=self.templates)
            
        next_state = "end_call"
        return next_state, bot_action
    
    def end_call_state(self,user_action) :
        
        print("Reached the end of transaction")
        return None, None