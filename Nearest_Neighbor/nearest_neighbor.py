import os
data_dir = input('Enter Data Directory :\t')
train_file = os.path.join(data_dir,'train_data.txt')
f_handle = open(train_file)
nearest_neighbor = dict()
for line in f_handle :
	print(line)
	raw_line = line[2:].lower().strip()
	if raw_line :
		utterances = raw_line.split('\t')
		user_utterance = utterances[0]
		bot_utterance = utterances[1]
		if user_utterance not in nearest_neighbor.keys() :
			response_dict = dict()
			response_dict[bot_utterance] = 1
			nearest_neighbor[user_utterance] = response_dict
		else :
			response_dict = nearest_neighbor[user_utterance]
			if bot_utterance not in response_dict.keys() :
				response_dict[bot_utterance] = 1
			else :
				response_dict[bot_utterance] += 1


f_handle.close()

def find_best_utterance(user_utterance,nearest_neighbor) :
	utt = user_utterance
	btt = None
	if utt in nearest_neighbor.keys() :
		responses = nearest_neighbor[utt]
		highest_value = -1
		temp_resp = str()
		for utterance,value in responses.items() :
			if value > highest_value :
				highest_value = value
				temp_resp = utterance
		btt = temp_resp
	return btt




t_handle = open(os.path.join(data_dir,'val_data.txt'))

count_dialog = 0
correct_dialog = 0
count_sentences = 0
correct_sentences = 0
correct_dialog_track = True
for line in t_handle :
	print(line)
	raw_line = line[2:].lower().strip()
	if not raw_line :
		count_dialog +=1
		if correct_dialog_track :
			correct_dialog += 1
		correct_dialog_track = True
	else :
		utterances = raw_line.split('\t')
		user_utterance = utterances[0]
		bot_utterance = utterances[1]
		bot_response = find_best_utterance(user_utterance,nearest_neighbor)

		if bot_utterance != bot_response :
			correct_dialog_track = False
		else :
			correct_sentences += 1
		count_sentences +=1


if count_sentences == 0 :
	print('Per-Response Accuracy is ZERO')
else :
	print('Per-Response Accuracy = {}%'.format(str(float(correct_sentences)*100/count_sentences)))
if count_dialog == 0:
	print('Per-Dialog Accuracy is ZERO')
else :
	print('Per-Dialog Accuracy = {}%'.format(str(float(correct_dialog)*100/count_dialog)))
t_handle.close()
