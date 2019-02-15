import numpy as np
from sys import argv
import os

def vectorize_utt(utt, vocab):
    vec = np.zeros(len(vocab))
    for w in utt.split(' '):
        try:
            vec[vocab[w]] = 1
        except KeyError:
            pass
    return vec


def vectorize_all(context_response_pairs, vocab):
    
    context_list = list()
    response_list = list() 

    for ind, context_response in enumerate(context_response_pairs):
        context, response = context_response
        #print("Context is :\n\n{}".format(context))
        #print("\n\nResponse is : \n\n{}".format(response))
        #u = input('Onto next ? ')
        context_vec = vectorize_utt(context, vocab)
        response_vec = vectorize_utt(response, vocab)
        context_list.append(context_vec)
        response_list.append(response_vec)
    
    context_tensor = np.array(context_list)
    response_tensor = np.array(response_list)

    return context_tensor, response_tensor


def load_vocab(vocab_filename):
    vocab = {}
    with open(vocab_filename, 'r') as f:
        for line in f:
            ind, word = line.strip().split('\t')
            vocab[word] = int(ind)
    return vocab


def load_train(train_filename):
    context_response_pairs = list()
    print("opening file name : {}".format(train_filename))
    with open(train_filename, 'r') as f:
        for line in f:
            sentence_pair = line[1:].strip().split('\t')
            if len(sentence_pair) < 2 :
                context = sentence_pair[0]
                context_response_pairs.append((context,"<silence>"))
            else :
                context, response = sentence_pair
                context_response_pairs.append((context, response))
    return context_response_pairs


def make_tensor(train_filename,vocab):
    print("opening file name : {}".format(train_filename))
    if type(vocab) == 'str':
        vocab = load_vocab(vocab_filename)
    train = load_train(train_filename)
    context, response = vectorize_all(train, vocab)
    #print("shape of context {} \nshape of response{}\n".format(context.shape,response.shape))
    return context, response

