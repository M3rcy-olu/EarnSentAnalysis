import nltk
from textblob import TextBlob
from newspaper import Article

def calcSentiment(url):
    article = Article(url)

    article.download()
    article.parse()
    article.nlp()

    text = article.text

    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity # -1 to 1 [negative to positive]
    return sentiment

urls = ['https://www.investors.com/news/technology/sq-stock-buy-now',
        'https://techcrunch.com/2022/04/05/block-cash-app-data-breach/',
        'https://www.marketwatch.com/story/block-inc-stock-underperforms-tuesday-when-compared-to-competitors-01649193697-8bc7c8d5776f',
        ]
sentiment_values = []
for site in urls:
    sentiment = calcSentiment(site)
    sentiment_values.append(sentiment)

sum = 0
for value in sentiment_values:
    sum+= value
average_sentiment = sum/len(sentiment_values)

print(sentiment_values)
print(average_sentiment)

