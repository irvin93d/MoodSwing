import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction.text import TfidfVectorizer

def tweet_proba(tweet, subjects, v, model):
    text = re.sub(r'(.)\1+', r'\1\1', tweet[0].lower())
    for s in subjects:
        text = text.replace(s, "")
    x_input = v.transform(text)
    return model.predict_proba(x_input)
    
def tweet_count(tweet):
    # retweets have more weight than favorites
    return 5 * tweet[1] + tweet[2] + 1

def process_tweets(tweets, subject):
    # tweets is a list of size 3 tuples
    # (tweet body, # of retweets, # of favorites)
    with open('regmodel.pickle', 'rb') as f:
        model = pickle.load(f)
    with open('vectorizer.pickle', 'rb') as f:
        v = pickle.load(f)
    
    subjects = subject.split()
    counts = np.Array([tweet_count(tweet, subjects, v, model) for tweet in tweets])
    scores = (np.Array([tweet_proba(tweet) for tweet in tweets]) * 2) - 1
    weighted_score = np.average(scores, weights = counts)
    
    return tweets[np.argmin(scores)][0], tweets[np.argmax(scores)][0], weighted_score
