import sys
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from newsapi import NewsApiClient
from datetime import date, timedelta, datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

sia = SentimentIntensityAnalyzer()
pd.set_option('display.max_colwidth',1000)

def get_sources(category = None):
    newsapi = NewsApiClient(api_key='94ce21a1a53f4684a21af8a92fb7a0b4')
    sources = newsapi.get_sources()
    if category is not None:
        rez = [source['id'] for source in sources['sources'] if source['category'] == category and source['language'] == 'en']
    else:
        rez = [source['id'] for source in sources['sources'] if source['language'] == 'en']
    return rez

def get_articles_sentiments(keywrd, startd, sources_list = None, show_all_articles = False):
  newsapi = NewsApiClient(api_key='94ce21a1a53f4684a21af8a92fb7a0b4')
  if type(startd)== str :
    my_date = datetime.strptime(startd,'%d-%b-%Y')
  else:
    my_date = startd
  #If the sources list is provided - use it
  if sources_list:
    articles = newsapi.get_everything(q = keywrd, from_param = my_date.isoformat(), to = (my_date + timedelta(days = 1)).isoformat(), language="en", sources = ",".join(sources_list), sort_by="relevancy", page_size = 100)
  else:
    articles = newsapi.get_everything(q = keywrd, from_param = my_date.isoformat(),to = (my_date + timedelta(days = 1)).isoformat(), language="en", sort_by="relevancy", page_size = 100)
  article_content = ''
  date_sentiments = {}
  date_sentiments_list = []
  seen = set()
  for article in articles['articles']:
    if str(article['title']) in seen:
      continue
    else:
      seen.add(str(article['title']))
    article_content = str(article['title']) + '. ' + str(article['description'])
    #Get the sentiment score
    sentiment = sia.polarity_scores(article_content)['compound']
  
    date_sentiments.setdefault(my_date, []).append(sentiment)
    date_sentiments_list.append((sentiment, article['url'], article['title'],article['description']))
    date_sentiments_l = sorted(date_sentiments_list, key = lambda tup: tup[0],reverse = True)
    sent_list = list(date_sentiments.values())[0]
    #Return a dataframe with all sentiment scores and articles  
    return pd.DataFrame(date_sentiments_list, columns=['Sentiment','URL','Title','Description'])

return_articles = get_articles_sentiments(keywrd= 'google', startd = '31-Aug-2025', sources_list = None, show_all_articles= True)
return_articles.Sentiment.hist(bins=30,grid=False)
return_articles.sort_values(by='Sentiment', ascending=True)[['Sentiment','URL']].head(2)

print(return_articles.Sentiment.mean())
print(return_articles.Sentiment.count())
print(return_articles.Description[0])