import nltk.sentiment
import numpy as np
import pandas as pd
import sklearn.tree
import sklearn.linear_model
import sklearn.ensemble
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
import math
import pickle
from sklearn.model_selection import cross_val_score, GridSearchCV

# Read in the data
with open("c:/users/alex/documents/Sentiment Analysis Dataset.csv", 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
lines = [line.strip().split(",", maxsplit = 3) for line in lines]

header = lines[0]
del lines[0]

data = pd.DataFrame(lines[:300000], columns = header)
del lines

# Normalize the text
repl = lambda m: re.sub(r'(.)\1+', r'\1\1', m) # Reduce instances of repeated characters     
data["FilteredText"] = data.SentimentText.str.lower().apply(repl)

from sklearn.feature_extraction.text import TfidfVectorizer

mdf = 250 # Words must appear in at least 250 documents
v = TfidfVectorizer(binary=True, min_df = mdf, ngram_range=(1,2), use_idf=True) # A word must appear in at least 1000 tweets to be considered for tf-idf
x = v.fit_transform(data.FilteredText) # Calculate all tf-idf values for each word in every tweet

v.stop_words_ = set() # Clear out unneccessary data for reductino in pickle size

sid = SentimentIntensityAnalyzer()
outputs = data.FilteredText.apply(lambda x: sid.polarity_scores(x)["compound"])

# Do a grid search to find the best hyperparameters for the Random Forest

forest_model = sklearn.ensemble.RandomForestClassifier()

parameters = {
    'n_estimators' : [1, 5, 10, 20, 30],
    'max_depth' : [1, 5, 10, 20, 30]
}
searcher = GridSearchCV(forest_model, parameters, cv = 3, scoring="accuracy", n_jobs = -1, verbose = 3)
searcher.fit(x, data.Sentiment)
print("Forest Model yielded these params:", searcher.best_params_)

forest_model = sklearn.ensemble.RandomForestClassifier(**searcher.best_params_)
forest_acc = cross_val_score(forest_model, x, data.Sentiment, cv = 5, verbose = 3, n_jobs = 5).mean()
print("Forest Model yielded this accuracy:", forest_acc) 

log_model = sklearn.linear_model.LogisticRegression()
log_acc = cross_val_score(log_model, x, data.Sentiment, cv = 5, verbose = 3, n_jobs = 5).mean()
print("Logistic Regression Model yielded this accuracy:", log_acc)

if log_acc > forest_acc:
    best_model = log_model
    print("Logistic Regression Selected")
else:
    best_model = forest_model
    print("Random Forest Classifier Selected")

best_model.fit(x, data.Sentiment)

with open("regmodel.pickle", 'wb') as f:
    pickle.dump(best_model, f, 2)

with open("vectorizer.pickle", 'wb') as f:
    pickle.dump(v, f, 2)
