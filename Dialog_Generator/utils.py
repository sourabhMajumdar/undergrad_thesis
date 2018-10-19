import pandas as pd
import random
import os
import copy
def make_templates(file_name="templates_for_dialogue_self_play.xlsx",sheet_name="MAKE_TRANSACTION",previous_dictionary_train=None,previous_dictionary_val=None) :
    if previous_dictionary_train == None or previous_dictionary_val == None:
        
        template_dictionary_train = dict()
        template_dictionary_val = dict()
    else :
        template_dictionary_train = previous_dictionary_train
        template_dictionary_val = previous_dictionary_val
    
    df = pd.read_excel(file_name,sheet_name)
    for index,row in df.iterrows() :
        if not pd.isnull(row["LABEL"]) :
            if row["LABEL"] not in template_dictionary_train.keys() :
                template_sentences_train = list()
                template_sentences_val = list()
            else :
                template_sentences_train = template_dictionary_train[row["LABEL"]]
                template_sentences_val = template_dictionary_val[row["LABEL"]]
            
                
            if not pd.isnull(row["TEXT-EN (Marco)"]) :
                template_sentences_train.append(row["TEXT-EN (Marco)"])
            if not pd.isnull(row["TEXT-EN (Sourabh)"]) :
                template_sentences_val.append(row["TEXT-EN (Sourabh)"])
            
            template_dictionary_train[row["LABEL"]] = template_sentences_train
            template_dictionary_val[row["LABEL"]] = template_sentences_val
    
    return template_dictionary_train , template_dictionary_val
    
class Action(object) :
    def __init__(self,actor=None,action=None,slots=None,values=None,message=None,description=None,templates=None) :
        
        self.actor = actor # who performed the action
        self.action = action # what action was performed
        self.slots = slots # what slot was dealt with 
        self.values = values # what was the value with this slot
        self.message = message # Any particular message related to the action
        self.description = description # This contain the description of the action and is never intended to be shown or appear in the actual conversation
        self.templates = templates
        self.template = None
        
        
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
    
    def set_templates(self,new_templates=None) :
        
        if new_templates :
            self.templates = new_templates
            
        dictionary_key = self.action
        
        if self.slots :
            if len(self.slots) > 0 :
                for slot in self.slots :
                    
                    if slot == "intent" :
                        
                        if self.actor == "User" :
                            
                            dictionary_key += "-" + slot + "_" + self.values["intent"]
                            
                        else :
                            
                            dictionary_key += "-" + slot
                    else :
                        
                        dictionary_key += "-" + slot
        
        
        # if the dictionary_key exists in the template dictionary then get a template other wise set template = the action message
        if self.templates and dictionary_key in self.templates.keys() :
            self.template = random.sample(self.templates[dictionary_key],1)[0]
        else :
            self.template = self.message
        
    # when called , construct a dialog from the slots and give it to the user
    def get_dialog(self,with_actor=True,templates=None) :

        
        if templates :
            self.set_templates(new_templates=templates)
        else :
            self.set_templates()
            
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
            
            sentence = self.action + " " + self.message
        if with_actor :
            return self.actor + " : " + sentence
        else :
            return sentence

def create_raw_data(file_directory="../data/",file_name="data.txt",dialogs=None) :
    
    if not os.path.exists(file_directory) :
        os.makedirs(file_directory)
    
    file_handle = open(os.path.join(file_directory,file_name),"w")
    
    for dialog in dialogs :
        for action in dialog :
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
            file_handle.write("{} {}\t{}\n".format(str(count),dialog[i].get_dialog(with_actor=False),dialog[i+1].get_dialog(with_actor=False)))
            count += 1
        file_handle.write("\n")
    file_handle.close()

def create_candidates(file_directory="../data/",file_name="data.txt",dialogs=None) :
    candidate_set = set()
    if not os.path.exists(file_directory) :
        os.makedirs(file_directory)
        
    for dialog in dialogs :
        for action in dialog :
            if action.get_actor() == "Bot" or action.get_actor() == "API" :
                candidate_set.add(action.get_dialog(with_actor=False))
    file_handle = open(os.path.join(file_directory,file_name),"w")
    for candidate in candidate_set :
        file_handle.write("1 {}\n".format(candidate))
    file_handle.close()

def create_dialogs(User,Bot,number_of_dialogs,dialog_templates_train=None,dialog_templates_val=None) :
    
    dialogs_train = list()
    dialogs_val = list()
    
    for i in range(number_of_dialogs) :
        
        dialog_train = list()
        dialog_val = list()

        user = User(templates=dialog_templates_train)
        bot = Bot(templates=dialog_templates_train)

        user_action_train = Action(actor="User",
                             action=None,
                             slots=None,
                             values=None,
                             message="<SILENCE>",
                             templates=dialog_templates_train)
        

        bot_action_train = Action(actor="Bot",
                            action="request",
                            slots=["intent"],
                            values=None,
                            message="Gettinng intent",
                            templates=dialog_templates_train)
        
        
        
        dialog_train.append(user_action_train)
        dialog_train.append(bot_action_train)
        
        user_action_val = copy.deepcopy(user_action_train)
        bot_action_val = copy.deepcopy(bot_action_train)
        
        user_action_val.set_templates(new_templates=dialog_templates_val)
        bot_action_val.set_templates(new_templates=dialog_templates_val)
        
        dialog_val.append(user_action_val)
        dialog_val.append(bot_action_val)
        
        latest_action = None
        
        while latest_action != "end_call" :
            
            user_action_train = user.speak(bot_action_train)
            
            #print("user_action {}, user_message {} user_description {}".format(user_action_train.get_action(),user_action_train.get_message(),user_action_train.get_description()))
            bot_action_train = bot.speak(user_action_train)
            #print("bot_action {}, bot_message {} bot_description {}".format(bot_action_train.get_action(),bot_action_train.get_message(),bot_action_train.get_description()))
            latest_action = bot_action_train.get_action()
            
            user_action_val = copy.deepcopy(user_action_train)
            bot_action_val = copy.deepcopy(bot_action_train)
        
            user_action_val.set_templates(new_templates=dialog_templates_val)
            bot_action_val.set_templates(new_templates=dialog_templates_val)
            #print("latest action is {}".format(latest_action))
            dialog_train.append(user_action_train)
            dialog_train.append(bot_action_train)
            
            dialog_val.append(user_action_val)
            dialog_val.append(bot_action_val)
            #print("User:{} Bot:{}".format(user_action.get_message(),bot_action.get_message()))
        
        dialogs_train.append(dialog_train)
        dialogs_val.append(dialog_val)
    
    return dialogs_train , dialogs_val

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
                                    message="mem_call:{}".format(action.get_values()["intent"]))
                start_dialog.append(mem_action)
                break
        start_dialogs.append(start_dialog)
    return start_dialogs

