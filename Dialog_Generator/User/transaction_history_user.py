import random
import sys
sys.path.append("..")
from utils import Action
class Transaction_history_user() :
    def __init__(self,templates=None) :
        
        # Below is the available pool of values from which we will create a Custom user for the transaction
        self.user_names = ["Sourabh","Serra","Simone","Marco","Vevake","Matteo","Tahir","Samuel"]
        self.user_accounts = ["Savings","Credit","Checkin"]
        self.user_balances = [400,1300,3000,8000]
        self.user_transaction_types = ["credit","debit"]
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
                                message="providing value for user_account",
                                templates=self.templates)
        
            
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
                                     message=accept_message,
                                     templates=self.templates)
            else :
                
                user_action = Action(actor=actual_actor,
                                     action="inform",
                                     slots=None,
                                     values=None,
                                     message=reject_message,
                                     templates=self.templates)
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
                                         message="Providing value for {}".format(bot_action.get_slots()[0]),
                                         templates=self.templates)
                
                else :
                    
                    user_action = Action(actor="User",
                                       action="inform",
                                       slots=["intent"],
                                       values={"intent" : self.user["intent"],"name" : self.user["name"]},
                                       message="Providing value for intent",
                                       templates=self.templates)
            else:
                
                user_action = self.perform_random_action(bot_action)
        
        elif bot_action.get_action() == "api_call" :
            
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
        if bot_action.get_action() == "request_accounts" :
            
            slot_message = ",".join(self.user["user_accounts"])
            bot_message = "list_of_accounts : {}".format(slot_message)
            user_action = Action(actor="API_RESP",
                                action="inform",
                                slots = self.user["user_accounts"],
                                values=None,
                                message=bot_message,
                                description="LIST_OF_SLOTS",
                                templates=self.templates)
        
        elif bot_action.get_action() == "destination_name_check" :
            
            if self.user["destination_name"] in self.user["destination_names"] :
                
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=None,
                                     values=None,
                                     message="destination_name_check : success",
                                     templates=self.templates)
            else :
                
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=self.user["destination_names"],
                                     values={"destination_names" : self.user["destination_names"]},
                                     message="destination_name_check : failed",
                                     templates=self.templates)
                
        
        
        return user_action            
        