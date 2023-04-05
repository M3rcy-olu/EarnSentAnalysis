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
print("running")
for ticker in raw_tickers:
    url = finviz_url + ticker

    req = Request(url = url, headers={'user-agent': 'my-app'})
    try:
        response = urlopen(req)
        list_tickers.append(ticker)
    except urllib.error.URLError:
        raw_tickers.remove(ticker)

#creates a dictionary of news tables for each ticker

for i in range(0, len(list_tickers), 5):
    split_list = list_tickers[i:i+5]
grouped_tickers.append(split_list)

save_number = 1
for tickers in grouped_tickers:
    news_tables = {}   
    for ticker in tickers:
        url = finviz_url + ticker

        req = Request(url = url, headers={'user-agent': 'my-app'})
        response = urlopen(req)

        html = BeautifulSoup(response, 'html')
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

    #Next is to apply sentiment analysis on titles
    #figure out how to apply sentiment analysis on the acutall articles which we could do by following the link to each article then using simple sentiment
    #finally we want to return the tickers with the most exteme sentiments 
    df = pd.DataFrame(parsed_data, columns=['ticker', 'date', 'time', 'title'])
    vader = SentimentIntensityAnalyzer()
    f = lambda title: vader.polarity_scores(title)['compound']
    df['compound'] = df['title'].apply(f)
    df['date'] = pd.to_datetime(df.date).dt.date
    print(df)
    print(df['ticker'])
'''
    plt.figure(figsize = (10,8))

    mean_df = df.groupby(['ticker','date']).mean()
    mean_df = mean_df.unstack()
    mean_df = mean_df.xs('compound', axis='columns').transpose()
    mean_df.plot(kind='bar')
    plt.savefig(fname = 'ticker_earnings_sentiment_set' + str(save_number))
    save_number+=1'''






    

    