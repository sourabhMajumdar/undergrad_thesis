import random
import sys
sys.path.append("..")
from utils import Action
class Account_bot(object) :
    
    def __init__(self,templates=None) :
        
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
        self.templates = templates
        
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
                               message="accounts:{}".format(self.user_values["name"]),
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
                                description="SELECT_ACCOUNT",
                                templates=self.templates)
        else : 
            next_state = "list_accounts"
            bot_action = Action(actor="API",
                               action="request_accounts",
                               slots=["name"],
                               values=None,
                               message="accounts:{}".format(self.user_values["name"]),
                               templates=self.templates)
            
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
                               description="API_CALL",
                               templates=self.templates)
        else :
            next_state = "select_account"
            bot_action = Action(actor="Bot",
                               action="request",
                               slots=None,
                               values=None,
                               message="Please select an account",
                               templates=self.templates)
        
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
                               message=bot_message,
                               templates=self.templates)
        else :
            next_state = "end_call"
            bot_action = Action(actor="Bot",
                               action="end_call",
                               slots=None,
                               values=None,
                               message="error in processing request !!",
                               templates=self.templates)
        
        return next_state , bot_action
    
    def end_call_state(self,user_action) :
        print("Reached end of transaction")
        return
