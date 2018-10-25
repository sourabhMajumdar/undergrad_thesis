import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import numpy as np
from tqdm import tqdm


nltk.download('punkt')
stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char),None) for char in string.punctuation)


def stem_tokens(tokens) :
    return [stemmer.stem(item) for item in tokens]


def normalize(text) :
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))


vectorizer = TfidfVectorizer(tokenizer=normalize,stop_words='english')



def cosine_sim(text1,text2) :
    tfidf = vectorizer.fit_transform([text1,text2])
    return ((tfidf*tfidf.T).A)[0,1]



tf_idf_model_directory = "tf_idf_model/"

if not os.path.exists(tf_idf_model_directory) :
    os.makedirs(tf_idf_model_directory)

print(cosine_sim('a little bird','a little bird'))
print(cosine_sim('a little bird','a little bird chirps'))
print(cosine_sim('a little bird','a big dog barks'))


data_dir = input('Enter Data Directory :\t')

c_handle = open(os.path.join(data_dir,'candidates.txt'))

candidate_list = list()
for line in c_handle :
    candidate_list.append(line[2:].strip())
c_handle.close()




def predict_response(candidate_list,context) :
    candidate_scores = list()
    for i in range(len(candidate_list)) :
        score = cosine_sim(candidate_list[i],context)
        candidate_scores.append(score)
        
    candidate_array = np.array(candidate_scores)
    index_tuple = np.unravel_index(candidate_array.argmax(),candidate_array.shape)
    #print(index_tuple)
    index = index_tuple[0]
    bot_response = candidate_list[index]
    #print("context is \n:{}\n bot_response is \n: {}\n".format(context,bot_response))
    
    
    return bot_response

f_handle = open(os.path.join(data_dir,'val_data.txt'))



count_sentence = 1
count_dialog = 0
count = 0
context = str()
success_sentence = 0
list_of_lines = f_handle.readlines()
print("total_lines to process  : {} ".format(len(list_of_lines)))





print("The average amount of time to process one sentence is 11 seconds !!")
break_sentence_number = int(input('enter the number of sentence you want to process'))
count_sentence = 0
count_dialog = 0
correct_dialog = 0
correct_sentence = 0
correct_dialog_track = True
lines_to_process = list_of_lines[:min(len(list_of_lines),break_sentence_number)]
for line in tqdm(lines_to_process) :   
    raw_line = line[2:].lower().strip()
    if not raw_line :
        if correct_dialog_track :
            correct_dialog += 1
        correct_dialog_track = True
        count_dialog += 1
        context = str()
    else :
        count_sentence += 1
        
        utterances = raw_line.split('\t')
        
        user_utterance = utterances[0]
        bot_utterance = utterances[1]
        
        context += user_utterance
        #print("user_utterance\n : {}\n context :\n {}\n bot_utterance :\n {}".format(user_utterance,context,bot_utterance))
        predicted_response = predict_response(candidate_list,context)
        
        context += '\t' + bot_utterance + '\n'
        
        if bot_utterance != predicted_response :
            correct_dialog_track = False
        else :
            correct_sentence += 1
        
if count_sentence == 0 :
    print('Per-Dialog Accuracy ZERO')
else :
    print('Per-Response Accuracy : {}%'.format(str(float(correct_sentence)*100/count_sentence)))

if count_dialog == 0 :
    print('Per-Dialog Accuracy ZERO')
else :
    print('Per-Dialog Accuracy : {}%'.format(str(float(correct_dialog)*100/count_dialog)))

       
    
f_handle.close()




