## Neural Approaches toward Domain independent dialog system

Before we begin, let me introduce myself. 
Hello, my name is Sourabh Majumdar and I am a final year undergraduate student at BITS-Pilani,Goa.
This project is my undergraduate thesis and as you can probably guess, the topic is "Neural Approaches toward domain indpndent dialog system".
I am currently doing this thesis under the supervision of [ **Dr. Marco Guerini** ](<mailto:guerini@fbk.eu>) at **Fondazione Bruno Kessler,Trento,Italy**

### Description of the project

To summarize, today's machine learning systems are highly advanced to communicate with humans in natural way. However they suffer two main problems that have not been adressed properly.

1. To Build such a system from scratch for a new domain (for e.g. creating a chat bot for a new company customer care) we need often need training data for the system which is not always available.

2. Once we have data for a new domain, it causes problems to scale to new domain because we need to re-train everything.

My undergraduate thesis tries to adress the problem by suggesting an end-to-end architecture that tries to solve both of these problems.


### Models Used 

The main models used for this experiment are the baselines from the paper [ **Learning End to End Dialog** ](<https://arxiv.org/abs/1605.07683>) and the my model proposed based on the [ **End to End Memory Networks** ](<https://arxiv.org/abs/1503.08895>)

The code for all the models are deescribed in the respective folder

### Data for the Experiment

The Data for this experiment was inspired from the paper [ **Dialog Self Play** ](<https://arxiv.org/abs/1801.04871>) proposed by google.

### How to run the Experiment

Before we begin the experiment, we need to understand how the experiment works.

**Workings**

The experiment is basically aimed at comparing multiple memory network model against single memory network.
We need to See how both these networks perform on singluar task and then on multiple task.
Finally we need to see the ability of the system to scale without loosing the ability to converse effectively in the already trained domains.

Since now we know how to run the experiments, we start it step by step

**Step#1 Create the Data**

To generate the data navigate to the *Data Generator* i.e

```
cd "Data Generator"
```
and run the *create_dialog.py* file

```python
python create_dialog.py
```

After you run this command you should see a folder named *Data* **one directory above**.

**Step#2 Run the single memory network**

Single Memory Network uses one memory network to handle all the tasks given in the experiment. 
To run the single memory network, navigate to the *Single Memory Network* folder and run the following command

```python
python single_memory_network.py --train=True --epochs=200 --embedding_size=20
```
feel free to experiment with the arguements.

**Step#3 Run the Multiple memory network**

Multiple Memory Network uses more than one memory network to handle multiple tasks.
What I mean to say is that there is a dedicated memory task for each task and one memory network which determines which memory network to call from the conversation uptill now.

To run Multiple Memory Network, navigate to the folder *Multiple Memory Network* and run the following command
```python
python multiple_memory_network.py --train=True --epochs=200 --embedding_size=20
```

**Step#4 Run TF-IDF model**

TF-IDF is information retreival model (*No Machine Learning*) and assigns _**T**erm-**Frequency**-**I**nverse**D**ocument**F**requency_ score to each candidate in our list of candidates and outputs the candidate with the highest *TF-IDF* score.

The **TF-IDF** score is calcutates for each candidate and our *current context* which happens to be the conversation uptill now.

To run and test this model, navigate to the directory named *td_idf_model* and run the following command
```python
python tf-idf_model.py
```

Now you will be prompted to entrire to enter a *data_dir*, simply mention your directory as *"../data/[NAME OF YOUR DATA FOLDER]"*.

Now you will be asked to entire the number of lines to process. This is the number of *user_utterances* you want to check.
**Note** : The average time to process one user_utterance may be as high as 11 seconds or higher, so be careful to enter an realistic value to see your results in time.


**Step#5 Run Nearest Neighbor model**

Just like the *TF-IDF* model, ***Nearest Neighbor*** tries to find the most simmilar conversation in the data-set and then returns the *bot utterance* from that conversation.

To run this model, simply navigate to the directory named *Nearest Neighbor* and run the command
```python
python nearest_neighbor.py
```
Now again like the previous case, you will be prompted to enter a directory for the data, mention it as *"../data/[NAME OF YOUR DATA FOLDER]"*

Now you will see the *Per-Response* and *Per-Dialog* Accuracy of the model.

**Step#6 Results**

Currently there is no separate folder to see results, you can see the **per-response** and **per-dialog accuracy**, after the training and the training and validation charts in the *Performance Charts* folder. 


If you have any questions, feel free to contact on the email provided below.
Ciao !!!!!

### Resources

Currently my project is inspired from the following papers

1. [ **Memory Networks** ](<https://arxiv.org/abs/1410.3916>)
2. [ **End to End Memory Networks** ](<https://arxiv.org/abs/1503.08895>)
3. [ **Learning End to End Dialog** ](<https://arxiv.org/abs/1605.07683>)
4. [ **Dialog Self Play** ](<https://arxiv.org/abs/1801.04871>)

### Architecture

I propose a multiple memory network architecture inspied from the first two links i.e ([ **Memory Networks** ](<https://arxiv.org/abs/1410.3916>) and [ **End to End Memory Networks** ](<https://arxiv.org/abs/1503.08895>)).

To create the data I take inspiration from the last link i.e ([ **Dialog Self Play** ](<https://arxiv.org/abs/1801.04871>)).



### Contact

Feel free to contact me at [ **Sourabh Majumdar** ](<mailto:msourabh970320@gmail.com>)
