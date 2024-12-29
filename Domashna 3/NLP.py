import pandas as pd
import requests
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk


nltk.download('vader_lexicon')

def fetch_news_mse():
    url = "https://www.mse.mk/mk/news/latest"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Не може да се пристапи до веб-страницата: {url}")

    soup = BeautifulSoup(response.text, 'html.parser')
    news = []

    for item in soup.find_all('div', class_='container-middle'):
        title = item.find('div', class_='col-md-11').text.strip()
        date = item.find('div', class_='col-md-1').text.strip()
        news.append({'Title': title, 'Date': date})

    return news



def analyze_sentiment(news_list):
    analyzer = SentimentIntensityAnalyzer()
    sentiments = []

    for news in news_list:
        sentiment_score = analyzer.polarity_scores(news['Title'])
        if sentiment_score['compound'] > 0.05:
            sentiments.append("Positive")
        elif sentiment_score['compound'] < -0.05:
            sentiments.append("Negative")
        else:
            sentiments.append("Neutral")

    return sentiments



def generate_signal(sentiments):
    sentiment_counts = pd.Series(sentiments).value_counts()
    positive = sentiment_counts.get("Positive", 0)
    negative = sentiment_counts.get("Negative", 0)
    neutral = sentiment_counts.get("Neutral", 0)

    print(f"Positive: {positive}, Negative: {negative}, Neutral: {neutral}")

    if positive > negative:
        return "BUY"
    elif negative > positive:
        return "SELL"
    else:
        return "HOLD"



if __name__ == "__main__":
    try:

        news_data = fetch_news_mse()
        if not news_data:
            raise Exception("Не се пронајдени вести.")

        df = pd.DataFrame(news_data)

        df['Sentiment'] = analyze_sentiment(news_data)

        recommendation = generate_signal(df['Sentiment'])
        print(f"Recommendation: {recommendation}")

        df.to_csv('sentiment_analysis_mse.csv', index=False)
        print("Резултатите се зачувани во 'sentiment_analysis_mse.csv'")

    except Exception as e:
        print(f"Се случи грешка: {e}")
