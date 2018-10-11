# Undergraduate Thesis

## Topic

The topic of this thesis is "Neural Approaches Toward Domain Independent Dialog System"

## Description

The description is the same as in the [ **Website Link** ](<https://sourabhmajumdar.github.io/undergrad_thesis/>).

To summarize we want to develop a dialog system that is capable of handling more than one task oriented conversation and also be able to scale to new domains without much computational effort

## Running the project 

To run this project we need to complete two basic steps

1. Create the Data
2. Run the Model

### Creating the Data

To create the data, you need to navigate to the Dialog_Generator folder and run the following command

```python

python create_dialog.py

```

### Running the models

There are two models to run i.e. *Single_Memory_Network_Architecture* and *Multiple_Memory_Network_Architecture*

### Single Memory Network

In this model there is a single memory network that aims to handle multiple domains, so one memory network is handling separate domains like *making a transaction* and *dislaying account balance*

To run and test this model, run the following commands

**To Train**
```python
python one_mem_net.py --train=True
```

**To Test**
```python
python one_mem_net.py --train=False
```

### Multiple Memory Network

In this model, we have multiple memory networks, each handling one specific task i.e one memory network handles transaction and another one handles account balance.

To be able to handle multiple domains, we introduce a third memory network, whose job is to figure out which memory network to call for the conversation.

In this case we can handle multiple intents and scale to new domains easily because our job is not to carry the conversation but whom to call for the conversation.

To run this model, run the following commands

**To Train**
```python
python mult_mem_net.py --train=True
```

**To Test**
```python
python mult_mem_net.py --train=False
```


### Resources

If you want to learn more about **Memory Networks**, you can check out the following link.


<a href="http://www.youtube.com/watch?feature=player_embedded&v=ZwvWY9Yy76Q
" target="_blank"><img src="http://img.youtube.com/vi/ZwvWY9Yy76Q/0.jpg" 
alt="IMAGE ALT TEXT HERE" width="240" height="180" border="10" /></a>
