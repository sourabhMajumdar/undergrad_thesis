# Data Collection for Generating Dialogs

## About

This folder is dedicated to the task of data collection, if you want to contribute to the task of data collection, then follow the instructions given below

Before we begin, we must be clear what we mean by Data Collection.

If you have read the description of the project website, then you know that we use the method proposed by [ **Dialog Self-Play** ](<https://arxiv.org/abs/1801.04871>) by **Google**

The way we try to model this approach is by breaking down each conversation between a bot and a user as a set of **Actions**. 
Why we do this is because each conversation between a user and a bot is more than a couple of utterances.
There are also api_calls and checks needed to be done by the bot in-order to complete the task intended by the user.
The best way to model this by considering each interaction as a set of actions.

Now, once we have our actions, we intend to convert the actions which relate to an utterance into a natural language utterance.
for example an Action where the user informs the bot of a particular slot, let's say "informing the departure airport for a flight booking scenario" 
is by saying something like "I intend to leave from **Verona** airport". or "Departure airport is **Verona**".

We try to see both of the above utterance as a natural language template, something like "I intend to leave from **{departure_airport}** " and 
"Departure airport is **{departure_ariport}**".

Simmilary we intend to collect simmilar templates for each actions and eventually substitute the slot in the template by it's corrsponding value.
And by data, we mean that we intend to collect these templates

## Understanding the Spread sheet

The spread sheet contains 6 sheets. Each of the sheet is a data collection for a specific intent, like MAKE_TRANSACTION collects data for making a transaction

For each sheet you will see three collumns i.e Player, Intent, and Text

**Player** : specifies the person who makes the utterance, i.e player or bot.

**Intent** : specifies the intent that the player wants to convey.

**TEXT** : mentions a natural language utterance, of informing that intent


## An example

Let's say the intent is "inform {date_of_departure}", then a natural language template will be 
"I would like to leave on **{date_of_departure}**."

## Task

Your task as a participlant is to write such templates for each intent in each sheet
