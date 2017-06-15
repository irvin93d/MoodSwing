"""
MoodSwing
Alexa Skill - Twitter Sentiment Analysis
Final Project - CPE466
Kyle Vigil, Alex Boyd, Jonathan Ohlsson, Duane Irvin
"""

from __future__ import print_function
from __future__ import unicode_literals
import twitter
import string
import json
import sys
from pprint import pprint
import urllib
import datetime
import numpy as np
import pickle
import re
import unicodedata
from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction.text import TfidfVectorizer

# api object to connect to the Twitter search to retrieve tweets
# put in own details here,
#api = twitter.Api(consumer_key, consumer_secret, access_token_key, access_token_secret)

def emoji_to_name(text):
    # given a string, this will replace all of the emojis (ord >= 256) with the name of the emoji
    return "".join([c if ord(c) <= 256 else " " + unicodedata.name(c, c) + " " for c in text])

def tweet_proba(tweets, v, model):
    # preprocessing, vectorization, and prediction of the list of tweet texts

    # text preprocessing:
    # 1) reduce repeated characters to only 2 characters 2) replace emojis with emoji names
    texts = np.array([re.sub(r'(.)\1+', r'\1\1', emoji_to_name(tweet.lower())) for tweet in tweets])

    x_input = v.transform(texts) # vectorize text
    ret = model.predict_proba(x_input)[:,1] # predict sentiments with linear regression model
    return ret
    
def tweet_count(tweet):
    # retweets have more weight than favorites
    return 5 * tweet[1] + tweet[2] + 1

def process_tweets(tweets, subject):
    # tweets is a list of size 3 tuples
    # (tweet body, # of retweets, # of favorites)
    # All of the preprocessing and loading and calling of sentiment classification model

    # load the regression model sentiment classifier. Created in ModelSelection.py
    with open('regmodel.pickle', 'rb') as f:
        model = pickle.load(f)

    # load the vectorizer function that creates the model feature row from a body of text.
    # created in ModelSelection.py
    with open('vectorizer.pickle', 'rb') as f:
        v = pickle.load(f)

    # variables to store most positive and negative tweets
    negative_score = 1
    negative_tweet = ""
    positive_score = -1
    positive_tweet = ""

    # list of average weighted composite sentiment scores for three time periods
    sentiments = []

    for i in range(3): # three time periods
        if len(tweets[i]) == 0: # check if there are any tweets, 0 (neutral) if none found
            sentiments.append(0)
        else: # tweets exist
            texts = [tweet[0] for tweet in tweets[i]] # list of just text of tweets

            # sentiments for each tweet text shifted from a range of 0 to 1 --> -1 to 1
            scores = (tweet_proba(texts, v, model) * 2) - 1
            
            # weight each sentiment score by the number of retweets and favorites it got
            # if a tweet is popular (lots of likes and retweets), twitter agrees with the 
            # sentiment of that tweet on that topi
            counts = np.array([tweet_count(tweet) for tweet in tweets[i]])

            # take the weighted average of all sentiments
            sentiments.append(np.average(scores, weights = counts))

            # update texts for most negative and positive tweets
            if scores.min() < negative_score:
                negative_tweet = tweets[i][np.argmin(scores)][0]
                negative_score = scores.min()
            if scores.max() > positive_score:
                positive_tweet = tweets[i][np.argmax(scores)][0]
                positive_score = scores.max()

    return positive_tweet, negative_tweet, sentiments

