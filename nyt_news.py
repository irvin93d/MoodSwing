from bs4 import BeautifulSoup
import requests
import json
from fetch_dataset import getSentiment
from nltk.sentiment.vader import SentimentIntensityAnalyzer


API_KEY = "1f06efa445634075b37476ab5065ebaf"

def _get_headlines():
    return requests.get("https://newsapi.org/v1/articles?source=the-new-york-times&sortBy=top&apiKey=" + API_KEY).json()

def _get_story(url):
    res = ""
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    text_divs = soup.find_all("p", {"class": "story-body-text"})
    for div in text_divs:
        res += " " + div.get_text()
    return res

def get_news():
    head = _get_headlines()
    articles = []
    for article in head['articles']:
        articles.append(_get_story(article['url']))
    
    # TODO Remove ---
    analyzer = SentimentIntensityAnalyzer()
    i = 0
    for article in articles:
        print(head['articles'][i]['title'])
        print(analyzer.polarity_scores(article))
        i += 1
    return articles

get_news()

