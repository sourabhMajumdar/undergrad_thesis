import numpy as np # no use until now
import random # used for random sampling of values where applicable
import math # no use untill now
import pandas as pd # to read the excel file 
import os # to carry os operations
import copy # this is used to copy the class object
import glob
import copy


def make_templates(sheet_name="MAKE_TRANSACTION",previous_dictionary=None) :
    if previous_dictionary == None :
        template_dictionary = dict()
    else :
        template_dictionary = previous_dictionary
    
    for file_name in glob.glob('template_folder/*.xlsx') :
        df = pd.read_excel(file_name,sheet_name)
        for index,row in df.iterrows() :
            if not pd.isnull(row["LABEL"]) :
                if row["LABEL"] not in template_dictionary.keys() :
                    template_sentences = set()
                else :
                    template_sentences = template_dictionary[row["LABEL"]]
            
                
                if not pd.isnull(row["TEXT"]) :
                    template_sentences.add(row["TEXT"])
            
                template_dictionary[row["LABEL"]] = template_sentences
        del df
    
    # define all the dictionaries
    template_dictionary_train = dict()
    template_dictionary_val = dict()
    template_dictionary_test = dict()
    template_dictionary_test_oot = dict()
    
    final_template_dictionary = dict()
    
    for key,value in template_dictionary.items() :
        list_of_templates = list(value)
        
        if len(list_of_templates) < 3 :
            
            list_of_templates_train = list_of_templates
            list_of_templates_val = list_of_templates
            list_of_templates_test = list_of_templates
        else :
            
            list_of_templates_train = list_of_templates[0:int(len(list_of_templates)/3)]
            list_of_templates_val = list_of_templates[int(len(list_of_templates)/3):int(2*len(list_of_templates)/3)]
            
            list_of_templates_from_train = random.sample(list_of_templates,max(len(list_of_templates_train)//2,1))
            list_of_templates_from_val = random.sample(list_of_templates,max(len(list_of_templates_val)//2,1))
            
            list_of_templates_test = list()
            list_of_templates_test.extend(list_of_templates_from_train)
            list_of_templates_test.extend(list_of_templates_from_val)
            
            list_of_templates_test_oot = list_of_templates[int(2*len(list_of_templates)/3):int(len(list_of_templates))]
        
        
        
        template_dictionary_train[key] = list_of_templates_train
        template_dictionary_val[key] = list_of_templates_val
        template_dictionary_test[key] = list_of_templates_test
        template_dictionary_test_oot[key] = list_of_templates_test
    
    final_template_dictionary["train"] = template_dictionary_train
    final_template_dictionary["val"] = template_dictionary_val
    final_template_dictionary["test"] = template_dictionary_test
    final_template_dictionary["test_oot"] = template_dictionary_test_oot
    
    return final_template_dictionary
    
    
class Action(object) :
    def __init__(self,
                 actor=None,
                 action=None,
                 slots=None,
                 values=None,
                 message=None,
                 description=None,
                 slot_concerned=None,
                 templates=None,
                 pattern_marker=None) :
        
        self.actor = actor # who performed the action
        self.action = action # what action was performed
        self.slots = slots # what slot was dealt with 
        self.values = values # what was the value with this slot
        self.message = message # Any particular message related to the action
        self.description = description # This contain the description of the action and is never intended to be shown or appear in the actual conversation
        self.templates = templates
        self.template = None
        self.dictionary_key_found = False
        self.slot_concerned = slot_concerned
        self.pattern_marker = pattern_marker
        
        self.set_templates(self.templates)
        
        
    # standard actions to perform
    def get_actor(self) :
        return self.actor
    
    def get_action(self) :
        return self.action
    
    def get_slots(self) :
        return self.slots
    
    def get_values(self) :
        return self.values
    
    def get_message(self) :
        return self.message
    
    def get_description(self) :
        return self.description
    def template_found(self) :
        return self.dictionary_key_found
    
    def get_pattern_marker(self) :
        return self.pattern_marker
    
    def set_templates(self,new_templates=None) :
        
        if new_templates :
            #print("templates changed")
            self.templates = new_templates
        
        if self.action :
            dictionary_key = self.action
        else :
            dictionary_key = str()
        
        if self.slots :
            if len(self.slots) > 0 :
                for slot in self.slots :
                    
                    if slot == "intent" :
                        
                        if self.actor == "User" :
                            
                            dictionary_key += "-" + slot + "_" + self.values["intent"]
                            
                        else :
                            
                            dictionary_key += "-" + slot
                            
                    elif slot == "domain_description" :
                        continue
                        
                    else :
                        
                        dictionary_key += "-" + slot
        
        # if the dictionary_key exists in the template dictionary then get a template other wise set template = the action message
        if self.templates and dictionary_key in self.templates.keys() :
            self.template = random.sample(self.templates[dictionary_key],1)[0]
            self.dictionary_key_found = True
        else :
            self.template = self.message
        
    # when called , construct a dialog from the slots and give it to the user
    def get_dialog(self,with_actor=True,templates=None) :

        
        if templates :
            self.set_templates(new_templates=templates)
        
            
        # first split the template into a list of words
        words = self.template.strip().split()
        sentence = None
        
        # only go to this loop if the actor is a User or Bot , in case of API go to else statement which will just append action and message
        if self.actor == "User" or self.actor == "Bot" :
            if self.values :
                for slot,value in self.values.items() :
                    search_slot = "{" + slot + "}"
                    if search_slot in words :
                        slot_index = words.index(search_slot)
                        words.insert(slot_index,str(value))
                
                        words.pop(slot_index+1)
                    sentence = " ".join(words)
                
            # if it's a request action then get a template requesting the slots
            elif self.action == "request" :
                
                sentence = self.template
            
            # if it's a end_call then show the action and the message given
            elif self.action == "end_call" :
                
                sentence = self.action + " " + self.message
            
            else :
                
                sentence = self.message
        
        else:
            if self.action :
                sentence = self.action + " " + self.message
            else :
                sentence = self.message
        if with_actor :
            return self.actor + " : " + sentence
        else :
            return sentence

def create_dialogs(User,
                   Bot,
                   number_of_dialogs,
                   dialog_templates=None,
                   list_of_user_profiles=None,
                   user_values=None,
                   turn_compression=False,
                   new_api=False,
                   re_order=False,
                   another_slot=False,
                   audit_more=False) :
    
    dialogs_train = list()
    dialogs_val = list()
    dialogs_test = list()
    dialogs_test_oot = list()
    
    final_dialogs = dict()
    
    for i in range(number_of_dialogs) :
        
        dialog_train = list()
        dialog_val = list()
        dialog_test = list()
        dialog_test_oot = list()

        user = User(templates=dialog_templates["train"],
                    list_of_user_profiles=list_of_user_profiles,
                    user_values=user_values,
                    turn_compression=turn_compression,
                    new_api=new_api,
                    another_slot=another_slot,
                    audit_more=audit_more)
        
        bot = Bot(templates=dialog_templates["train"],
                  turn_compression=turn_compression,
                  re_order=re_order,
                  audit_more=audit_more)

        user_action_train = Action(actor="User",
                             action=None,
                             slots=None,
                             values=None,
                             message="<SILENCE>",
                             templates=dialog_templates["train"])
        

        bot_action_train = Action(actor="Bot",
                            action="request",
                            slots=["intent"],
                            values=None,
                            message="Gettinng intent",
                            templates=dialog_templates["train"])
        
        
        
        dialog_train.append(user_action_train)
        dialog_train.append(bot_action_train)
        
        # creating validation actions
        user_action_val = copy.deepcopy(user_action_train)
        bot_action_val = copy.deepcopy(bot_action_train)
        
        
        
        user_action_val.set_templates(new_templates=dialog_templates["val"])
        bot_action_val.set_templates(new_templates=dialog_templates["val"])
        
        
        dialog_val.append(user_action_val)
        dialog_val.append(bot_action_val)
        
        # creating test actions
        user_action_test = copy.deepcopy(user_action_train)
        bot_action_test = copy.deepcopy(bot_action_train)
        
        
        user_action_test.set_templates(new_templates=dialog_templates["test"])
        bot_action_test.set_templates(new_templates=dialog_templates["test"])
        
        dialog_test.append(user_action_test)
        dialog_test.append(bot_action_test)
        
        # creating test oot actions
        user_action_test_oot = copy.deepcopy(user_action_train)
        bot_action_test_oot = copy.deepcopy(bot_action_train)
        
        
        user_action_test_oot.set_templates(new_templates=dialog_templates["test_oot"])
        bot_action_test_oot.set_templates(new_templates=dialog_templates["test_oot"])
        
        dialog_test_oot.append(user_action_test_oot)
        dialog_test_oot.append(bot_action_test_oot)
        
        
        latest_action = None
        
        while latest_action != "end_call" :
            
            user_action_train = user.speak(bot_action_train)
            
            #print("user_action {}, user_message {} user_description {}".format(user_action_train.get_action(),user_action_train.get_message(),user_action_train.get_description()))
            bot_action_train = bot.speak(user_action_train)
            #print("bot_action {}, bot_message {} bot_description {}".format(bot_action_train.get_action(),bot_action_train.get_message(),bot_action_train.get_description()))
            latest_action = bot_action_train.get_action()
            
            # creating validation actions
            user_action_val = copy.deepcopy(user_action_train)
            bot_action_val = copy.deepcopy(bot_action_train)
            
            
            # creating test actions
            user_action_test = copy.deepcopy(user_action_train)
            bot_action_test = copy.deepcopy(bot_action_train)
            
            # creating test oot actions
            user_action_test_oot = copy.deepcopy(user_action_train)
            bot_action_test_oot = copy.deepcopy(bot_action_train)
            
            # setting validation templates
            user_action_val.set_templates(new_templates=dialog_templates["val"])
            bot_action_val.set_templates(new_templates=dialog_templates["val"])
            
            # setting test templates
            user_action_test.set_templates(new_templates=dialog_templates["test"])
            bot_action_test.set_templates(new_templates=dialog_templates["test"])
            
            # setting test oot templates
            user_action_test_oot.set_templates(new_templates=dialog_templates["test_oot"])
            bot_action_test_oot.set_templates(new_templates=dialog_templates["test_oot"])
            
            dialog_train.append(user_action_train)
            dialog_train.append(bot_action_train)
            
            dialog_val.append(user_action_val)
            dialog_val.append(bot_action_val)
            
            dialog_test.append(user_action_test)
            dialog_test.append(bot_action_test)
            
            dialog_test_oot.append(user_action_test_oot)
            dialog_test_oot.append(bot_action_test_oot)
            
            #print("User:{} Bot:{}".format(user_action.get_message(),bot_action.get_message()))
        
        dialogs_train.append(dialog_train)
        dialogs_val.append(dialog_val)
        dialogs_test.append(dialog_test)
        dialogs_test_oot.append(dialog_test_oot)
        
    final_dialogs["train"] = dialogs_train
    final_dialogs["val"] = dialogs_val
    final_dialogs["test"] = dialogs_test
    final_dialogs["test_oot"] = dialogs_test_oot
    
    return final_dialogs

def create_start_dialog(dialogs=None) :
    start_dialogs = list()
    for dialog in dialogs :
        start_dialog = list()
        for action in dialog :
            start_dialog.append(action)
            if action.get_action() == "inform" and "intent" in action.get_slots() :
                mem_action = Action(actor="Bot",
                                    action="mem_call",
                                    slots=None,
                                    values=None,
                                    message="mem_call:{}".format(action.get_values()["domain_description"]))
                start_dialog.append(mem_action)
                break
        start_dialogs.append(start_dialog)
    return start_dialogs

def create_special_dialog(dialogs=None) :
    special_dialogs = list()
    for dialog in dialogs :
        special_dialog = list()
        #print("starting new dialog")
        #print("length of dialog is : {}".format(len(dialog)))
        
        for action in dialog :
            special_dialog.append(action)
            if action.get_action() and action.get_slots() and action.get_action() == "inform" and "intent" in action.get_slots() :
                
                mem_action = Action(actor="Bot",
                                    action="mem_call",
                                    slots=None,
                                    values=None,
                                    message="mem_call:{}".format(action.get_values()["domain_description"]))
                
                special_dialog.append(mem_action)
                special_dialog.append(action)
                
        special_dialogs.append(special_dialog)
    return special_dialogs

def create_raw_data(file_directory="../data/",file_name="data.txt",dialogs=None) :
    
    if not os.path.exists(file_directory) :
        os.makedirs(file_directory)
    
    file_handle = open(os.path.join(file_directory,file_name),"w")
    
    for dialog in dialogs :
        if dialog :
            for action in dialog :
                if action :
                    file_handle.write(action.get_dialog())
                    file_handle.write("\n")
            file_handle.write("\n")
    file_handle.close()
    
def create_training_data(file_directory="../data/",file_name="data.txt",dialogs=None) :
    
    if not os.path.exists(file_directory) :
        os.makedirs(file_directory)
        
    file_handle = open(os.path.join(file_directory,file_name),"w")
    for dialog in dialogs :
        count = 1
        for i in range(0,len(dialog),2) :
            user_dialog = dialog[i]
            bot_dialog = dialog[i+1]
            
            user_pattern = user_dialog.get_pattern_marker()
            bot_pattern = bot_dialog.get_pattern_marker()
            
            if user_pattern or bot_pattern :
                list_of_pattern = list()
                if user_pattern :
                    list_of_pattern.extend(user_pattern)
                if bot_pattern :
                    list_of_pattern.extend(bot_pattern)
                    
                pattern_marked = '-'.join(list_of_pattern)
                file_handle.write("{}{} {}\t{}\n".format(str(count),pattern_marked,user_dialog.get_dialog(with_actor=False),bot_dialog.get_dialog(with_actor=False)))
            else :
                file_handle.write("{} {}\t{}\n".format(str(count),user_dialog.get_dialog(with_actor=False),bot_dialog.get_dialog(with_actor=False)))
            count += 1
        file_handle.write("\n")
    file_handle.close()
    
def create_candidates(file_directory="../data/",file_name="data.txt",dialogs=None) :
    candidate_set = set()
    if not os.path.exists(file_directory) :
        os.makedirs(file_directory)
        
    for dialog in dialogs :
        for action in dialog :
            if action.get_actor() == "Bot" :
                candidate_set.add(action.get_dialog(with_actor=False))
    file_handle = open(os.path.join(file_directory,file_name),"w")
    for candidate in candidate_set :
        file_handle.write("1 {}\n".format(candidate))
    file_handle.close()
    
def find_generic_responses(actor=None,dialogs=None,file_directory=None,file_name=None) :
    set_of_sentences = set()
    if not os.path.exists(file_directory) :
        os.makedirs(file_directory)
    
    for dialog in dialogs :
        for action in dialog :
            if action.get_actor() == actor and action.template_found() == False :
                 if "api_call" not in action.get_dialog(with_actor=False) :
                        set_of_sentences.add(action.get_dialog(with_actor=False))
    file_handle = open(os.path.join(file_directory,file_name),"w")
    for sentence in set_of_sentences :
        file_handle.write("1 {}\n".format(sentence))
    file_handle.close()