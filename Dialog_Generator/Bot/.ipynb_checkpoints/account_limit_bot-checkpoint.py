import random
import sys
sys.path.append("..")
from utils import Action

class Account_limit_bot(object) :
    def __init__(self,
                 templates=None,
                 turn_compression=False,
                 re_order=False,
                 audit_more=False) :
        
        self.last_slot = None
        self.list_of_slots = ["user_account"]
        self.slots_to_ask = ["user_account"]
        self.user_values = dict()
        
        self.states = {"initial" : self.initial_state ,
                       "check_initial" : self.check_initial_state,
                       "list_accounts" : self.list_accounts_state,
                       "user_account" : self.select_account_state,
                       "check_account" : self.check_account_state,
                       "change_account" : self.change_account_state,
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
        #print("next_state is {}".format(next_state))
        self.current_state = self.states[next_state]
        
        return bot_action
        
    # meet the initial state, here the user may provide one or more than one values
    # request intent if not given already
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
                
                next_state = "list_accounts"
                bot_action = Action(actor="Bot",
                                   action="api_call",
                                   slots=["name"],
                                   values=None,
                                   message="api_call:request_account_api",
                                   description="REQUEST_ACCOUNTS",
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
        
        if "api_result:success" in user_action.get_message() :
            if not self.slots_to_ask :
                next_state = "api_call"
                api_value = self.user_values["user_account"]
                api_message = "api_call:check_balance_api, user_account:{}".format(self.user_values["user_account"])
                bot_action = Action(actor="Bot",
                                   action="api_call",
                                   slots=None,
                                   values={"api_call" : api_value},
                                   message=api_message,
                                   description="API_CALL",
                                   templates=self.templates)
            else :
                if self.re_order :
                    next_state = random.sample(self.slots_to_ask,1)[0]
                else :
                    next_state = self.slots_to_ask[0]
                
        else :
            self.priority_states = user_action.get_slots()
            self.priority_actions = user_action.get_values()
            
            next_state = self.priority_states[0]
            bot_action = self.priority_actions[next_state]
            
            self.priority_states.remove(next_state)
            
        return next_state , bot_action
    
    def list_accounts_state(self,user_action) :
        
        if user_action.get_description() == "LIST_OF_SLOTS" :
            next_state = "user_account"
            slot_message = ",".join(user_action.get_slots())
            bot_message = "You have the following accounts : {} , which one do you wish ?".format(slot_message)
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=["user_account"],
                                values=None,
                                message=bot_message,
                                description="SELECT_ACCOUNT",
                                templates=self.templates)
        else : 
            next_state = "list_accounts"
            bot_action = Action(actor="Bot",
                               action="api_call",
                               slots=["name"],
                               values=None,
                               message="api_call:request_accounts_api",
                               description="REQUEST_ACCOUNTS",
                               templates=self.templates)
            
        return next_state , bot_action
        
    def select_account_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "user_account" in user_action.get_slots() :
            
            next_state = "check_account"
            bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=None,
                                values=None,
                                message="api_call:check_account_api, user_account:{}".format(self.user_values["user_account"]),
                                description="API_ACCOUNT_CHECK",
                                templates=self.templates)
        else :
            
            if user_action.get_description() == "ANOTHER_SLOT_VALUE" :
                slot_given = user_action.get_slots()[0]
                appropriate_state = self.states[slot_given]
                
                next_state, bot_action = appropriate_state(user_action)
                
            else :
                
                next_state = "user_account"
                bot_action = Action(actor="Bot",
                                   action="request",
                                   slots=None,
                                   values=None,
                                   message="Please select an account",
                                   description="SELECT_ACCOUNT",
                                   templates=self.templates)
        
        return next_state , bot_action
    
    def check_account_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "api_result:success" in user_action.get_message() :
            
            next_state = "api_call"
            api_value = self.user_values["user_account"]
            api_message = "api_call:account_limit_api, user_account:{}".format(self.user_values["user_account"])
            bot_action = Action(actor="Bot",
                               action="api_call",
                               slots=None,
                               values={"api_call" : api_value},
                               message=api_message,
                               description="API_CALL",
                               templates=self.templates)
        else :
            next_state = "change_account"
            slot_message = ",".join(user_action.get_slots())
            bot_message = "It seems that you have not entered a valid account, you available accounts are {}, would you like change the source account ?".format(slot_message)
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=None,
                                values=None,
                                message=bot_message,
                                description="CHANGE_ACCOUNT",
                                templates=self.templates)
        return next_state , bot_action
    
    def change_account_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "accept" in user_action.get_message():
            
            self.slots_to_ask.insert(0,"user_account")
            
            if self.turn_compression :
                next_state = "check_account"
                bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=None,
                                values=None,
                                message="api_call:check_account_api, user_account:{}".format(self.user_values["user_account"]),
                                description="API_ACCOUNT_CHECK",
                                templates=self.templates)
            else :
            
                next_state = "user_account"
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=[next_state],
                                    values=None,
                                    message="Requesting user to provide new user account",
                                    templates=self.templates)
        else :
            next_state = "end_call"
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="Denied to change account",
                                templates=self.templates)
        
        return next_state , bot_action
    
    def api_call_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "api_result:success" in user_action.get_message() :
            
            next_state = "end_call"
            bot_message = "your current limit for account is {}".format(self.user_values["limit"])
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
        print("Reached end of account limit")
        return