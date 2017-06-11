import twitter
import string
import json
import sys
from pprint import pprint
import urllib
from nltk.sentiment.vader import SentimentIntensityAnalyzer

twitter_config = json.load(open('./twitter_config.json'))

api = twitter.Api(consumer_key=twitter_config['consumer_key'],
                  consumer_secret=twitter_config['consumer_secret'],
                  access_token_key=twitter_config['access_token_key'],
                  access_token_secret=twitter_config['access_token_secret']
                  )

anal = SentimentIntensityAnalyzer() # TODO: rename?

def getTweets(keyword, count=100):
    tweets = []
    saved = 0
    nextId = None
    left = count
    toGet = 0
    while left > 0:
        if left > 100:
            toGet = 100
            left -= 100
        else:
            toGet = left
            left = 0

        statuses = api.results = api.GetSearch(
            term=keyword, 
            max_id=nextId, 
            count=count,
            lang="en")
        tweets.extend(statuses)
        saved += len(statuses)
        print("Fetched tweets:", saved)
        nextId = statuses[len(statuses) - 1].id - 1


    return tweets

def getSentiment(topic):
    tweets = [tweet.text for tweet in getTweets(topic)]
    res = {
        "neg": 0,
        "pos": 0,
        "neu": 0,
        "compound": 0
    }
    
    for tweet in tweets:
        sentiment = anal.polarity_scores(tweet)
        for (k,v) in sentiment.items():
            res[k] += v

    for (k, v) in res.items():
        res[k] = v / len(tweets)

    return res

def main():
    while True:
        topic = input("Topic > ")
        print(getSentiment(topic))

if __name__ == '__main__':
    main()