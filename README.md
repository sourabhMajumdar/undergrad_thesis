## Deep Learning Approaches for Low-Resource Task Oriented Conversational Agents Using Synthetic Data Generation Techniques

Before we begin, let me introduce myself. 
Hello, my name is Sourabh Majumdar and I am a final year undergraduate student at BITS-Pilani,Goa.
This project is my undergraduate thesis and as you can probably guess, the topic is "Deep Learning Approaches for Low-Resource Task Oriented Conversational Agents Using Synthetic Data Generation Techniques
".
I am currently doing this thesis under the supervision of [ **Dr. Marco Guerini** ](<mailto:guerini@fbk.eu>) at Fondazione Bruno Kessler,Trento,Italy

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
python experiment.py --train=True --epochs=200 --embedding_size=20
```
feel free to experiment with the arguements.

**Step#3 Run the Multiple memory network**

Multiple Memory Network uses more than one memory network to handle multiple tasks.
What I mean to say is that there is a dedicated memory task for each task and one memory network which determines which memory network to call from the conversation uptill now.

To run Multiple Memory Network, navigate to the folder *Multiple Memory Network* and run the following command
```python
python experiment.py --train=True --epochs=200 --embedding_size=20
```

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
