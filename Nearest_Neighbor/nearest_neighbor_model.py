import os
import numpy as np
from tqdm import tqdm

class Nearest_Neighbor_Model(object):
	"""docstring for Nearest_Neighbor"""
	def __init__(self,data_dir,model_dir,description,mult_oop,pipeline_testing):
		self.data_dir = data_dir
		self.model_dir = model_dir
		self.description = description
		self.mult_oop = mult_oop
		self.pipeline_testing = pipeline_testing

		self.test_file = None
		if self.mult_oop :
			self.test_file = self.test_file_multiple_oop
		else :
			self.test_file = self.test_file_one_oop

	def train(self):
		train_file = os.path.join(self.data_dir,'train_data.txt')
		f_handle = open(train_file)
		self.nearest_neighbor = dict()
		all_lines = f_handle.readlines()
		for line in tqdm(all_lines) :
			raw_line = line.strip().split(' ',1)
			if raw_line and len(raw_line) > 1:
				#print(raw_line[1])
				utterances = raw_line[1].split('\t')
				user_utterance = utterances[0]
				bot_utterance = utterances[1]

				if user_utterance not in self.nearest_neighbor.keys() :
					response_dict = dict()
					response_dict[bot_utterance] = 1
					self.nearest_neighbor[user_utterance] = response_dict
				else :
					response_dict = self.nearest_neighbor[user_utterance]
					if bot_utterance not in response_dict.keys() :
						response_dict[bot_utterance] = 1
					else :
						response_dict[bot_utterance] += 1
		f_handle.close()

	def predict_and_converse(self,context,user_utterance,nid,bot_utterance) :
		context = '{}\n{}'.format(context,user_utterance)
		utt = user_utterance
		btt = str()
		print(utt)
		if utt in self.nearest_neighbor.keys() :
			responses = self.nearest_neighbor[utt]
			highest_value = -1
			temp_resp = str()
			for utterance,value in responses.items() :
				if value > highest_value :
					highest_value = value
					temp_resp = utterance
			btt = temp_resp
		return btt, context, nid

	def evaluate_this_line(self,given_line,test_case) :
		if test_case == None :
			return True
		else :
			raw_words = test_case.split('_')
			if 'oot' in raw_words :
				raw_words.remove('oot')
				out_of_pattern = '_'.join(raw_words)
			if out_of_pattern in given_line :
				return True
			else :
				return False

	def test_file_multiple_oop(self,test_case) :
		print(" Testing Model with description : {}".format(self.get_description()))
		story = list()
		nid = 1
		network_converse = self.predict_and_converse
		count_sentence = 0
		correct_sentence = 0
		correct_dialog = 0
		count_dialog = 0
		correct_intent = 0
		correct_dialog_track = True

		test_directory = os.path.join(self.data_dir,'test/')

		if test_case == None :
			test_file_name = 'test_data.txt'
		else :
			test_file_name = 'test_data_{}.txt'.format(test_case)

		file_name = os.path.join(test_directory,test_file_name)
		f_handle = open(file_name)
		if self.pipeline_testing :
			all_list_of_lines = f_handle.readlines()
			list_of_lines = all_list_of_lines[:100]
		else :
			list_of_lines = f_handle.readlines()

		for line in tqdm(list_of_lines) :
			evaluate_flag = self.evaluate_this_line(line,test_case)
			line = line.strip()

			if not line :
				story = list()
				nid = 1
				if correct_dialog_track :
					correct_dialog += 1
				correct_dialog_track = True
				count_dialog += 1
			else :
				set_of_sentence_tokens = line.split(' ',1)
				raw_sentence = set_of_sentence_tokens[1]
				raw_line = raw_sentence.strip()
				if evaluate_flag :
					count_sentence += 1
				utterances = raw_line.split('\t')
				user_utterance = utterances[0]
				bot_utterance = utterances[1]
				bot_response, story, nid = network_converse(story,user_utterance,nid,bot_utterance)
				if bot_response.strip() == bot_utterance :
					if evaluate_flag :
						if nid == 2 :
							correct_intent += 1
						correct_sentence += 1
				else :
					correct_dialog_track = False

		per_response_accuracy = 0.0
		per_dialog_accuracy = 0.0
		per_intent_accuracy = 0.0
		if count_sentence == 0:
			per_resonse_accuracy = 0.0
		else :
			per_response_accuracy = float(correct_sentence)/count_sentence

		if count_dialog == 0:
			per_dialog_accuracy = 0.0
			per_intent_accuracy = 0.0
		else : 
			per_dialog_accuracy = float(correct_dialog)/count_dialog
			per_intent_accuracy = float(correct_intent)/count_dialog

		print("{} percentage of correct sentences : {}".format(file_name,per_response_accuracy))
		print("{} percentage of correct dialogs : {}".format(file_name,per_dialog_accuracy))
		print("{} percentage of correct intents : {}".format(file_name,per_intent_accuracy))

		return per_response_accuracy, per_dialog_accuracy, per_intent_accuracy

	def test_file_one_oop(self,test_case) :
		print(" Testing Model with description : {}".format(self.get_description()))

		story = list()
		nid = 1
		network_converse = self.predict_and_converse
		count_sentence = 0
		correct_sentence = 0
		correct_dialog = 0
		count_dialog = 0
		correct_intent = 0
		correct_dialog_track = True

		test_directory = os.path.join(self.data_dir,'test/')

		if test_case == None :
			test_file_name = 'test_data.txt'
		else :
			test_file_name = 'test_data_{}.txt'.format(test_case)

		file_name = os.path.join(test_directory,test_file_name)

		f_handle = open(file_name)
		if self.pipeline_testing :
			all_list_of_lines = f_handle.readlines()
			list_of_lines = all_list_of_lines[:100]
		else :
			list_of_lines = f_handle.readlines()

		dialog_done  = False

		for line in tqdm(list_of_lines) :
			evaluate_flag = self.evaluate_this_line(line,test_case)
			line = line.strip()

			if not line :
				dialog_done = False
				story = list()
				nid = 1
				if correct_dialog_track :
					correct_dialog += 1
				correct_dialog_track = True
				count_dialog += 1
			else :
				set_of_sentence_tokens = line.split(' ',1)
				raw_sentence = set_of_sentence_tokens[1]
				raw_line = raw_sentence.strip()
				if evaluate_flag and not dialog_done:
					count_sentence += 1
				#print("Raw line is : {}".format(raw_line))
				utterances = raw_line.split('\t')
				user_utterance = utterances[0]
				bot_utterance = utterances[1]
				bot_response, story, nid = network_converse(story,user_utterance,nid,bot_utterance)
				if bot_response.strip() == bot_utterance :
					if evaluate_flag and not dialog_done :
						if nid == 2 :
							correct_intent += 1
						correct_sentence += 1
					else :
						correct_dialog_track = False
			if evaluate_flag :
				dialog_done = True

		per_response_accuracy = 0.0
		per_dialog_accuracy = 0.0
		per_intent_accuracy = 0.0

		if count_sentence == 0:
			per_resonse_accuracy = 0.0
		else :
			per_response_accuracy = float(correct_sentence)/count_sentence

		if count_dialog == 0:
			per_dialog_accuracy = 0.0
			per_intent_accuracy = 0.0
		else : 
			per_dialog_accuracy = float(correct_dialog)/count_dialog
			per_intent_accuracy = float(correct_intent)/count_dialog

		print("{} percentage of correct sentences : {}".format(file_name,per_response_accuracy))
		print("{} percentage of correct dialogs : {}".format(file_name,per_dialog_accuracy))
		print("{} percentage of correct intents : {}".format(file_name,per_intent_accuracy))

		return per_response_accuracy, per_dialog_accuracy, per_intent_accuracy

	def dialog_analysis(self,file_directory="Analysis_Directory/",file_name="Analysis.txt") :
		print(" Analysing Dialogs for Model description : {}".format(self.get_description()))

		if not os.path.exists(file_directory) :
			os.makedirs(file_directory)

		file_handle = open(os.path.join(file_directory,file_name),'w')
		test_directory = self.test_directory
		for file_covered in glob.glob(test_directory + 'test_data*.txt') :
			print("file opened : == > {}".format(file_covered))

			story = list()
			analysis_story = list()
			nid = 1
			network_converse = self.predict_and_converse
			count_sentence = 0
			correct_sentence = 0
			correct_dialog = 0
			count_dialog = 0
			error_count = 0
			api_error = 0
			api_bleu_score = 0.0
			non_api_error = 0
			correct_dialog_track = True
			f_handle = open(file_covered)

			if self.pipeline_testing :
				all_list_of_lines = f_handle.readlines()
				list_of_lines = all_list_of_lines[:100]
			else :
				list_of_lines = f_handle.readlines()

			for line in tqdm(list_of_lines) :
				raw_line = line[2:].strip()
				if not raw_line :
					story = list()
					nid = 1
					analysis_story = list()
					if correct_dialog_track :
						correct_dialog += 1
					correct_dialog_track = True
					count_dialog += 1
				else :
					count_sentence += 1
					utterances = raw_line.split('\t')
					user_utterance = utterances[0]
					bot_utterance = utterances[1]
					bot_response, story, nid = network_converse(story,user_utterance,nid,bot_utterance)
					if bot_response.strip() != bot_utterance :
						error_count += 1
						if "api_call" in bot_utterance and "api_call" in bot_response :
							api_error += 1
							tok_bot_utterance = tokenize(bot_utterance)
							tok_bot_response = tokenize(bot_response)
							api_bleu_score += sentence_bleu([tok_bot_utterance],tok_bot_response)
						else :
							non_api_error +=1
						correct_dialog_track = False

						file_handle.write("Story is :\n")
						for l in analysis_story :
							file_handle.write("{}\n".format(l))

						file_handle.write("\n")
						file_handle.write("User Utterance : {}\n".format(user_utterance))
						file_handle.write("Bot Utterance (expected) : {}\n".format(bot_utterance))
						file_handle.write("Bot Utterance (predicted) : {}\n\n".format(bot_response))

					analysis_story.append("User >> {} || Bot >> {} \n".format(user_utterance,bot_utterance))

			if api_error == 0 :
				print("Congrat's no api_error")
			else :
				print("Number of api error's = {}/{}, Avg api_bleu score = {}".format(str(api_error),str(error_count),str(float(api_bleu_score)/api_error)))
				print("Number of non api error's = {}/{}".format(str(non_api_error),str(error_count)))

		file_handle.close()

	def get_description(self) :
		return self.description
