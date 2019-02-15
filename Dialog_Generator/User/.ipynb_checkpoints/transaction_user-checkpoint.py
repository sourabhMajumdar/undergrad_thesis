import random
import sys
import copy
sys.path.append("..")
from utils import Action

class Transaction_user() :
    def __init__(self,
                 templates=None,
                 list_of_user_profiles=None,
                 user_values=None,
                 turn_compression=False,
                 new_api=False,
                 another_slot=False,
                 audit_more=False) :
        
        # Below is the available pool of values from which we will create a Custom user for the transaction
        self.user_names = user_values["partner_names"]
        self.user_accounts = user_values["user_accounts"]
        self.transfer_amt = user_values["amount_values"]
        self.slots = ["user_account","partner_name","amount"]
        
        self.slots_to_give = copy.deepcopy(self.slots)
        
        self.templates = templates
        self.priority_states = list()
        self.priority_actions = dict()
        self.turn_compression = turn_compression
        self.new_api = new_api
        self.another_slot = another_slot
        self.audit_more = audit_more
        
        
        self.override = False
        
        self.state_track = dict()
        self.state_track["CHANGE_PARTNER_NAME"] = 0
        self.state_track["CHANGE_AMOUNT"] = 0
        self.state_track["CHANGE_ACCOUNT"] = 0
        # create the custom user
        self.user = dict()
        
        row_chosen = random.randint(0,len(list_of_user_profiles)-1)
        self.user_chosen = list_of_user_profiles[row_chosen]
        
        self.create_user_profile(self.user_chosen)
    
    def sort_my_slots(self,slots_given) :
        
        
        if slots_given :
            
            slots_sorted = list()
            
            if "user_account" in slots_given :
                slots_sorted.append("user_account")
                slots_given.remove("user_account")
            
            if "partner_name" in slots_given :
                slots_sorted.append("partner_name")
                slots_given.remove("partner_name")
            
            if "amount" in slots_given :
                slots_sorted.append("amount")
                slots_given.remove("amount")
        
            for slot in slots_given :
                slots_sorted.append(slot)
        else :
            slots_sorted = list()
        
        return slots_sorted
    
    def create_user_profile(self,user_chosen) :
        
        # Every value is assigned randomly 
        
        # selectinng name of sender and reciever
        
        #names = random.sample(self.user_names,2)
        
        #self.user["name"] = names[0]
        self.user["name"] = user_chosen["name"]
        
        #self.user["partner_name"] = names[1]
    
        #number_of_partner_names = random.randint(1,len(self.user_names))
        #self.user["partner_names"] = random.sample(self.user_names,number_of_partner_names)
        #self.user["partner_names"].sort()
        
        list_of_partner_names = user_chosen["partner_names"].strip().split(',')
        self.user["partner_names"] = list_of_partner_names
        self.user["partner_names"].sort()
        
        self.user["partner_name"] = random.sample(self.user_names,1)[0]
        
        #selecting the usr_account to make the transaction from
        #self.user["user_account"] = random.sample(self.user_accounts,1)[0]
        
        #number_of_user_accounts = random.randint(1,len(self.user_accounts))
        #self.user["user_accounts"] = random.sample(self.user_accounts,number_of_user_accounts)
        #self.user["user_accounts"].sort()
        
        list_of_user_accounts = user_chosen["user_accounts"].strip().split(',')
        self.user["user_accounts"] = list_of_user_accounts
        self.user["user_accounts"].sort()
        
        self.user["user_account"] = random.sample(self.user_accounts,1)[0]
        
        
        # selecting the amount to be transfered
        self.user["amount"] = int(random.sample(self.transfer_amt,1)[0])
        #self.user["amount"] = int(user_chosen["amount"])
        
        
        # selecting the balance of the user
        #self.user["balance"] = random.sample(self.user_balances,1)[0]
        self.user["balance"] = int(user_chosen["balance"])
        
        # selecting the limit of the user
        #self.user["limit"] = random.sample(self.transaction_limit,1)[0]
        self.user["limit"] = int(user_chosen["limit"])
        
        
        # setting up the max_transferable amount
        self.user["max_transferable_amt"] = min(self.user["limit"],self.user["balance"])
        
        # setting up the intent
        self.user["intent"] = "transaction"
        self.user["domain_description"] = "transaction_memory_network"
    
    # Returns the respective value of the slot
    def get_value(self,slot_asked) :
        
        return self.user[slot_asked]
    
    def remove_slot(self,slot_given) :
        if slot_given in self.slots :
            self.slots.remove(slot_given)
        
    
    def perform_random_action(self,bot_action) :
        
        values_to_give = dict()
        actual_actor = None
        actual_action = None
        slot_to_give = list()
        pattern_to_give = list()
        
        if bot_action.get_description() == "API_CALL" :
            
            actual_actor = "API"
            actual_action = None
            accept_message = "api_response:api_call, api_result:success"
            reject_message = "api_response:api_call, api_result:failed"
            slot_concerned = "api"
        
        elif bot_action.get_description() == "CHANGE_ACCOUNT" :
            
            
            slot_to_give.append("user_account")
            new_account = random.sample(self.user_accounts,1)[0]
            while new_account == self.user["user_account"] :
                new_account = random.sample(self.user_accounts,1)[0]
                
            self.user["user_account"] = new_account
            
            if self.state_track["CHANGE_ACCOUNT"] > 2 :
                self.override = True
                new_account = random.sample(self.user["user_accounts"],1)[0]
                self.user["user_account"] = new_account
                
            values_to_give["user_account"] = new_account
            
            actual_actor = "User"
            actual_action = None
            accept_message = "accept"
            reject_message = "reject"
            slot_concerned = "user_account"
            
            if self.audit_more :
                slots_to_change = copy.deepcopy(self.slots_to_give)
                slots_to_change.remove("user_account")
                
                slot_chosen_to_change = random.sample(slots_to_change,1)[0]
                
                slot_choice_list = list()
                
                if slot_chosen_to_change == "partner_name" :
                    slot_choice_list = self.user_names
                elif slot_chosen_to_change == "amount" :
                    slot_choice_list = self.transfer_amt
                    
                new_value = random.sample(slot_choice_list,1)[0]
                
                while new_value == self.user[slot_chosen_to_change] :
                    new_value = random.sample(slot_choice_list,1)[0]
                    
                values_to_give[slot_chosen_to_change] = new_value
                
                slot_to_give.append(slot_chosen_to_change)
                pattern_to_give.append("audit_more")
                
                accept_message = "accept use {} and change {} to {}".format(new_account,slot_chosen_to_change,new_value)
                
            
                
            if self.turn_compression :
                accept_message = "accept use {}".format(new_account)
                pattern_to_give.append("turn_compression")
                
            self.state_track["CHANGE_ACCOUNT"] += 1
        
        elif bot_action.get_description() == "CHANGE_AMOUNT" :
            
            slot_to_give.append("amount")
            if self.state_track["CHANGE_AMOUNT"] > 2 :
                self.override = True
                
            actual_actor = "User"
            actual_action = None
            accept_message = "accept"
            reject_message = "reject"
            slot_concerned = "amount"
            self.user["amount"] = self.user["max_transferable_amt"]
            values_to_give["amount"] = self.user["max_transferable_amt"]
            
            self.state_track["CHANGE_AMOUNT"] += 1
        
        elif bot_action.get_description() == "CHANGE_PARTNER_NAME" :
            
            
            
            slot_to_give.append("partner_name")
                
            new_partner_name = random.sample(self.user_names,1)[0]
            
            while new_partner_name == self.user["name"] or new_partner_name == self.user["partner_name"] :
                new_partner_name = random.sample(self.user_names,1)[0]
                
            self.user["partner_name"] = new_partner_name
            
            if self.state_track["CHANGE_PARTNER_NAME"] > 2 :
                self.override = True
                new_partner_name = random.sample(self.user["partner_names"],1)[0]
                self.user["partner_name"] = new_partner_name
                
                
            values_to_give["partner_name"] = new_partner_name
            
            actual_actor = "User"
            actual_action = None
            accept_message = "accept"
            reject_message = "reject"
            slot_concerned = "partner_name"
            
            if self.audit_more :
                slots_to_change = copy.deepcopy(self.slots_to_give)
                slots_to_change.remove("partner_name")
                
                slot_chosen_to_change = random.sample(slots_to_change,1)[0]
                
                slot_choice_list = list()
                
                if slot_chosen_to_change == "user_account" :
                    slot_choice_list = self.user_accounts
                elif slot_chosen_to_change == "amount" :
                    slot_choice_list = self.transfer_amt
                    
                new_value = random.sample(slot_choice_list,1)[0]
                pattern_to_give.append("audit_more")
                
                while new_value == self.user[slot_chosen_to_change] :
                    new_value = random.sample(slot_choice_list,1)[0]
                    
                values_to_give[slot_chosen_to_change] = new_value
                slot_to_give.append(slot_chosen_to_change)
                
                accept_message = "accept use {} and change {} to {}".format(new_partner_name,slot_chosen_to_change,new_value)

            if self.turn_compression :
                accept_message = "accept go for {}".format(new_partner_name)
                pattern_to_give.append("audit_more")
                
            self.state_track["CHANGE_PARTNER_NAME"] += 1
        
        else :
            actual_actor = "User"
            accept_message = "accept"
            reject_message = "reject"
            
        toss = random.randint(0,100)
        if self.override or toss > 10 :
            self.override = False
            user_action = Action(actor=actual_actor,
                                 action=actual_action,
                                 slots=slot_to_give,
                                 values=values_to_give,
                                 message=accept_message,
                                 templates=self.templates,
                                 pattern_marker=pattern_to_give)
        else :
            user_action = Action(actor=actual_actor,
                                 action=actual_action,
                                 slots=slot_to_give,
                                 values=values_to_give,
                                 message=reject_message,
                                 templates=self.templates,
                                 pattern_marker=None)
        return user_action
    # This is the function that converses with the bot through 'Action' Objects
    def speak(self,bot_action) :
        user_action = None
        if bot_action.get_action() == "api_call" :
            
            user_action = self.api_response(bot_action)            

        elif bot_action.get_action() == "request" :
            
            if bot_action.get_slots() != None :
                
                if bot_action.get_slots()[0] != "intent" :
                    
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
                    
                    for slot in slots_to_inform :
                        self.remove_slot(slot)
                        
                    
                    all_slots = ["intent","domain_description"] + self.sort_my_slots(slots_to_inform)
                    
                    values_to_inform = dict()
                    
                    for slot in all_slots :
                        values_to_inform[slot] = self.user[slot]
                    
                    user_action = Action(actor="User",
                                         action="inform",
                                         slots=all_slots,
                                         values=values_to_inform,
                                         message="Providing intent",
                                         slot_concerned="intent",
                                         templates=self.templates,
                                         pattern_marker=pattern_to_give)
            else :
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
        if bot_action.get_description() == "API_AMOUNT_CHECK" :
            
            if self.user["amount"] > self.user["max_transferable_amt"] :
                
                user_action = Action(actor="API",
                                     action=None,
                                     slots=["limit","balance","max_transferable_amt"],
                                     values={"limit" : self.user["limit"],
                                             "balance" : self.user["balance"],
                                             "max_transferable_amt" : self.user["max_transferable_amt"]},
                                     message="api_response:amount_check_api, limit:{},balance:{},max_transferable_amt:{}, message:'change to max_transferable_amt ?'".format(self.user["limit"],
                                                                                                                                   self.user["balance"],
                                                                                                                                   self.user["max_transferable_amt"]),
                                     slot_concerned="amount",
                                     templates=self.templates)
            
            else :
                
                user_action = Action(actor="API",
                                     action=None,
                                     slots=["limit","balance","max_transferable_amt"],
                                     values={"limit" : self.user["limit"],
                                             "balance" : self.user["balance"],
                                             "max_transferable_amt" : self.user["max_transferable_amt"]},
                                     message="api_response:amount_check_api, api_result:success",
                                     slot_concerned="amount",
                                     templates=self.templates)
        
        # if the API action askes for a initial state check
        elif bot_action.get_description() == "API_INITIAL_SLOT_CHECK" :
            
            # if the flag becomes true at the end of this segment then it means that one or more than one slots are incorrect
            flag = False
            error_message = list()
            order_of_slots = list()
            # if user account is given in the initial slots then check if it is appropriate
            if "user_account" in bot_action.get_slots() and self.user["user_account"] not in self.user["user_accounts"] :
                
                order_of_slots.append("change_account")
                
                self.priority_states.append("change_account")
                slot_message = ','.join(self.user["user_accounts"])
                bot_message = "It seems that you have not entered a valid account, you available accounts are {}, would you like change the source account ?".format(slot_message)
                self.priority_actions["change_account"] = Action(actor="Bot",
                                                                action="request",
                                                                slots=None,
                                                                values=None,
                                                                message=bot_message,
                                                                description="CHANGE_ACCOUNT",
                                                                 slot_concerned="user_account",
                                                                templates=self.templates)
            
            # if partner name is given in the initial slots then check if it is appropriate
            if "partner_name" in bot_action.get_slots() and self.user["partner_name"] not in self.user["partner_names"] :
                
                order_of_slots.append("change_partner_name")
                self.priority_states.append("change_partner_name")
                slot_message = ','.join(self.user["partner_names"])
                bot_message = "The recipient you are trying to provide doesn't exist, available list of recipients is {}, would you like to change the recipient ?".format(slot_message)
                self.priority_actions["change_partner_name"] = Action(actor="Bot",
                                                                    action="request",
                                                                    slots=None,
                                                                    values=None,
                                                                    message=bot_message,
                                                                    description="CHANGE_PARTNER_NAME",
                                                                      slot_concerned="parnter_name",
                                                                    templates=self.templates)
            
            # if both user_account and amount are present then check if the amount satisfies the criteria
            if "user_account" in bot_action.get_slots() and "amount" in bot_action.get_slots() and self.user["amount"] > self.user["max_transferable_amt"] :
                
                order_of_slots.append("change_amount")
                self.priority_states.append("change_amount")
                self.priority_actions["change_amount"] = Action(actor="Bot",
                                                                action="request",
                                                                slots=None,
                                                                values=None,
                                                                message="It seems the amount you provided can't be processed because your transaction limit is {} and your current balance is {} so the maximum you can transfer is {}, would you like to reduce your amount to this amount ?".format(self.user["limit"],self.user["balance"],self.user["max_transferable_amt"]),
                                                                description="CHANGE_TO_MAX_TRANSFERABLE_AMT",
                                                                slot_concerned="amount",
                                                                templates=self.templates)
                
            
            # if self.priority_states is no empty then one or more than one value is incorrect then send appropriate error message
            if self.priority_states :
                order_message = ','.join(order_of_slots)
                user_action = Action(actor="API",
                                     action=None,
                                     slots=self.priority_states,
                                     values=self.priority_actions,
                                     message="api_response:initial_slot_check_api, api_result:failed, message:'{}'".format(order_message),
                                     slot_concerned="initial",
                                     templates=self.templates)
            
            # if everything is okay then send the correct message
            else :
                
                user_action = Action(actor="API",
                                     action=None,
                                     slots=bot_action.get_slots(),
                                     values=None,
                                     message="api_response:initial_slot_check_api, api_result:success",
                                     slot_concerned="initial",
                                     templates=self.templates)
        
        # if the requested action is an account check
        elif bot_action.get_description() == "API_ACCOUNT_CHECK" :
            #print("checking account")
            if self.user["user_account"] in self.user["user_accounts"] :
                
                user_action = Action(actor="API",
                                     action=None,
                                     slots=["account"],
                                     values=self.user,
                                     message="api_response:account_check_api, api_result:success",
                                     slot_concerned="user_account",
                                     templates=self.templates)
            
            else :
                
                slot_message = ','.join(self.user["user_accounts"])
                api_message = "api_response:account_check_api, api_result:failed, message:'availbale list of user accounts : {}'".format(slot_message)
                
                user_action = Action(actor="API",
                                     action=None,
                                     slots=self.user["user_accounts"],
                                     values=self.user,
                                     message=api_message,
                                     slot_concerned="user_account",
                                     templates=self.templates)
        
        # if the requested action is partner name check
        elif bot_action.get_description() == "API_PARTNER_NAME_CHECK" :
            
            if self.user["partner_name"] in self.user["partner_names"] :
                
                user_action = Action(actor="API",
                                     action=None,
                                     slots=["partner_name"],
                                     values=None,
                                     message="api_response:partner_name_check_api, api_result:success",
                                     slot_concerned="partner_name",
                                     templates=self.templates)
            
            else :
                
                slot_message = ','.join(self.user["partner_names"])
                api_message = "api_response:partner_check_api, api_result:failed, message:'available list of names :{}'".format(slot_message)
                user_action = Action(actor="API",
                                     action=None,
                                     slots=self.user["partner_names"],
                                     values={"partner_names" : self.user["partner_names"]},
                                     message=api_message,
                                     slot_concerned="partner_name",
                                     templates=self.templates)
        else :
            user_action = self.perform_random_action(bot_action)
        
        return user_action            