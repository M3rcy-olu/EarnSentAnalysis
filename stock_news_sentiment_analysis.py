#finviz is a great platform that contains all the articles written about a stock
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from difflib import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import urllib.request, urllib.parse, urllib.error
import stock_screener as sc
import datetime as dt
import matplotlib.pyplot as plt


finviz_url = 'https://finviz.com/quote.ashx?t='
#generated using a stock screener to screen for stocks within one week from earnings
raw_tickers = sc.generateTickers()

list_tickers = []
removed_tickers = []
grouped_tickers = []

#tests which stock tickers can be found on finviz
for ticker in raw_tickers:
    url = finviz_url + ticker

    req = Request(url = url, headers={'user-agent': 'my-app'})
    try:
        response = urlopen(req)
        list_tickers.append(ticker)
    except urllib.error.URLError:
        raw_tickers.remove(ticker)
print("Finished gathering earnings data")

#creates a dictionary of news tables for each ticker
news_tables = {}   
for ticker in list_tickers:
    url = finviz_url + ticker

    req = Request(url = url, headers={'user-agent': 'my-app'})
    response = urlopen(req)

    html = BeautifulSoup(response, features="lxml")
    news_table = html.find(id='news-table')
    news_tables[ticker] = news_table

#Organizes table information so that the table information ins broken up into list containing the stock ticker, date, time and new headline
raw_parsed_data = []
parsed_data = []
for ticker, news_table in news_tables.items():
    
    for row in news_table.findAll('tr'):

        title = row.a.text
        date_data = row.td.text.split(' ')

        if len(date_data) == 1:
            time = date_data[0]
        else: 
            date = date_data[0]
            time = date_data[1]
        raw_parsed_data.append([ticker, date, time, title])

#filters the news information to only contain that within a two week period
current_day = dt.date.today()
for item in raw_parsed_data:
    item_date = item[1]
    item_date_data = item_date.split('-')
    month = item_date_data[0]
    day = item_date_data[1]
    year = '20' + item_date_data[2]
    article_date = dt.datetime.strptime(month + ' ' + day + ' ' + year, '%b %d %Y')
    article_date = article_date.date()
    days_between = current_day - article_date
    days_between = str(days_between)
    int_days_between = 0
    if 'day' in days_between:
        days_between_data = days_between.split(' ')
        int_days_between = days_between_data[0]
    if int(int_days_between) <= 21:
        parsed_data.append(item)
print("Finished optimizing data")

 
df = pd.DataFrame(parsed_data, columns=['ticker', 'date', 'time', 'title'])
vader = SentimentIntensityAnalyzer()
f = lambda title: vader.polarity_scores(title)['compound']
df['compound'] = df['title'].apply(f)
df['date'] = pd.to_datetime(df.date).dt.date
#averages the sentiment of each article for each ticker
ticker_average_sentiments = [] # list that contains the ticker associated with its average sentiment
current_index = 0
graph_indexer = 0
checker = df['ticker'][current_index] #checker used to see if the tickers analyzed is the same ticker that the average is being calculated for
sum = 0
num_articles = 0 
#the following goes through the data frame from above and for eacher ticker checks if it equals the checker
#if so the sentiment of its article is added to sum and the number or articles increases by one
#if not it means we are on a new ticker thus, the program first calculates the average of the previous ticker, then resets sum and num_articles to zero then being colleting the sentiment for the average of the next ticker
for ticker in df['ticker']:
    if ticker == checker:
        sum += df['compound'][current_index]
        num_articles += 1
    else:
        average = sum/num_articles
        ticker_average_sentiments.append([checker, graph_indexer+1, average])
        graph_indexer +=3
        sum = 0
        num_articles = 0
        checker = df['ticker'][current_index]
        sum += df['compound'][current_index]
        num_articles += 1
    current_index += 1
#calculates the average of the last ticker
ticker_average_sentiments.append([df['ticker'][len(df.index)-1], graph_indexer+1, sum/num_articles])
#creates a data fram with the ticker and average sentiment
df_2 = pd.DataFrame(ticker_average_sentiments, columns=['ticker', 'index', 'sentiment'])
print("Generating Tables")

#Print Data as a graph
plt.figure(figsize = (25,20))
graph = df_2.plot(kind='scatter', x = 'index', y = 'sentiment')
plt.savefig(fname = 'two-week_sentiment_stock_projections' + str(dt.date.today()) + 'unlabeled')
for i in range(0, len(df_2.index)):
    txt = df_2['ticker'][i]
    graph.annotate(txt, (df_2['index'][i]+0.05, df_2['sentiment'][i]), fontsize = 5)
plt.savefig(fname = 'two-week_sentiment_stock_projections' + str(dt.date.today()))
print("Analysis Complete!")

#The Project is Complete 5-24-22 M.D






    

    