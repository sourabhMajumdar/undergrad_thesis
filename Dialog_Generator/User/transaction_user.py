import random
import sys
sys.path.append("..")
from utils import Action
class Transaction_user() :
    def __init__(self,templates=None) :
        
        # Below is the available pool of values from which we will create a Custom user for the transaction
        self.user_names = ["Sourabh","Serra","Simone","Marco","Vevake","Matteo","Tahir","Samuel"]
        self.user_accounts = ["Savings","Credit","Checkin"]
        self.transaction_limit = [1000,2000,5000]
        self.user_balances = [400,1300,3000,8000]
        self.transfer_amt = [200,800,1200,1600,2400,4500,9000]
        self.slots = ["user_account","destination_name","amount"]
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
                                         message="Providing intent",
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
                                                                                                                                   self.user["max_transferable_amt"]),
                                     templates=self.templates)
            
            else :
                
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=["limit","balance","max_transferable_amt"],
                                     values={"limit" : self.user["limit"],
                                             "balance" : self.user["balance"],
                                             "max_transferable_amt" : self.user["max_transferable_amt"]},
                                     message="amount_check : success",
                                     templates=self.templates)
        
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
                                                                message="user_account:{}".format(self.user["user_account"]),
                                                                templates=self.templates)
            
            # if destination name is given in the initial slots then check if it is appropriate
            if "destination_name" in bot_action.get_slots() and self.user["destination_name"] not in self.user["destination_names"] :
                
                self.priority_states.append("check_destination")
                self.priority_actions["check_destination"] = Action(actor="API",
                                                                   action="destination_name_check",
                                                                   slots=["destination_name"],
                                                                   values=None,
                                                                   message="destination_name:{}".format(self.user["destination_name"]),
                                                                   templates=self.templates)
            
            # if both user_account and amount are present then check if the amount satisfies the criteria
            if "user_account" in bot_action.get_slots() and "amount" in bot_action.get_slots() and self.user["amount"] > self.user["max_transferable_amt"] :
                
                self.priority_states.append("check_amount")
                self.priority_actions["check_amount"] = Action(actor="API",
                                              action="amount_check",
                                              slots=["limit","balance"],
                                              values=None,
                                              message="user_account:{} , amount:{}".format(self.user["user_account"],
                                                                      self.user["amount"]),
                                              templates=self.templates)
            
            # if self.priority_states is no empty then one or more than one value is incorrect then send appropriate error message
            if self.priority_states :
                
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=self.priority_states,
                                     values=self.priority_actions,
                                     message="initial_slots_check : failed, message='one or more slots are faulty'",
                                     templates=self.templates)
            
            # if everything is okay then send the correct message
            else :
                
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=bot_action.get_slots(),
                                     values=None,
                                     message="initial_slots_check : success",
                                     templates=self.templates)
        
        # if the requested action is an account check
        elif bot_action.get_action() == "account_check" :
            
            if self.user["user_account"] in self.user["user_accounts"] :
                
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=["account"],
                                     values=self.user,
                                     message="account_check : success",
                                     templates=self.templates)
            
            else :
                
                slot_message = ','.join(self.user["user_accounts"])
                api_message = "account_check : failed , message='availbale list of user accounts : " + slot_message + "'"
                
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=self.user["user_accounts"],
                                     values=self.user,
                                     message=api_message,
                                     templates=self.templates)
        
        # if the requested action is destination name check
        elif bot_action.get_action() == "destination_name_check" :
            
            if self.user["destination_name"] in self.user["destination_names"] :
                
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=["destination_name"],
                                     values=None,
                                     message="destination_name_check : success",
                                     templates=self.templates)
            
            else :
                
                slot_message = ','.join(self.user["destination_names"])
                api_message = "destination_name_check : failed , message='available list of names : " + slot_message + "'"
                user_action = Action(actor="API_RESP",
                                     action="inform",
                                     slots=self.user["destination_names"],
                                     values={"destination_names" : self.user["destination_names"]},
                                     message=api_message,
                                     templates=self.templates)
        
        return user_action            
        