def get_tweets(keyword, count=100): 
    # Returns a list of three (time periods) lists of tuples (tweets) of tweet text, favorites, retweets 
    # keyword = topic, count = number of tweets per time period

    tweets = [] # list of lists

    # get date information for creating bins to query twitter for
    today = datetime.date.today().isoformat()
    yesterday = datetime.date.fromordinal(datetime.date.today().toordinal()-1).isoformat()
    last_week = datetime.date.fromordinal(datetime.date.today().toordinal()-7).isoformat()
    dates = (last_week, yesterday, today, None)
    
    # three date ranges
    for i in range(3):
        temp = [] # list of tweets to be appended to tweets
        nextId = None # used for paging (not necessary in our current implementation due to time constraints)
        left = count # the number of tweets left to retrieve per time period
        toGet = 0 # used for paging. Number of tweets to get for a single query
        
        while left > 0:
            toGet = min(left, 100) # find number of tweets to get in one query, max is 100
            left -= 100 # decrement tweets left

            # actual twitter search, since and until are time constraint, result_type gets most popular tweets, 
            # term searches by topic
            statuses = api.GetSearch(
                term=keyword, 
                max_id=nextId, 
                count=toGet,
                lang="en",
                since=dates[i],
                until=dates[i+1],
                result_type="popular"
            )
            
            # lengthen temporary list of tweet tuples
            temp.extend([(t.text, t.retweet_count, t.favorite_count) for t in statuses])

            # if no tweets are found, exit loop
            if len(statuses) == 0:
                break
            
            # used for paging
            nextId = statuses[len(statuses) - 1].id - 1
            
        tweets.append(temp)
    
    return tweets

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, card_output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': card_output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    # Intent - onStart or welcomeItent
    # Responds with help and user interaction for sentiment

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Mood Swing. " \
                    "See how Twitter feels on any topic. For example by saying, " \
                    "how does Twitter feel about Leonardo DiCaprio?"

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "See how Twitter feels on any topic. For example by saying, " \
                    "how does Twitter feel about Leonardo DiCaprio?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    # Intent - sessionEnd
    # Used when quitting MoodSwing session

    card_title = "Session Ended"
    speech_output = "Thank you for trying Mood Swing. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, "", None, should_end_session))

def value(sent):
    # Return text interpretation of the numerical sentiment value, between -1 and 1

    if sent < -0.1:
        return 'very negative'
    elif sent < -0.01:
        return 'somewhat negative'
    elif sent < 0.01:
        return 'neutral'
    elif sent < 0.1:
        return 'somewhat positive'
    else:
        return 'very positive'

def get_twitter_sentiment(intent, session):
    # Main function to gather all twitter sentiment. Focus of work here.

    should_end_session = True # single response to a single query
    topic = '<error>' # default topic

    if 'Topic' in intent['slots'] and 'value' in intent['slots']['Topic']: # if alexa was able to pick up words from the user
        topic = intent['slots']['Topic']['value'] # get topic from JSON

        # all sentiment analysis
        posTweet, negTweet, sentiment = process_tweets(get_tweets(topic, 50), topic)
        
        # clean tweets for voice output by Alexa
        posOut = ' '.join([i for i in posTweet.split() if 'http' not in i])
        negOut = ' '.join([i for i in negTweet.split() if 'http' not in i])

        # create outputs, card and spoken
        speech_output = "last week twitter felt " + value(sentiment[0]) + " about " + topic + ". yesterday twitter felt " + value(sentiment[1]) \
                        + " and today twitter feels " + value(sentiment[2]) + ". the most positive tweet was, " + posOut + ". and the most negative tweet was, " + negOut
        card_output = "Last week: " + value(sentiment[0]) + ", Score: " + str(sentiment[0]) + \
                        "\nYesterday: " + value(sentiment[1]) + ", Score: " + str(sentiment[1]) + \
                        "\nToday: " + value(sentiment[2]) + ", Score: " + str(sentiment[2]) + \
                        "\nMost positive tweet: " + posTweet + "\nMost negative tweet: " + negTweet

    else: # no input from user
        speech_output = "Sorry your input was not detected. Please try again"
        card_output = "Error detecting input. Please try again. Format: Alexa, ask MoodSwing how twitter feels about <topic>"

    return build_response({}, build_speechlet_response(
        topic.title() + ": Twitter Analysis", speech_output, card_output, "", should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    # Called when the session starts

    # logging
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    # Called when the user launches the skill without specifying what they want

    # logging
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    # Called when the user specifies an intent for this skill

    # logging
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to skill intent handlers
    if intent_name == "SentimentAnalysisIntent":
        return get_twitter_sentiment(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    # Called when the user ends the session.
    # Is not called when the skill returns should_end_session=true

    # logging
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])


# --------------- Main handler ------------------

def lambda_handler(event, context):
    # Route the incoming request based on type (LaunchRequest, IntentRequest,
    # etc.) The JSON body of the request is provided in the event parameter.
    
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    # error check to make sure the request came from our Alexa Skill
    if (event['session']['application']['applicationId'] != "amzn1.ask.skill.29cb168c-b2b6-46c2-85e0-c469a1a29e6d"):
        raise ValueError("Invalid Application ID")

    # start new session
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    # dispatch all requests
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
