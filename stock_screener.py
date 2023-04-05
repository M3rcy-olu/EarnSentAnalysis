import datetime as dt
import pandas as pd
import requests
from bs4 import BeautifulSoup

#Goes through the earnings calender on MarketWatch and returns the ticker symbols of stocks that have earnings within a week from the current day
def generateTickers():
    #establishes connection with MarketWatch
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
    }
    #Loads webpage
    url = 'https://www.marketwatch.com/tools/earningscalendar'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    #finds the html component holding the table which earnings information are stored
    tabpane = soup.find('div', 'tabpane')
    #Finds the subtables for each day
    earning_tables = tabpane.find_all('div', {'id': True})

    #Determines the current day and the date 7 days ahead
    today = dt.date.today()
    year = str(today)[:4]

    earnings_in_a_week = []
    dfs= {}

    raw_tickers = []
    tickers = []

    #Determines which tables contain earnings within a week
    for earning_table in earning_tables:
        #Filters out dates with earnings
        if not 'Sorry, this date currently does not have any earnings announcements scheduled.' in earning_table.text:
            earning_date = earning_table['id'].replace('page', '') #extracts the date of each subtable
            #Converts the date to a datetime format to be compared to the current date 
            earning_month = earning_date[:3]
            earning_day = earning_date[3:]
            earning_date = dt.datetime.strptime(earning_month + ' ' + str(earning_day) + ' ' + year, '%b %d %Y')
            earning_date = earning_date.date()

            #finds how many days are between each subtable date and the current day
            days_between = earning_date - today
            days_between = str(days_between)
            #converts days_between to an integers to be used in the if statement
            if 'day' in days_between:
                split_string = days_between.split(' ')
                int_days_between = int(split_string[0])
                #adds the subtable to the list of earning in a week
                if int_days_between <= 7 and int_days_between > 0:
                    earnings_in_a_week.append(earning_table)

    for earning_table in earnings_in_a_week:
        #extracts data under the subtable by converting all data into one long string
        table = str(earning_table.find_all('td'))

        #extracts the components holding the ticker prices
        table = table.split(',')
        index = 1
        while(index <= len(table)-5):
            raw_tickers.append(table[index])
            index+=6
    #removes html components 
    for ticker in raw_tickers:
        format_ticker = ticker[5:]
        split_ticker = format_ticker.split('<')
        return_ticker = split_ticker[0]
        if not '.' in return_ticker:    
            tickers.append(return_ticker)
    return tickers

    




    

     

        
        
   