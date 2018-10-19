from __future__ import absolute_import

import os
import re
import numpy as np
import tensorflow as tf

stop_words=set(["a","an","the"])

def write_candidates(data_dir="data/",file_name="candidate_file.txt",candidate_list=None) :
    
    f_handle = open(os.path.join(data_dir,file_name),"w")
    for candidate in candidate_list :
        print(candidate)
        f_handle.write("{}\n".format(candidate))
    f_handle.close()

def load_candidates(data_dir):
    candidates=[]
    candidates_f=None
    candid_dic={}

    candidates_f='candidates.txt'
    #candidates_list = list()
    with open(os.path.join(data_dir,candidates_f)) as f:
        for i,line in enumerate(f):
            #candidates_list.append(line.strip().split(' ',1)[1] + " --> " + str(i))
            candid_dic[line.strip().split(' ',1)[1]] = i
            line=tokenize(line.strip())[1:]
            candidates.append(line)
    # return candidates,dict((' '.join(cand),i) for i,cand in enumerate(candidates))
    #write_candidates(data_dir,candidate_list=candidates_list)
    return candidates,candid_dic


def load_dialog_task(data_dir, candid_dic, isOOV):
    '''Load the nth task. There are 20 tasks in total.

    Returns a tuple containing the training and testing data for the task.
    '''


    '''files = os.listdir(data_dir)
    files = [os.path.join(data_dir, f) for f in files]
    s = 'dialog-babi-task{}-'.format(task_id)
    train_file = [f for f in files if s in f and 'trn' in f][0]
    if isOOV:
        test_file = [f for f in files if s in f and 'tst-OOV' in f][0]
    else: 
        test_file = [f for f in files if s in f and 'tst.' in f][0]
    val_file = [f for f in files if s in f and 'dev' in f][0]'''

    train_file = os.path.join(data_dir,"train_data.txt")
    test_file = os.path.join(data_dir,"test_data.txt")
    val_file = os.path.join(data_dir,"val_data.txt")
    
    print("train_file is {} ".format(train_file))
    print("validation file is {} ".format(val_file))
    print("test file is {} ".format(test_file))
    
    train_data = get_dialogs(train_file,candid_dic)
    test_data = get_dialogs(test_file,candid_dic)
    val_data = get_dialogs(val_file,candid_dic)
    return train_data, test_data, val_data


def tokenize(sent):
    '''Return the tokens of a sentence including punctuation.
    >>> tokenize('Bob dropped the apple. Where is the apple?')
    ['Bob', 'dropped', 'the', 'apple', '.', 'Where', 'is', 'the', 'apple']
    '''
    sent=sent.lower()
    if sent=='<silence>':
        return [sent]
    result=[x.strip() for x in re.split('(\W+)?', sent) if x.strip() and x.strip() not in stop_words]
    if not result:
        result=['<silence>']
    if result[-1]=='.' or result[-1]=='?' or result[-1]=='!':
        result=result[:-1]
    return result


# def parse_dialogs(lines,candid_dic):
#     '''
#         Parse dialogs provided in the babi tasks format
#     '''
#     data=[]
#     context=[]
#     u=None
#     r=None
#     for line in lines:
#         line=str.lower(line.strip())
#         if line:
#             nid, line = line.split(' ', 1)
#             nid = int(nid)
#             if '\t' in line:
#                 u, r = line.split('\t')
#                 u = tokenize(u)
#                 r = tokenize(r)
#                 # temporal encoding, and utterance/response encoding
#                 u.append('$u')
#                 u.append('#'+str(nid))
#                 r.append('$r')
#                 r.append('#'+str(nid))
#                 context.append(u)
#                 context.append(r)
#             else:
#                 r=tokenize(line)
#                 r.append('$r')
#                 r.append('#'+str(nid))
#                 context.append(r)
#         else:
#             context=[x for x in context[:-2] if x]
#             u=u[:-2]
#             r=r[:-2]
#             key=' '.join(r)
#             if key in candid_dic:
#                 r=candid_dic[key]
#                 data.append((context, u,  r))
#             context=[]
#     return data

def parse_dialogs_per_response(lines,candid_dic):
    '''
        Parse dialogs provided in the babi tasks format
    '''
    data=[]
    context=[]
    u=None
    r=None
    for line in lines:
        line=line.strip()
        if line:
            nid, line = line.split(' ', 1)
            nid = int(nid)
            if '\t' in line:
                u, r = line.split('\t')
                a = candid_dic[r]
                u = tokenize(u)
                r = tokenize(r)
                # temporal encoding, and utterance/response encoding
                # data.append((context[:],u[:],candid_dic[' '.join(r)]))
                data.append((context[:],u[:],a))
                u.append('$u')
                u.append('#'+str(nid))
                r.append('$r')
                r.append('#'+str(nid))
                context.append(u)
                context.append(r)
            else:
                r=tokenize(line)
                r.append('$r')
                r.append('#'+str(nid))
                context.append(r)
        else:
            # clear context
            context=[]
    return data



def get_dialogs(f,candid_dic):
    '''Given a file name, read the file, retrieve the dialogs, and then convert the sentences into a single dialog.
    If max_length is supplied, any stories longer than max_length tokens will be discarded.
    '''
    with open(f) as f:
        return parse_dialogs_per_response(f.readlines(),candid_dic)

def vectorize_candidates_sparse(candidates,word_idx):
    shape=(len(candidates),len(word_idx)+1)
    indices=[]
    values=[]
    for i,candidate in enumerate(candidates):
        for w in candidate:
            indices.append([i,word_idx[w]])
            values.append(1.0)
    return tf.SparseTensor(indices,values,shape)

def vectorize_candidates(candidates,word_idx,sentence_size):
    shape=(len(candidates),sentence_size)
    C=[]
    for i,candidate in enumerate(candidates):
        lc=max(0,sentence_size-len(candidate))
        C.append([word_idx[w] if w in word_idx else 0 for w in candidate] + [0] * lc)
    return tf.constant(C,shape=shape)


def vectorize_data(data, word_idx, sentence_size, batch_size, candidates_size, max_memory_size):
    """
    Vectorize stories and queries.

    If a sentence length < sentence_size, the sentence will be padded with 0's.

    If a story length < memory_size, the story will be padded with empty memories.
    Empty memories are 1-D arrays of length sentence_size filled with 0's.

    The answer array is returned as a one-hot encoding.
    """
    S = []
    Q = []
    A = []
    data.sort(key=lambda x:len(x[0]),reverse=True)
    for i, (story, query, answer) in enumerate(data):
        if i%batch_size==0:
            memory_size=max(1,min(max_memory_size,len(story)))
        ss = []
        for i, sentence in enumerate(story, 1):
            ls = max(0, sentence_size - len(sentence))
            ss.append([word_idx[w] if w in word_idx else 0 for w in sentence] + [0] * ls)

        # take only the most recent sentences that fit in memory
        ss = ss[::-1][:memory_size][::-1]

        # pad to memory_size
        lm = max(0, memory_size - len(ss))
        for _ in range(lm):
            ss.append([0] * sentence_size)

        lq = max(0, sentence_size - len(query))
        q = [word_idx[w] if w in word_idx else 0 for w in query] + [0] * lq

        #print("okay to story is : {}\n and type of object for ss is : {}\n".format(ss,type(ss[0])))
        #print("okay so query is : {}\nand type of object for q is : {}\n".format(q,type(q[0])))
        
        ss_n = np.array(ss)
        q_n = np.array(q)
        a_n = np.array(answer)

        S.append(ss_n)
        Q.append(q_n)
        A.append(a_n)
    return S, Q, A
