"""
MoodSwing
Alexa Skill - Twitter Sentiment Analysis
Final Project - CPE466
Kyle Vigil, Alex Boyd, Jonathan Ohlsson, Duane Irvin
"""

from __future__ import print_function
import twitter
import string
import json
import sys
from pprint import pprint
import urllib
import datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer

api = twitter.Api(consumer_key='OLh11Nm6ad9w1a5QRD4h2ARxh',
                  consumer_secret='82vgb7dxiwbHKP2h73qah43JBPXgz1nWs84SX9KqDxo6EoNNHO',
                  access_token_key='2801824835-EaJY8MQkq4sssj2gMtj9Ig5lFnihtUxtpTn0JAM',
                  access_token_secret='3BK70ksGKpcMFQ0ENuy6qWP6AOeFRmI45Dw8ysl2SByyh')

anal = SentimentIntensityAnalyzer(lexicon_file="vader_lexicon.txt") # TODO: rename?

def getTweets(keyword, count=100):
    tweets = []
    today = datetime.date.today().isoformat()
    yesterday = datetime.date.fromordinal(datetime.date.today().toordinal()-1).isoformat()
    last_week = datetime.date.fromordinal(datetime.date.today().toordinal()-7).isoformat()
    dates = (last_week, yesterday, today, None)
    
    for i in range(3):
        temp = []
        nextId = None
        left = count
        toGet = 0
        
        while left > 0:
            toGet = min(left, 100)
            left -= 100

            statuses = api.GetSearch(
                term=keyword, 
                max_id=nextId, 
                count=toGet,
                lang="en",
                since=dates[i],
                until=dates[i+1],
                result_type="popular"
            )
            
            temp.extend([t.text for t in statuses])

            if len(statuses) == 0:
                break
            
            nextId = statuses[len(statuses) - 1].id - 1
            
        tweets.append(temp)
    
    return tweets

def getSentiment(tweets):
    sentiments = []
    negative = (0, "")
    positive = (0, "")
    
    for i in range(3):
        temp_sentiment = 0

        if len(tweets[i]) == 0:
            sentiments.append(0)
        else:
            for tweet in tweets[i]:
                s = anal.polarity_scores(tweet)['compound']
                temp_sentiment += s
                if s > positive[0]:
                    positive = (s, tweet)
                if s < negative[0]:
                    negative = (s, tweet)

            sentiments.append(temp_sentiment / len(tweets[i]))

    return sentiments, negative[1], positive[1]

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
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Mood Swings. " \
                    "See how Twitter feels on any topic. For example by saying, " \
                    "how does Twitter feel about Leonardo DiCaprio?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "See how Twitter feels on any topic. For example by saying, " \
                    "how does Twitter feel about Leonardo DiCaprio?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "Im on a card", reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying Mood Swing. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, "", None, should_end_session))

def value(sent):
    if sent < 0:
        return 'negative'
    elif sent > 0:
        return 'positive'
    else:
        return 'neutral'


def get_twitter_sentiment(intent, session):
    """ Main function to gather all twitter sentiment. Focus of work here.
    """
    session_attributes = {}
    should_end_session = False
    topic = '<error>'

    if 'Topic' in intent['slots'] and 'value' in intent['slots']['Topic']: # if alexa was able to pick up words from the user
        topic = intent['slots']['Topic']['value']
        sentiment, negTweet, posTweet = getSentiment(getTweets(topic, 50))
        posOut = ' '.join([i for i in posTweet.split() if 'http' not in i])
        negOut = ' '.join([i for i in negTweet.split() if 'http' not in i])

        speech_output = "last week twitter felt " + value(sentiment[0]) + " about " + topic + ". yesterday twitter felt " + value(sentiment[1]) \
                        + " and today twitter feels " + value(sentiment[2]) + ". the most positive tweet was, " + posOut + " and the most negative tweet was, " + negOut
        card_output = "Last week: " + value(sentiment[0]) + ", Score: " + str(sentiment[0]) + \
                        "\nYesterday: " + value(sentiment[1]) + ", Score: " + str(sentiment[1]) + \
                        "\nToday: " + value(sentiment[2]) + ", Score: " + str(sentiment[1]) + \
                        "\nMost positive tweet: " + posTweet + "\nMost negative tweet: " + negTweet

        # speech_output = "twitter feels positive about " + topic + ", with a score of " + str(round(sentiment,2)) + \
        # ". the most positive tweet is, " + ' '.join([i for i in posTweet.split() if 'http' not in i and i[0].isalpha()])

    else: # no input from user
        speech_output = "Sorry your input was not detected. Please try again"
        card_output = "Error detecting input. Please try again. Format: Alexa, ask MoodSwing how twitter feels about <topic>"

    return build_response(session_attributes, build_speechlet_response(
        topic.title() + ": Twitter Analysis", speech_output, card_output, "why is this here", should_end_session))



# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "SentimentAnalysisIntent":
        return get_twitter_sentiment(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])


    if (event['session']['application']['applicationId'] != "amzn1.ask.skill.29cb168c-b2b6-46c2-85e0-c469a1a29e6d"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])