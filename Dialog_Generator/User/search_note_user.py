import random
import sys
import copy
sys.path.append("..")
from utils import Action

class Search_note_user() :
    def __init__(self,
                 templates=None,
                 list_of_user_profiles=None,
                 user_values=None,
                 turn_compression=False,
                 new_api=False,
                 another_slot=False,
                 audit_more=False) :
        
        # Below is the available pool of values from which we will create a Custom user for the transaction
        #self.user_names = ["Sourabh","Serra","Simone","Marco","Vevake","Matteo","Tahir","Samuel"]
        self.user_accounts = user_values["user_accounts"]
        
        self.slots = ["object"]
        
        self.intents = ["accounted","credited"]
        self.objects = user_values["notes"]
        self.partner_names = user_values["company_name"]
        
        self.templates = templates
        self.priority_states = list()
        self.priority_actions = dict()
        
        self.turn_compression = turn_compression
        self.new_api = new_api
        self.another_slot = another_slot
        self.audit_more = audit_more
        
        self.override = False
        self.state_track = dict()
        self.state_track["CHANGE_OBJECT"] = 0
        self.state_track["CHANGE_PARTNER_NAME"] = 0
        
        # create the custom user
        self.user = dict()
        
        row_chosen = random.randint(0,len(list_of_user_profiles)-1)
        user_chosen = list_of_user_profiles[row_chosen]
        
        self.create_user_profile(user_chosen)
    
    def sort_my_slots(self,slots_given) :
        
        
        if slots_given :
            
            slots_sorted = list()
            
            if "object" in slots_given :
                slots_sorted.append("object")
                slots_given.remove("object")
            
            if "partner_name" in slots_given :
                slots_sorted.append("partner_name")
                slots_given.remove("partner_name")
            
            for slot in slots_given :
                slots_sorted.append(slot)
        else :
            slots_sorted = list()
        
        return slots_sorted
    
    def create_user_profile(self,user_chosen) :
        
        # Every value is assigned randomly 
        
        # selectinng name of sender and reciever
        
        
        
        self.user["name"] = user_chosen["name"]
        
        
        
        
        self.user["partner_name"] = random.sample(self.partner_names,1)[0]
        
        #number_of_allowed_partner_names = random.randint(1,len(self.partner_names))
        #self.user["partner_names"] = random.sample(self.partner_names,number_of_allowed_partner_names)
        #self.user["partner_names"].sort()
        self.user["partner_names"] = user_chosen["company_names"].strip().split(',')
        
        self.user["object"] = random.sample(self.objects,1)[0]
        self.user["intent"] = random.sample(self.intents,1)[0]
        self.user["domain_description"] = "search_note_memory_network"
        
        
        # creating the assosiations
        self.partner_object = dict()
        self.object_partner = dict()
        self.user["note:associated_partner"] = user_chosen["note:associated_partner"].strip().split(',')
        for note_associated_partner in self.user["note:associated_partner"] :
            note, associated_partner = note_associated_partner.split(":")
            
            if associated_partner not in self.partner_object.keys() :
                list_of_objects = list()
            else :
                list_of_objects = self.partner_object[associated_partner]
                
            if note not in self.object_partner.keys() :
                list_of_partners = list()
            else :
                list_of_partners = self.object_partner[note]
                    
            list_of_objects.append(note)
            self.partner_object[associated_partner] = list_of_objects
            
            list_of_partners.append(associated_partner)
            self.object_partner[note] = list_of_partners
            
            
        self.object_amount_dict = dict()
        self.user["note:amount"] = user_chosen["note:amount"].strip().split(',')
        for note_amount in self.user["note:amount"] :
            note, amount = note_amount.split(":")
            self.object_amount_dict[note] = amount
        
        self.object_date_dict = dict()
        self.user["note:date"] = user_chosen["note:date"].strip().split(',')
        for note_date in self.user["note:date"] :
            note, date = note_date.split(":")
            self.object_date_dict[note] = date
        
        #self.partner_object = dict()
        #for partner in self.user["partner_names"] :
        #    number_of_objects_associated = random.randint(1,len(self.objects))
        #    self.partner_object[partner] = random.sample(self.objects,number_of_objects_associated)
            
        self.user["note:flow"] = user_chosen["note:flow"].strip().split(',')
        #print(self.user["note:flow"])
        
        credited_list = list()
        accounted_list = list()
        self.intent_object = {'credited' : credited_list,
                              'accounted' : accounted_list}
        
        for note_flow in self.user["note:flow"] :
            note, flow = note_flow.split(':')
            if flow not in self.intent_object.keys() :
                list_of_objects = list()
            else :
                list_of_objects = self.intent_object[flow]
                
            list_of_objects.append(note)
            self.intent_object[flow] = list_of_objects
            
        #print("intent object")
        #print(self.intent_object)
            
            
        #for intent in self.intents :
        #    number_of_objects_associated = random.randint(1,len(self.objects))
        #    list_of_objects = random.sample(self.objects,number_of_objects_associated)
        #    self.intent_object[intent] = list_of_objects
            #print("intent : == > {}, list of objects == > {}".format(intent,list_of_objects))
        
        
                
        
    
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
        pattern_to_give = list()
        
        if bot_action.get_description() == "API_CALL" :
            
            actual_actor = "API"
            actual_action = None
            
            accept_key = "search_note_success"
            accept_message = self.templates[accept_key][0]
            
            note_amount = self.object_amount_dict[self.user["object"]]
            note_date = self.object_date_dict[self.user["object"]]
            
            values_to_give = {"note_amount" : note_amount, "note_date" : note_date}
            
            reject_key = "search_note_failed"
            reject_message = self.templates[reject_key][0]
            
            #accept_message = "api_response:search_note_api, api_result:success"
            #reject_message = "api_response:search_note_api, api_result:failed"
        
        elif bot_action.get_description() == "CHANGE_OBJECT" :
            
            new_object = random.sample(self.objects,1)[0]
            while new_object == self.user["object"] :
                new_object = random.sample(self.objects,1)[0]
                
            self.user["object"] = new_object
            values_to_give["object"] = new_object
            
            if self.state_track["CHANGE_OBJECT"] > 2 :
                self.override = True
                new_object = random.sample(self.object_partner.keys(),1)[0]
                self.user["object"] = new_object
                
            actual_actor = "User"
            actual_action = None
            
            accept_key = "change_object_accept"
            accept_message = self.templates[accept_key]
            
            reject_key = "change_object_reject"
            reject_message = self.templates[reject_key]
            
            #accept_message = "accept"
            #reject_message = "reject"
            
            if self.turn_compression :
                
                accept_key = "change_object_accept_turn_compression"
                accept_message = self.templates[accept_key]
                
                #accept_message = "accept use {}".format(new_object)
                pattern_to_give.append("turn_compression")
                
            values_to_give = {"object" : new_object}
            self.state_track["CHANGE_OBJECT"] += 1
        
        
        elif bot_action.get_description() == "CHANGE_PARTNER_NAME" :
            
            
            new_partner_name = random.sample(self.partner_names,1)[0]
            
            while new_partner_name == self.user["partner_name"] :
                new_partner_name = random.sample(self.partner_names,1)[0]
                
            self.user["partner_name"] = new_partner_name
            if self.state_track["CHANGE_PARTNER_NAME"] > 2 :
                self.override = True
                new_partner_name = random.sample(self.user["partner_names"],1)[0]
                self.user["partner_name"] = new_partner_name
            
            actual_actor = "User"
            
            accept_key = "change_partner_name_accept"
            accept_message = self.templates[accept_key]
            
            reject_key = "change_partner_name_reject"
            reject_message = self.templates[reject_key]
            
            #accept_message = "accept"
            #reject_message = "reject"
            
            if self.turn_compression :
                accept_key = "change_partner_name_accept_turn_compression"
                accept_message = self.templates[accept_key][0]
                
                #aceept_message = "accept use {}".format(new_partner_name)
                pattern_to_give.append("turn_compression")
                
            values_to_give["partner_name"] = new_partner_name
            self.state_track["CHANGE_PARTNER_NAME"] += 1
        
        else :
            actual_actor = "User"
            
            accept_key = "general_accept"
            accept_message = self.templates[accept_key]
            
            reject_key = "general_reject"
            reject_message = self.templates[reject_key]
            
            #accept_message = "accept"
            #reject_message = "reject"
            
        toss = random.randint(0,100)
        if toss > 10 or self.override :
            self.override = False
            user_action = Action(actor=actual_actor,
                                 action=actual_action,
                                 slots=None,
                                 values=values_to_give,
                                 message=accept_message,
                                 description="ACCEPT_REQUEST",
                                 templates=self.templates,
                                 pattern_marker=pattern_to_give)
        else :
            user_action = Action(actor=actual_actor,
                                 action=actual_action,
                                 slots=None,
                                 values=values_to_give,
                                 message=reject_message,
                                 description="REJECT_REQUEST",
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
                                             templates=self.templates)
                        
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
                    pattern_to_give = list()
                    number_of_slots = random.randint(1,len(self.slots))
                    slots_to_inform = random.sample(self.slots,number_of_slots)
                    
                    for slot in slots_to_inform :
                        self.remove_slot(slot)
                        
                    all_slots = ["intent","domain_description"] + self.sort_my_slots(slots_to_inform)
                    
                    values_to_inform = dict()
                    
                    for slot in all_slots :
                        values_to_inform[slot] = self.user[slot]
                        
                    if self.new_api :
                        pattern_to_give.append("new_api")
                        all_slots.append("partner_name")
                        given_partner_name = random.sample(self.partner_names,1)[0]
                        values_to_inform["partner_name"] = given_partner_name
                        
                    
                    user_action = Action(actor="User",
                                         action="inform",
                                         slots=all_slots,
                                         values=values_to_inform,
                                         message="Providing intent",
                                         templates=self.templates)
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
        if bot_action.get_description() == "API_OBJECT_CHECK" :
            
            if self.user["object"] in self.intent_object[self.user["intent"]] :
                
                if self.user["object"] in self.object_partner.keys() :
                    selected_partner_name = self.object_partner[self.user["object"]]
                    
                    key = "check_object_success"
                    user_message = self.templates[key][0]
                    user_message = user_message.format(selected_partner_name)
                    
                    user_action = Action(actor="API",
                                         action=None,
                                         slots=["partner_name"],
                                         values={"partner_name" : selected_partner_name},
                                         #message="api_response:check_object_api, api_result:success, message:'partner_name:{}'".format(selected_partner_name),
                                         message=user_message,
                                         templates=self.templates)
                else :
                    key = "check_object_failed_note_not_exists"
                    user_message = self.templates[key][0]
                    
                    user_action = Action(actor="API",
                                         action=None,
                                         slots=None,
                                         values=None,
                                         #message="api_response:check_object_api, api_result:failed, message:'note doesnt exists'",
                                         message=user_message,
                                         description="NOTE_NOT_EXIST",
                                         templates=self.templates)
                
            else :
                key = "check_object_failed_note_cant_perform"
                user_message = self.templates[key][0]
                
                user_action = Action(actor="API",
                                     action=None,
                                     slots=None,
                                     values=None,
                                     #message="api_response:check_object_api, api_result:failed, message:'{} cannot perform {}'".format(self.user["object"],self.user["intent"]),
                                     message=user_message,
                                     description="NOTE_CANNOT_PERFORM_INTENT",
                                     templates=self.templates)
        
        # if the API action askes for a initial state check
        elif bot_action.get_description() == "API_INITIAL_SLOT_CHECK" :
            
            # if the flag becomes true at the end of this segment then it means that one or more than one slots are incorrect
            flag = False
            error_message = list()
            order_of_slots = list()
            message_to_convey = str()
            # if user account is given in the initial slots then check if it is appropriate
            if "object" in bot_action.get_slots() and "partner_name" not in bot_action.get_slots() :
                
                if self.user["object"] not in self.intent_object[self.user["intent"]] :
                    message_to_convey = "Cannot perform that action"
                    self.priority_states.append("end_call")
                    
                    key = "end_call_object_not_associated_with_note"
                    bot_message = self.templates[key][0]
                    
                    self.priority_actions["end_call"] = Action(actor="Bot",
                                                                action="end_call",
                                                                slots=None,
                                                                values=None,
                                                                #message="Cannot perform that action",
                                                               message=bot_message,
                                                                templates=self.templates)
                elif self.user["object"] not in self.object_partner.keys() :
                    message_to_convey = "Note has no partner name"
                    self.priority_states.append("partner_name")
                    self.priority_actions["partner_name"] = Action(actor="Bot",
                                                                   action="request",
                                                                   slots=["partner_name"],
                                                                   values=None,
                                                                   #message="requesting for partner name",
                                                                   message=bot_message,
                                                                   templates=self.templates)
                    
            elif "partner_name" in bot_action.get_slots() and "object" in bot_action.get_slots() :
                
                if self.user["object"] not in self.object_partner.keys() :
                    message_to_convey = "I am sorry we have no {} in our records".format(self.user["object"])
                    self.priority_states.append("end_call")
                    
                    key = "end_call_object_not_associated_with_partner_name"
                    bot_message = self.templates[key][0]
                    
                    self.priority_actions["end_call"] = Action(actor="Bot",
                                                                action="end_call",
                                                                slots=None,
                                                                values=None,
                                                                #message="Cannot perform that action",
                                                               message=bot_message,
                                                                templates=self.templates)
                elif self.user["partner_name"] not in self.object_partner[self.user["object"]] :
                    message_to_convey = "We have no {} from {}".format(self.user["object"],self.user["partner_name"])
                    self.priority_states.append("end_call")
                    
                    key = "end_call_partner_name_not_associated_with_object"
                    bot_message = self.templates[key][0]
                    
                    self.priority_actions["end_call"] = Action(actor="Bot",
                                                               action="end_call",
                                                               slots=None,
                                                               values=None,
                                                               #message="Can't perform that action",
                                                               message=bot_message,
                                                               templates=self.templates)
                    
                    
                
            
            # if destination name is given in the initial slots then check if it is appropriate
            
            # if both user_account and amount are present then check if the amount satisfies the criteria
                
            
            # if self.priority_states is no empty then one or more than one value is incorrect then send appropriate error message
            if self.priority_states :
                
                key = "check_initial_slot_failed"
                user_message = self.templates[key][0]
                user_message = user_message.format(message_to_convey)
                
                user_action = Action(actor="API",
                                     action=None,
                                     slots=self.priority_states,
                                     values=self.priority_actions,
                                     #message="api_response:initial_slot_check_api, api_result:failed, message:'{}'".format(message_to_convey),
                                     message=user_message,
                                     templates=self.templates)
            
            # if everything is okay then send the correct message
            else :
                selected_partner_name = self.object_partner[self.user["object"]][0]
                self.user["partner_name"] = selected_partner_name
                
                key = "check_initial_slot_success"
                user_message = self.templates[key][0]
                user_message = user_message.format(selected_partner_name)
                
                user_action = Action(actor="API",
                                     action=None,
                                     slots=["partner_name"],
                                     values={"partner_name" : selected_partner_name},
                                     #message="api_response:initial_slot_check_api, api_result:success, message:'partner_name:{}'".format(selected_partner_name),
                                     message=user_message,
                                     templates=self.templates)
        
        # if the requested action is an account check
        elif bot_action.get_description() == "API_PARTNER_NAME_CHECK" :
            if "partner_name" in self.user["partner_names"] :
                
                key = "check_partner_name_success"
                user_message = self.templates[key][0]
                
                user_action = Action(actor="API",
                                     action="api_response",
                                     slots=["objects"],
                                     values={"objects" : self.partner_object[self.user["partner_name"]]},
                                     message=user_message,
                                     templates=self.templates)
            else :
                
                key = "check_partner_name_failed"
                user_message = self.templates[key][0]
                user_message = user_message.format(self.user["partner_name"])
                
                user_action = Action(actor="API",
                                     action=None,
                                     slots=None,
                                     values=None,
                                     #message="api_response:check_partner_name, api_result:failed, message:'{} is not list of contacts, would you like to change partner name'".format(self.user["partner_name"]),
                                     message=user_message,
                                     templates=self.templates)
        
        # if the requested action is destination name check
        else :
            user_action = self.perform_random_action(bot_action)
        
        return user_action            