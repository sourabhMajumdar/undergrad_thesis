import random
import sys
sys.path.append("..")

from utils import Action

class Account_user() :
    def __init__(self,templates=None) :
        
        # Below is the available pool of values from which we will create a Custom user for the transaction
        self.user_names = ["Sourabh","Serra","Simone","Marco","Vevake","Matteo","Tahir","Samuel"]
        self.user_accounts = ["Savings","Credit","Checkin"]
        self.user_balances = [400,1300,3000,8000]
        self.slots = ["user_account"]
        self.templates = templates
        
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
        
        
        for slot in slots_given :
            slots_sorted.append(slot)
        
        return slots_sorted
    
    def create_user_profile(self) :
        
        # Every value is assigned randomly 
        
        # selectinng name of sender and reciever
        
        self.user["name"] = random.sample(self.user_names,1)[0]
                
        #selecting the usr_account to make the transaction from
        
        
        # select at random the number of account the user has.
        number_of_account = random.randint(1,len(self.user_accounts))
        
        self.user["user_accounts"] = random.sample(self.user_accounts,number_of_account)
        
        # select a list of accounts from the given sample
        
        self.user["user_account"] = random.sample(self.user_accounts,1)[0]
        
        self.user["balance"] = random.sample(self.user_balances,1)[0]
                        
        # setting up the intent
        self.user["intent"] = "account_balance"
    
    # Returns the respective value of the slot
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
        if bot_action.get_description() == "SELECT_ACCOUNT" :
               
            self.user["user_account"] = random.sample(self.user_accounts,1)[0]
            
            user_action = Action(actor="User",
                                action="inform",
                                slots=["user_account"],
                                values={"user_account" : self.user["user_account"]},
                                message="providing value for user_account",
                                templates=self.templates)
        
        else :
            
            if bot_action.get_description() == "API_CALL" :
                
                actual_actor = "API"
                actual_action = "api_response"
                accept_message = "api_result:success, balance:{}".format(self.user["balance"])
                reject_message = "api_result:failed"
                values_to_give = {"balance" : self.user["balance"]}
            
            elif bot_action.get_description() == "CHANGE_ACCOUNT" :
                
                actual_actor = "User"
                actual_action = "inform"
                accept_message = "accept"
                reject_message = "reject"
                
                new_account = random.sample(self.user_accounts,1)[0]
                
                while new_account == self.user["user_account"] :
                    new_account = random.sample(self.user_accounts,1)[0]
                
                self.user["user_account"] = new_account
                
            else :
                
                actual_actor = "User"
                actual_action = "inform"
                accept_message = "accept"
                reject_message = "reject"
            
            toss = random.randint(0,1)
            if toss == 1 :
                user_action = Action(actor=actual_actor,
                                     action=actual_action,
                                     slots=None,
                                     values=values_to_give,
                                     message=accept_message,
                                     templates=self.templates)
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
                    
                    user_value = self.get_value(bot_action.get_slots()[0])
                    user_action = Action(actor="User",
                                         action="inform",
                                         slots=bot_action.get_slots(),
                                         values={bot_action.get_slots()[0] : user_value},
                                         message="Providing value for {}".format(bot_action.get_slots()[0]),
                                         templates=self.templates)
                
                else :
                    
                    number_of_slots = random.randint(0,len(self.slots))
                    slots_to_inform = random.sample(self.slots,number_of_slots)
                    all_slots = ["intent"] + self.sort_my_slots(slots_to_inform)
                    values_to_inform = dict()
                    
                    for slot in all_slots :
                        values_to_inform[slot] = self.user[slot]
                    
                    values_to_inform["name"] = self.user["name"]
                        
                    user_action = Action(actor="User",
                                       action="inform",
                                       slots=all_slots,
                                       values=values_to_inform,
                                       message="Providing value for intent",
                                       templates=self.templates)
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
        if bot_action.get_description() == "REQUEST_ACCOUNTS" :
            
            slot_message = ",".join(self.user["user_accounts"])
            bot_message = "list_of_accounts:{}".format(slot_message)
            user_action = Action(actor="API",
                                action="api_response",
                                slots = self.user["user_accounts"],
                                values=None,
                                message=bot_message,
                                description="LIST_OF_SLOTS",
                                templates=self.templates)
            
        elif bot_action.get_description() == "API_INITIAL_SLOT_CHECK" :
            flag = False
            error_message = list()
            
            if "user_account" in bot_action.get_slots() and self.user["user_account"] not in self.user["user_accounts"] :
                
                self.priority_states.append("check_account")
                self.priority_actions["check_account"] = Action(actor="Bot",
                                                                action="api_call",
                                                                slots=["user_account"],
                                                                values=None,
                                                                message="api_call:check_account_api user_account:{}".format(self.user["user_account"]),
                                                                description="API_ACCOUNT_CHECK",
                                                                templates=self.templates)
            if self.priority_states :
                user_action = Action(actor="API",
                                     action="api_response",
                                     slots=self.priority_states,
                                     values=self.priority_actions,
                                     message="api_result:failed, message:'user_account is incorrect'",
                                     templates=self.templates)
            else :
                user_action = Action(actor="API",
                                     action="api_response",
                                     slots=bot_action.get_slots(),
                                     values=None,
                                     message="api_result:success",
                                     templates=self.templates)
                
        elif bot_action.get_description() == "API_ACCOUNT_CHECK" :
            
            #print("checking account")
            if self.user["user_account"] in self.user["user_accounts"] :
                
                user_action = Action(actor="API",
                                     action="api_response",
                                     slots=["account"],
                                     values=self.user,
                                     message="api_result:success",
                                     templates=self.templates)
            else :
                
                slot_message = ','.join(self.user["user_accounts"])
                api_message = "api_result:failed, message:'available list of accounts : {}'".format(slot_message)
                user_action = Action(actor="API",
                                     action="api_response",
                                     slots=self.user["user_accounts"],
                                     values=None,
                                     message=api_message,
                                     templates=self.templates)
            
        else :
            user_action = self.perform_random_action(bot_action)
        
        
        return user_action                    
