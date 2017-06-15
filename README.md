# MoodSwings
Project - Twitter Sentiment Analysis for Amazon Alexa
Title - MoodSwings
Members - Kyle Vigil, Alex Boyd, Jonathan Ohlsson, Duane Irvin
 
# About
We are giving users of Alexa the ability to gauge Twitter about Twitter users' general feelings towards any topic (for instance, feelings about Coca-Cola, Donald Trump, CNN, etc.). Alexa will report back the general sentiment comparing a few different time periods (last week vs yesterday vs today) specified by the user upon query.
 
# Technologies
We are developing a skill for Amazon Alexa that allows users of Alexa to gain insight into the current and past sentiment Twitter has to any number of topics. In order to do this, we are running a program on AWS Lambda which is the standard connection for Alexa Skills. This allows the command that is run through Alexa to query our program with the appropriate parameters and our application will return back the desired sentiment analysis. The application running on Lambda will be written in Python 2.7 and will connect to the Twitter API through the package python-twitter. This package along with approved Twitter API access allows us to query Tweets from the past week as fast as possible. Given these tweets we used sklearn logistic regression to classify sentiment analysis on the tweets for the given time period and topic.
 
# Purpose
We give Alexa users the ability to see how Twitter feels about any topic over the span of the past week. This will be returned back in the format: “Twitter feels [sentiment = (very negative, somewhat negative, neutral, somewhat positive, very positive)] about [keyword] last week, [sentiment] yesterday, and [sentiment] today.” This type of analysis can be applied to many current topics such as celebrity trends, for example how Twitter reacts to Tiger Woods DUI by using the keywords Tiger Woods, politics, or any topic the user can think of.
  
# Running the Code
Included in our submission is lambda_handler.py (python 2.7), ModelSelection.py (python 3.6), and intent_schema. 

The lambda_handler is the file that gets called for AWS Lambda whenever an Alexa user uses our skill. In order to successfully deploy this on AWS Lambda we also needed to include all packages that weren't installed on the lambda instance inherently. For our project this was sklearn, numpy, scipy, and python-twitter. Our final product to be uploaded to lambda is a zipped file containing all folders for all of the packages, pickle files of the model and the vectorizer, as well as the lambda handler file. The final development zipped is 54MB and is currently on our github at https://github.com/irvin93d/MoodSwing. In order to upload this file into lambda, it needs to be first uploaded to an S3 bucket on AWS and then loaded into lambda from there. This means the steps to run our code are quite complex. 

To generate the pickle files simply run: 
python3 ModelSelection.py 
This will do all of the necessary training and select the best model based on basic metrics and store it into pickle files representing the model and vectorizer. 

To run the lambda code, an S3 bucket must be created and the zip file named lambda-sklearn.zip needs to be uploaded to it. Then a lambda function needs to be created and the kernel has to be set to Python 2.7. Copy the bucket location and file name (lambda-sklearn.zip) into the prompt after selecting to upload code from S3. Once this is fully uploaded, the lambda function will respond with sentiment analysis to any requests in the form of a properly formatted JSON file.

The next step for developing it with an Amazon Alexa Skill is to create a skill template in the Amazon Developer Portal. The proper interaction model which maps out which spoken instances will map to which intent as well as where to get the key word extraction from is stored in a file named intent_schema.json. Copy the intent schema into the appropriate location on the developer portal. After you have built the model and enabled the skill for testing, congratulations! You are now officially an Alexa Skill developer.