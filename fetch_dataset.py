import twitter
import string
import json
import sys
from pprint import pprint
import urllib

twitter_config = json.load(open('./twitter_config.json'))

api = twitter.Api(consumer_key=twitter_config['consumer_key'],
                  consumer_secret=twitter_config['consumer_secret'],
                  access_token_key=twitter_config['access_token_key'],
                  access_token_secret=twitter_config['access_token_secret']
                  )
black_list_words = ["the", "and", "of", "a", "is", "to"]

max_w_len = 45  # Seems to be a very long word

# Convert a word to a connonified form

                # raw_query="q={0}&result_type=recent&count={1}".format(keyword, count)

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
        nextId = statuses[len(statuses) - 1].id - 1


    return [tweet.text for tweet in tweets]


def main():

    tweets = getTweets('trump', 200)

    for tweet in tweets:
        print(tweet)
    print(len(tweets))

if __name__ == "__main__":
    # execute only if run as a script
    main()
