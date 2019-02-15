from __future__ import absolute_import
from __future__ import print_function

from .data_utils import load_dialog_task, vectorize_data, load_candidates, vectorize_candidates, vectorize_candidates_sparse, tokenize , write_candidates
from sklearn import metrics
from .memn2n import MemN2NDialog
from itertools import chain
from six.moves import range, reduce
import sys
import tensorflow as tf
import numpy as np
import os
import time
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from tqdm import tqdm

plt.ion()



class MultipleMemoryModel(object):

    def __init__(self,
        data_dir,
        model_dir,
        performance_directory,
        converse_later,
        OOV, memory_size,
        random_state,
        batch_size,
        learning_rate,epsilon,
        max_grad_norm,
        evaluation_interval,
        hops,
        epochs,
        embedding_size,
        session,
        description,
        pipeline_testing,
        plot_progress):

        self.data_dir = data_dir
        self.model_dir = model_dir
        self.performance_directory = performance_directory
        self.converse_later = converse_later
        self.OOV = OOV
        self.memory_size = memory_size
        self.random_state = random_state
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.epsilon = epsilon
        self.max_grad_norm = max_grad_norm
        self.evaluation_interval = evaluation_interval
        self.hops = hops
        self.epochs = epochs
        self.embedding_size = embedding_size
        self.sess = session

        self.description = description
        self.pipeline_testing = pipeline_testing
        self.plot_progress = plot_progress

        candidates, self.candid2indx = load_candidates(self.data_dir)
        self.n_cand = len(candidates)
        
        self.indx2candid = dict((self.candid2indx[key], key) for key in self.candid2indx)
        
        # task data
        self.trainData, self.testData, self.valData = load_dialog_task(
            self.data_dir, self.candid2indx, self.OOV)
        
        data = self.trainData + self.testData + self.valData
        
        self.build_vocab(data, candidates)
        # self.candidates_vec=vectorize_candidates_sparse(candidates,self.word_idx)
        
        self.candidates_vec = vectorize_candidates(candidates, self.word_idx, self.candidate_sentence_size)
        
        self.optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate, epsilon=self.epsilon)
        


        print(" model_dir : {}\nbatch_size : {}\n vocab_size : {}\n n_cand : {}\n sentence_size : {}\n embedding_size : {}\n candidates_vec : {}\n hops : {} max_grad_norm : {}\n ".format(self.model_dir,self.batch_size, self.vocab_size, self.n_cand, self.sentence_size,self.embedding_size,self.candidates_vec,self.hops,self.max_grad_norm))



    def build_model(self) :

        self.model = MemN2NDialog(self.batch_size, self.vocab_size, self.n_cand, self.sentence_size, self.embedding_size, self.candidates_vec, session=self.sess,hops=self.hops, max_grad_norm=self.max_grad_norm, optimizer=self.optimizer,description=self.description)

        self.saver = tf.train.Saver(max_to_keep=50)

        self.summary_writer = tf.summary.FileWriter(self.model_dir, self.model.graph_output.graph)

    def get_description(self) :
        return self.description

    def build_vocab(self, data, candidates):

        vocab = reduce(lambda x, y: x | y, (set(
            list(chain.from_iterable(s)) + q) for s, q, a in data))
        vocab |= reduce(lambda x, y: x | y, (set(candidate)
                                             for candidate in candidates))
        vocab = sorted(vocab)
        self.word_idx = dict((c, i + 1) for i, c in enumerate(vocab))

        max_story_size = max(map(len, (s for s, _, _ in data)))
        mean_story_size = int(np.mean([len(s) for s, _, _ in data]))

        self.sentence_size = max(map(len, chain.from_iterable(s for s, _, _ in data)))
        self.candidate_sentence_size = max(map(len, candidates))

        query_size = max(map(len, (q for _, q, _ in data)))

        self.memory_size = min(self.memory_size, max_story_size)
        self.vocab_size = len(self.word_idx) + 1  # +1 for nil word

        self.sentence_size = max(query_size, self.sentence_size)  # for the position
        # params
        print("vocab size:", self.vocab_size)
        print("Longest sentence length", self.sentence_size)
        print("Longest candidate sentence length",
              self.candidate_sentence_size)
        print("Longest story length", max_story_size)
        print("Average story length", mean_story_size)

    def get_memory_size(self) :
        return self.memory_size

    def get_sentence_size(self) :
        return self.sentence_size

    def set_memory_size(self,new_memory_size) :
        self.memory_size = new_memory_size

    def set_sentence_size(self,new_sentence_size) :
        self.sentence_size = new_sentence_size


    def converse(self):
        context = []
        u = None
        r = None
        nid = 1
        while True:
            line = input('--> ').strip().lower()
            if line == 'exit':
                break
            if line == 'restart':
                context = []
                nid = 1
                print("clear memory")
                continue
            u = tokenize(line)
            data = [(context, u, -1)]
            s, q, a = vectorize_data(
                data, self.word_idx, self.sentence_size, self.batch_size, self.n_cand, self.memory_size)
            preds = self.model.predict(s, q)
            r = self.indx2candid[preds[0]]
            print(r)
            r = tokenize(r)
            u.append('$u')
            u.append('#' + str(nid))
            r.append('$r')
            r.append('#' + str(nid))
            context.append(u)
            context.append(r)
            nid += 1


    def print_results(self,cost,avg_cost,accuracy,description,fbeta_score) :
        print("---------------------RESULTS FOR {}----------------------".format(description))
        print("\n=====================> {} cost     = {}".format(description,str(cost)))
        print("=======================> {} avg cost = {}".format(description,str(avg_cost)))
        print("=====================> {} accuracy = {}%".format(description,str(accuracy*100)))
        print("=====================> {} fbeta score = {} \n".format(description,str(fbeta_score)))
        print("-------------------------------><---------------------------------------------")

    def display_results(self,train_cost_list,avg_train_cost_list,train_fbeta_list,val_cost_list,avg_val_cost_list,val_fbeta_list,epoch_list) :

        
        plt.subplot(2,1,1)
        plt.title(self.description + "_performance")
        plt.plot(epoch_list,train_cost_list,'b',label='train_cost')
        plt.plot(epoch_list,val_cost_list,'r',label='val_cost')
        plt.plot(epoch_list,avg_train_cost_list,'y',label='avg_train_cost_list')
        plt.plot(epoch_list,avg_val_cost_list,'g',label='avg_val_cost')
        plt.xlabel('#Epochs')
        plt.ylabel('Cost')
        red_patch = mpatches.Patch(color='red',label='Validation Cost')
        blue_patch = mpatches.Patch(color='blue',label='Training Cost')
        yellow_patch = mpatches.Patch(color='yellow',label='Average Training Cost')
        green_patch = mpatches.Patch(color='green',label='Average Validation Cost')
        plt.legend(handles=[red_patch,green_patch,yellow_patch,blue_patch],loc='upper right')

        plt.subplot(2,1,2)
        red_beta_patch = mpatches.Patch(color='blue',label='train_fbeta_score')
        blue_beta_patch = mpatches.Patch(color='red',label='val_fbeta_score')
        plt.legend(handles=[red_beta_patch,blue_beta_patch],loc='upper right')
        plt.plot(epoch_list,train_fbeta_list,'b',label='train_fbeta_score')
        plt.plot(epoch_list,val_fbeta_list,'r',label='val_fbeta_score')
        plt.xlabel('#Epochs')
        plt.ylabel('fbeta_score')

        
        plt.show()
        plt.pause(0.01)


    def train(self):
        trainS, trainQ, trainA = vectorize_data(self.trainData, self.word_idx, self.sentence_size, self.batch_size, self.n_cand, self.memory_size)
        valS, valQ, valA = vectorize_data(self.valData, self.word_idx, self.sentence_size, self.batch_size, self.n_cand, self.memory_size)
        n_train = len(trainS)
        n_val = len(valS)
        print("Training Size", n_train)
        print("Validation Size", n_val)
        tf.set_random_seed(self.random_state)
        
        batches = zip(range(0, n_train - self.batch_size, self.batch_size),
                      range(self.batch_size, n_train, self.batch_size))
        
        batches = [(start, end) for start, end in batches]
        
        val_batches = zip(range(0,n_val-self.batch_size,self.batch_size),
                          range(self.batch_size,n_val,self.batch_size))
        val_batches = [(start,end) for start,end in val_batches]

        
        best_validation_accuracy = 0
        best_validation_cost = 99999

        epoch_list = list()
        train_cost_list = list()
        val_cost_list = list()
        avg_train_cost_list = list()
        avg_val_cost_list = list()
        train_fbeta_list = list()
        val_fbeta_list = list()

        if self.pipeline_testing :
            self.epochs = 1
            batches = batches[:100]
            val_batches = val_batches[:100]

        for t in range(1,self.epochs + 1):
            np.random.shuffle(batches)
            total_train_cost = 0.0
            print("Epoch# {}".format(t))
            print("Calculating training cost ")
            for start, end in tqdm(batches):
                s = trainS[start:end]
                q = trainQ[start:end]
                a = trainA[start:end]
                cost_t = self.model.batch_fit(s, q, a)
                total_train_cost += cost_t

            train_preds = self.batch_predict(trainS, trainQ, n_train)
            train_acc = metrics.accuracy_score(np.array(train_preds), trainA)
            train_fbeta_score = metrics.fbeta_score(np.array(train_preds),trainA,beta=9999,average='micro')
            train_fbeta_list.append(train_fbeta_score)

            epoch_list.append(t)
            total_avg_train_cost = float(total_train_cost)/len(batches)
            train_cost_list.append(total_train_cost)

            avg_train_cost_list.append(total_avg_train_cost)


            self.print_results(cost=total_train_cost,
                avg_cost=total_avg_train_cost,
                accuracy=train_acc,
                fbeta_score=train_fbeta_score,
                description="training")



            total_val_cost = 0.0
            
            for start,end in tqdm(val_batches):
                s = valS[start:end]
                q = valQ[start:end]
                a = valA[start:end]
                cost_val = self.model.batch_compute_loss(s,q,a)
                total_val_cost += cost_val

            total_avg_val_cost  = float(total_val_cost)/len(val_batches)

            val_cost_list.append(total_val_cost)
            avg_val_cost_list.append(total_avg_val_cost)
            val_preds = self.batch_predict(valS, valQ, n_val)
            val_acc = metrics.accuracy_score(val_preds, valA)
            val_fbeta_score = metrics.fbeta_score(val_preds,valA,beta=9999,average='micro')
            val_fbeta_list.append(val_fbeta_score)

            self.print_results(cost=total_val_cost,
                avg_cost=total_avg_val_cost,
                accuracy=val_acc,
                fbeta_score=val_fbeta_score,
                description="validation")


            if self.plot_progress :
                self.display_results(train_cost_list=train_cost_list,
                    avg_train_cost_list=avg_train_cost_list,
                    train_fbeta_list=train_fbeta_list,
                    val_cost_list=val_cost_list,
                    avg_val_cost_list=avg_val_cost_list,
                    val_fbeta_list=val_fbeta_list,
                    epoch_list=epoch_list)

            if t % self.evaluation_interval == 0 or t == 1:
                train_preds = self.batch_predict(trainS, trainQ, n_train)
                val_preds = self.batch_predict(valS, valQ, n_val)
                train_acc = metrics.accuracy_score(
                    np.array(train_preds), trainA)
                val_acc = metrics.accuracy_score(val_preds, valA)
                '''print('-----------------------')
                print('Epoch', t)
                print('Total Training Cost:', total_cost)
                print('Total Validation Cost:',val_cost)
                print('Training Accuracy:', train_acc)
                print('Validation Accuracy:', val_acc)
                print('-----------------------')'''

                # write summary
                train_acc_summary = tf.summary.scalar(os.path.join(self.model_dir + '/','train_acc'), tf.constant((train_acc), dtype=tf.float32))
                val_acc_summary = tf.summary.scalar(os.path.join(self.model_dir + '/','val_acc'), tf.constant((val_acc), dtype=tf.float32))
                merged_summary = tf.summary.merge(
                    [train_acc_summary, val_acc_summary])
                summary_str = self.sess.run(merged_summary)
                self.summary_writer.add_summary(summary_str, t)
                self.summary_writer.flush()

                if total_val_cost < best_validation_cost:
                    best_validation_accuracy = val_acc
                    best_validation_cost = total_val_cost
                    self.saver.save(self.sess, os.path.join(self.model_dir,'model.ckpt'), global_step=t)


        
        self.display_results(train_cost_list=train_cost_list,
            avg_train_cost_list=avg_train_cost_list,
            train_fbeta_list=train_fbeta_list,
            val_cost_list=val_cost_list,
            avg_val_cost_list=avg_val_cost_list,
            val_fbeta_list=val_fbeta_list,
            epoch_list=epoch_list)
        save_image_name = self.description + "_performance.png"

        if not os.path.exists(self.performance_directory) :
            os.makedirs(self.performance_directory)
        plt.savefig(os.path.join(self.performance_directory,save_image_name))
        plt.close()

    

   

    def predict_and_converse(self,context,user_utterance,nid,bot_utterance) :
        u = None
        r = None
        
        line = user_utterance.strip().lower()

        u = tokenize(line)
        data = [(context, u, -1)]
        s, q, a = vectorize_data(data,self.word_idx,self.sentence_size,self.batch_size,self.n_cand,self.memory_size)
        preds = self.model.predict(s,q)

        r = self.indx2candid[preds[0]]
        bot_response = r

        if "mem_call" in bot_utterance :
            return bot_response, context, nid
        else :
            if bot_response != bot_utterance :
                r = bot_utterance
            r = tokenize(r)
            u.append('$u')
            u.append('#' + str(nid))
            r.append('$r')
            r.append('#' + str(nid))
            context.append(u)
            context.append(r)
            nid += 1
            return bot_response, context, nid


    def load_saved_model(self) :
        ckpt = tf.train.get_checkpoint_state(self.model_dir)
        
        if ckpt and ckpt.model_checkpoint_path :
            self.saver.restore(self.sess,ckpt.model_checkpoint_path)
        else :
            print("...no checkpoint found...")

    def test(self):
        
        print(" Hey I am in the testing phase, model_dir is : ",self.model_dir)
        berger = input()
        
        ckpt = tf.train.get_checkpoint_state(self.model_dir)
        
        if ckpt and ckpt.model_checkpoint_path:
            self.saver.restore(self.sess, ckpt.model_checkpoint_path)
        else:
            print("...no checkpoint found...")
        if self.converse_later:
            self.converse()
        else:
            testS, testQ, testA = vectorize_data(
                self.testData, self.word_idx, self.sentence_size, self.batch_size, self.n_cand, self.memory_size)
            n_test = len(testS)
            print("Testing Size", n_test)
            test_preds = self.batch_predict(testS, testQ, n_test)
            test_acc = metrics.accuracy_score(test_preds, testA)
            print("Testing Accuracy:", test_acc)

    def batch_predict(self, S, Q, n):
        preds = []
        for start in range(0, n, self.batch_size):
            end = start + self.batch_size
            s = S[start:end]
            q = Q[start:end]
            pred = self.model.predict(s, q)
            preds += list(pred)
        return preds

    def close_session(self):
        self.sess.close()




    





