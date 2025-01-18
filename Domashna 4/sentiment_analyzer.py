import requests
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')

class NewsSentimentAnalyzerSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(NewsSentimentAnalyzerSingleton, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.base_url = "https://www.mse.mk/mk/news/latest"
        self.analyzer = SentimentIntensityAnalyzer()

    def fetch_news(self):
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        news = []
        for item in soup.find_all('div', class_='container-middle'):
            title = item.find('div', class_='col-md-11').text.strip()
            date = item.find('div', class_='col-md-1').text.strip()
            news.append({'Title': title, 'Date': date})
        return news

    def analyze_sentiment(self, news_list):
        sentiments = []
        for news in news_list:
            sentiment_score = self.analyzer.polarity_scores(news['Title'])
            if sentiment_score['compound'] > 0.05:
                sentiments.append("Positive")
            elif sentiment_score['compound'] < -0.05:
                sentiments.append("Negative")
            else:
                sentiments.append("Neutral")
        return sentiments

    def generate_signal(self, sentiments):
        sentiment_counts = pd.Series(sentiments).value_counts()
        positive = sentiment_counts.get("Positive", 0)
        negative = sentiment_counts.get("Negative", 0)
        neutral = sentiment_counts.get("Neutral", 0)

        if positive > negative:
            return "BUY"
        elif negative > positive:
            return "SELL"
        else:
            return "HOLD"
