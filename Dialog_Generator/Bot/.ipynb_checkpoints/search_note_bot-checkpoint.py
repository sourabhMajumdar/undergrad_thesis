import random
import sys
sys.path.append("..")
from utils import Action
class Search_note_bot(object) :
    
    def __init__(self,
                 templates=None,
                 turn_compression=False,
                 re_order=False,
                 audit_more=False) :
        
        self.last_slot = None
        self.list_of_slots = ["user_account","destination_name","amount"]
        self.slots_to_ask = ["object"]
        self.user_values = dict()
        self.states = {"initial" : self.initial_state ,
                       "check_initial" : self.check_initial_state,
                       "object" : self.object_state ,
                       "check_object" : self.check_object_state,
                       "change_object" : self.change_object_state,
                       "partner_name" : self.partner_name_state ,
                       "check_partner_name" : self.check_partner_name_state,
                       "change_partner_name" : self.change_partner_name_state,
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
        #print("next state is  == > {}".format(next_state))
        self.current_state = self.states[next_state]
        
        return bot_action
        
    # meet the initial state, here the user may provide one or more than one values
    def initial_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if user_action.get_slots() :
            
            if "intent" in user_action.get_slots() and len(user_action.get_slots()) > 2 :
                
                next_state = "check_initial"
                slots_given = user_action.get_slots()[1:] 
                slot_message = "api_call:initial_slot_check_api,"
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
                
                if self.re_order :
                    next_state = random.sample(self.slots_to_ask,1)[0]
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
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        if "api_result:success" in user_action.get_message() :
            
            if not self.slots_to_ask :
                
                next_state = "api_call"
                bot_action = Action(actor="Bot",
                                    action="api_call",
                                    slots=None,
                                    values=None,
                                    message="api_call:search_note_api, object:{}, partner_name:{}".format(self.user_values["object"],self.user_values["partner_name"]),
                                    description="API_CALL",
                                    templates=self.templates)
            
            else :
                
                if self.re_order :
                    next_state = random.sample(self.slots_to_ask,1)[0]
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
    
    def object_state(self,user_action) :
        
        # if user account has been given then 
        if "object" in user_action.get_slots() :
            
            # remove the slot which has already been asked
            self.remove_informed_slots(user_action)
                
            # update user infomation
            user_values = user_action.get_values()
            
            # record and store all the values given by the user
            self.record_user_values(user_action)
            
            
            # pick a slot to ask randomly from the remaining slots_to_ask
            next_state = "check_object"
            
            # perform the corresponding bot information
            bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=["object"],
                                values=None,
                                message="api_call:check_object_api, object:{}".format(self.user_values["object"]),
                                description="API_OBJECT_CHECK",
                                templates=self.templates)
                    
        else :
            
            if user_action.get_description() == "ANOTHER_SLOT_VALUE" :
                slot_given = user_action.get_slots()[0]
                appropriate_state = self.states[slot_given]
                
                next_state, bot_action = appropriate_state(user_action)
            else :
                
                next_state = "object"
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=["object"],
                                    values=None,
                                    message="requesting user to specify the object",
                                    templates=self.templates)
                
            
        return next_state , bot_action
    
    def check_object_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "api_result:success" in user_action.get_message() :
                
            if self.priority_states :
                next_state = self.priority_states[0]
                bot_action = self.priority_actions[next_state]
            
                self.priority_states.remove(next_state)
            
            else :
                
                next_state = "api_call"
                bot_action = Action(actor="Bot",
                                    action="api_call",
                                    slots=None,
                                    values=None,
                                    message="api_call:search_note_api, note:{}, partner_name:{}".format(self.user_values["object"],self.user_values["partner_name"]),
                                    description="API_CALL",
                                    templates=self.templates)        
        else :
            
            if user_action.get_description() == "NOT_NOT_EXIST" :
                next_state = "partner_name"
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=["partner_name"],
                                    values=None,
                                    message="requesting for partner_name",
                                    templates=self.templates)
            else :
                next_state = "end_call"
                bot_action = Action(actor="Bot",
                                    action="end_call",
                                    slots=None,
                                    values=None,
                                    message="can't perform that action",
                                    templates=self.templates)
        
        return next_state , bot_action
    
    def change_object_state(self,user_action) :
        
        if "accept" in user_action.get_message() :
            
            self.slots_to_ask.insert(0,"object")
            
            if self.turn_compression :
                # pick a slot to ask randomly from the remaining slots_to_ask
                next_state = "check_object"
                
                # perform the corresponding bot information
                bot_action = Action(actor="Bot",
                                    action="api_call",
                                    slots=["object"],
                                    values=None,
                                    message="api_call:check_object_api, object:{}".format(self.user_values["object"]),
                                    description="API_OBJECT_CHECK",
                                    templates=self.templates)
            else :
                
                next_state = "object"
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=[next_state],
                                    values=None,
                                    message="Requesting user to provide new object",
                                    templates=self.templates)
        
        else :
            
            next_state = "end_call"
            bot_action = Action(actor="Bot",
                                action="end_call",
                                slots=None,
                                values=None,
                                message="You denied to change the object",
                                templates=self.templates)
        
        return next_state , bot_action 
    
    def partner_name_state(self,user_action) :
        # remove the slot already asked
        self.remove_informed_slots(user_action)
            
        # update the user information with the new values got
        self.record_user_values(user_action)
        
        if "partner_name" in user_action.get_slots() :
            
            # sample out a new state based on the remaining slots to ask
            next_state = "check_partner_name"
            bot_action = Action(actor="Bot",
                                action="api_call",
                                slots=["destination_name"],
                                values=None,
                                message="api_call:check_partner_name_api, partner_name:{}".format(self.user_values["partner_name"]),
                                description="API_PARTNER_NAME_CHECK",
                                templates=self.templates)
        
        else :
            
            if user_action.get_description() == "ANOTHER_SLOT_VALUE" :
                slot_given = user_action.get_slots()[0]
                appropriate_state = self.states[slot_given]
                
                next_state, bot_action = appropriate_state(user_action)
            else :
                
                next_state = "partner_name"
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=["partner_name"],
                                    values=None,
                                    message="provide the Name of the partner",
                                    templates=self.templates)
        
        return next_state , bot_action
    
    def check_partner_name_state(self,user_action) :
        
        self.record_user_values(user_action)
        self.remove_informed_slots(user_action)
        
        if "api_result:success" in user_action.get_message() :
                
                next_state = "object"
                slot_message = ','.join(self.user["objects"])
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=None,
                                    values=None,
                                    message="You have the following notes from the partner : {}, which one do you wish to see ?".format(slot_message),
                                    templates=self.templates)
        
        else :
            
            if user_action.get_description() == "OBJECT_NOT_ASSOCIATED_WITH_PARTNER_NAME" :
                bot_message = "I am sorry, {} can't perform {}".format(self.user["partner_name"],self.user["object"])
            else :
                bot_message = "The partner name doesn't exists in your directory"
                
            next_state = "change_partner_name"
            bot_action = Action(actor="Bot",
                                action="request",
                                slots=None,
                                values=None,
                                message=bot_message,
                                description="CHANGE_PARTNER_NAME",
                                templates=self.templates)
        
        return next_state , bot_action
    
    def change_partner_name_state(self,user_action) :
        
        if "accept" in user_action.get_message() :
            
            self.slots_to_ask.insert(0,"partner_name")
            if self.turn_compression :
                next_state = "check_partner_name"
                bot_action = Action(actor="Bot",
                                    action="api_call",
                                    slots=["destination_name"],
                                    values=None,
                                    message="api_call:check_partner_name_api, partner_name:{}".format(self.user_values["partner_name"]),
                                    description="API_PARTNER_NAME_CHECK",
                                    templates=self.templates)
            else :
                
                next_state = "partner_name"
                bot_action = Action(actor="Bot",
                                    action="request",
                                    slots=[next_state],
                                    values=None,
                                    message="Requesting user to provide new partner name",
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
    


    def end_call_state(self,user_action) :
        
        #print("inside end_call state")
        next_state = "initial"
        bot_action = None
        
        return next_state , bot_action
    
    # Api call state
    def api_call_state(self,user_action) :
        
        if "api_result:success" in user_action.get_message() :
            
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