# MoodSwings
Project - Sentiment Analysis
Title - MoodSwings
Members - Kyle Vigil, Alex Boyd, Jonathan Ohlsson, Duane Irvin
 
# About
We are giving users of Alexa the ability to gauge Twitter (and possibly other websites depending on how far we get) about Twitter users' general feelings towards any topic (for instance, feelings about Coca-Cola, Donald Trump, CNN, etc.). Alexa will report back the general sentiment comparing a few different time periods (last month vs last week vs this week) specified by the user upon query.
 
# Technologies
We are developing a skill for Amazon Alexa that allows users of Alexa to gain insight into the current and past sentiment Twitter has to any number of topics. In order to do this, we are running a program on AWS Lambda which is the standard connection for Alexa Skills. This allows the command that is run through Alexa to query our program with the appropriate parameters and our application will return back the desired sentiment analysis. The application running on Lambda will be written in Python and will connect to the Twitter API through a standard package, either tweepy or something similar. This package along with approved Twitter API access allows us to query Tweets from the past two weeks as fast as possible. Given these tweets we will use NLTK or similar package to perform sentiment analysis on the tweets for the given time period and/or topic. A sample use case is seen below:

 
# Purpose
Our goal is to be able to give Alexa users the ability to see how Twitter feels about any topic over the span of the past two weeks. This will be returned back in a format similar to: “Twitter feels [sentiment = (very negative, somewhat negative, neutral, somewhat positive, very positive)] about [keyword] last week, [sentiment] this week, and [sentiment] today.” This type of analysis can be applied to many current topics such as celebrity trends, for example how Twitter reacts to Tiger Woods DUI by using the keywords Tiger Woods, politics, or any topic the user can think of. 
  
# Timeline
Our first step is getting the access to the Twitter API and retrieving the appropriate tweets given keywords. The next logical step is doing any preprocessing of the Tweets before the sentiment analysis. NLTK has a sentiment analysis function that can serve as a placeholder to test our preprocessing during this phase. Because we can use the NLTK placeholder, we can set up the Alexa Skill at this point in parallel with the development of our own sentiment analysis engine. Once our sentiment analysis function is complete, we can seamlessly swap it in for the NLTK one in our Alexa Skill. The final step is pushing the finished product to the official Amazon Skill app store. 
