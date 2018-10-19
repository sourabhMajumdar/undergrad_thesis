import random
import sys
sys.path.append("..")
from utils import Action
class Transaction_bot(object) :
    
    def __init__(self,templates=None) :
        
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
        
        for slot in user_action.get_slots() :
            
            if slot in self.slots_to_ask :
                
                self.slots_to_ask.remove(slot)
                
    def speak(self,user_action) :
        
        if user_action == None :
            
            print("user_action received is None")
        
        next_state , bot_action = self.current_state(user_action)
        #print("next state is  == > {}".format(next_state))
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
                slot_message = "api_call:initial_slot_check,"
                for slot in slots_given :
                    slot_message += " {}:{},".format(slot,self.user_values[slot])
                bot_action = Action(actor="Bot",
                                    action="api_call",
                                    slots=user_action.get_slots(),
                                    values=None,
                                    message=slot_message[:-1],
                                    description="API_INITIAL_SLOT_CHECK",
                                    templates=self.templates)
            
            else :
                
                next_state = self.slots_to_ask[0]
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=[next_state],
                                    values=None,
                                    message="requesting the values for {}".format(next_state),
                                    templates=self.templates)        
        else :           
            
            next_state = "initial"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=["intent"],
                                values=None,
                                message="Get the intent first",
                                templates=self.templates)
        
        return next_state , bot_action
    
    def check_initial_state(self,user_action) :
        # if the below message is received then it means that initial check is successful and move on to the next appropriate slots
        
        if user_action.get_message() == "api_result:success" :
            
            if not self.slots_to_ask :
                
                next_state = "confirmation_state"
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=None,
                                    values=None,
                                    message="confirm transaction ?",
                                    templates=self.templates)
            
            else :
                
                next_state = self.slots_to_ask[0]
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=[next_state],
                                    values=None,
                                    message="request for {} ".format(next_state),
                                    templates=self.templates)
        
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
            bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=["user_account"],
                                values=None,
                                message="api_call:account_check_api, user_account:{}".format(self.user_values["user_account"]),
                                description="API_ACCOUNT_CHECK",
                                templates=self.templates)
                    
        else :
            
            next_state = "user_account"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=["user_account"],
                                values=None,
                                message="requesting user to specify the account",
                                templates=self.templates)
            
        return next_state , bot_action
    
    def check_account_state(self,user_action) :
        
        if user_action.get_message() == "api_result:success" :
            
            if "amount" in self.user_values.keys() :
                
                next_state = "check_amount"
                bot_action = Action(actor="Bot",
                                    action="api_call",
                                    slots=["limit","balance"],
                                    values=None,
                                    message="api_call:amount_check_api, user_account:{}, amount:{}".format(self.user_values["user_account"],self.user_values["amount"]),
                                    description="API_AMOUNT_CHECK",
                                    templates=self.templates)
            
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
                                        message="confirm transaction ?",
                                        templates=self.templates)
            
                else :
                    
                    next_state = self.slots_to_ask[0]
                    bot_action = Action(actor="Bot",
                                        action="request",
                                        slots=[next_state],
                                        values=None,
                                        message="request for {}".format(next_state),
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
        
        if user_action.get_message() == "accept" :
            
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
                                message="You denied to change the account",
                                templates=self.templates)
        
        return next_state , bot_action 
    
    def destination_state(self,user_action) :
        # remove the slot already asked
        self.remove_informed_slots(user_action)
            
        # update the user information with the new values got
        self.record_user_values(user_action)
        
        if "destination_name" in user_action.get_slots() :
            
            # sample out a new state based on the remaining slots to ask
            next_state = "check_destination"
            bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=["destination_name"],
                                values=None,
                                message="api_call:destination_check_api, destination_name:{}".format(self.user_values["destination_name"]),
                                description="API_DESTINATION_NAME_CHECK",
                                templates=self.templates)
        
        else :
            
            next_state = "destination_name"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=["destination_name"],
                                values=None,
                                message="provide the Name of the Receiver",
                                templates=self.templates)
        
        return next_state , bot_action
    
    def check_destination_name_state(self,user_action) :
        
        if user_action.get_message() == "api_result:success" :
            
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
                                    message="confirm transaction ?",
                                    templates=self.templates)
                
            else :
                next_state = self.slots_to_ask[0]
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=[next_state],
                                    values=None,
                                    message="Requesting the name for {}".format(next_state),
                                    templates=self.templates)
        
        else :
            
            next_state = "change_destination_name"
            slot_message = ",".join(user_action.get_slots())
            bot_message = "The recipient you are trying to provide doesn't exist, available list of recipients is {}, would you like to change the recipient ?".format(slot_message)
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=None,
                                values=None,
                                message=bot_message,
                                description="CHANGE_DESTINATION_NAME",
                                templates=self.templates)
        
        return next_state , bot_action
    
    def change_destination_name_state(self,user_action) :
        
        if user_action.get_message() == "accept" :
            
            next_state = "destination_name"
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
                                message="User failed to change the account",
                                templates=self.templates)
        
        return next_state , bot_action
    
    def amount_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "amount" in user_action.get_slots() :
             
            if "user_account" in self.user_values.keys() :
                
                # No random check this time because we have to check if the amount given is correct or not
                next_state = "check_amount"
                bot_action = Action(actor="Bot",
                                    action="api_call",
                                    slots=["limit","balance"],
                                    values=None,
                                    message="api_call:check_amount, user_account:{}, amount:{}".format(self.user_values["user_account"],self.user_values["amount"]),
                                    description="API_AMOUNT_CHECK",
                                    templates=self.templates)
            
            else :
                
                next_state = self.slots_to_ask[0]
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=[next_state],
                                    values=None,
                                    message="requesting user to provide {} ".format(next_state),
                                    templates=self.templates)
        
        else :
            
            next_state = "amount"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=["amount"],
                                values=None,
                                message="requesting the user to provide the Amount",
                                templates=self.templates)
            
        return next_state , bot_action

    
    def check_amount_state(self,user_action) :
        
        self.record_user_values(user_action)
        
        if user_action.get_message() == "api_result:success" :
            
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
                                    message="confirm transaction ?",
                                    templates=self.templates)
            
            else :
                
                next_state = self.slots_to_ask[0]
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=[next_state],
                                    values=None,
                                    message="request for {} ".format(next_state),
                                    templates=self.templates)

        else :
            
            next_state = "change_amount"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=None,
                                values=None,
                                message="It seems the amount you provided can't be processed because your transaction limit is {} and your current balance is {} so the maximum you can transfer is {}, would you like to reduce your amount to this amount ?".format(self.user_values["limit"],self.user_values["balance"],self.user_values["max_transferable_amt"]),
                                description="CHANGE_TO_MAX_TRANSFERABLE_AMT",
                                templates=self.templates)
        
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
                                    message="confirm transaction ?",
                                    templates=self.templates)
            
            else :
                
                next_state = self.slots_to_ask[0]
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=[next_state],
                                    values=None,
                                    message="request for {} ".format(next_state),
                                    templates=self.templates)
        
        else :
            
            next_state = "end_call"
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="Rejected to change the decision",
                                templates=self.templates)
        
        return next_state , bot_action
    
    # This is a dead state and I don't know why it is here , but I don't know what will happen if I remove this function
    def balance_state(self,user_action) :
        return
    
    # ask for confirmation
    def confirmation_state(self,user_action) :
        
        if user_action.get_message() == "accept" :
            
            next_state = "api_call"
            #api_value = self.user_values["user_account"] + " " + self.user_values["destination_name"] + " "  + str(self.user_values["amount"])
            bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=["user_account","destination_name","amount"],
                                values={"user_account" : self.user_values["user_account"],
                                        "destination_name" : self.user_values["destination_name"],
                                        "amount" : self.user_values["amount"]},
                                message="api_call:transaction_api, user_account:{}, destination_name:{}, amount:{}".format(self.user_values["user_account"],self.user_values["destination_name"],self.user_values["amount"]),
                                description="API_CALL",
                                templates=self.templates)
        
        else :
            
            next_state = "end_call"
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="User refused to confirm transaction",
                                templates=self.templates)
        
        return next_state, bot_action

    # end the call
    def end_call_state(self,user_action) :
        
        print("inside end_call state")
        next_state = "initial"
        bot_action = None
        
        return next_state , bot_action
    
    # Api call state
    def api_call_state(self,user_action) :
        
        if user_action.get_message() == "api_result:success" :
            
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="{} conducted successfully, ciao !!".format(self.user_values["intent"]),
                                templates=self.templates)
        
        else :
            
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="error in processing {}".format(self.user_values["intent"]),
                                templates=self.templates)
        
        next_state = "end_call"
        
        return next_state , bot_action
