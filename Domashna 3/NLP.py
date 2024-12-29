import pandas as pd
import requests
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Преземање на потребните ресурси за VADER
nltk.download('vader_lexicon')


# Функција за собирање вести преку веб-скрепирање
def fetch_news_mse():
    url = "https://www.mse.mk/mk/news/latest"  # Страница со најнови вести
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Не може да се пристапи до веб-страницата: {url}")

    soup = BeautifulSoup(response.text, 'html.parser')
    news = []

    # Пример структура за Македонската берза
    for item in soup.find_all('div', class_='container-middle'):  # Проверете го точниот клас
        title = item.find('div', class_='col-md-11').text.strip()  # Земи насловот
        date = item.find('div', class_='col-md-1').text.strip()  # Земи датум
        news.append({'Title': title, 'Date': date})

    return news


# Функција за анализа на сентимент
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


# Функција за генерирање сигнал
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


# Главна програма
if __name__ == "__main__":
    try:
        # Собирање вести
        news_data = fetch_news_mse()
        if not news_data:
            raise Exception("Не се пронајдени вести.")

        # Создавање DataFrame
        df = pd.DataFrame(news_data)

        # Анализа на сентимент
        df['Sentiment'] = analyze_sentiment(news_data)

        # Генерирање сигнал
        recommendation = generate_signal(df['Sentiment'])
        print(f"Recommendation: {recommendation}")

        # Зачувување на резултатите
        df.to_csv('sentiment_analysis_mse.csv', index=False)
        print("Резултатите се зачувани во 'sentiment_analysis_mse.csv'")

    except Exception as e:
        print(f"Се случи грешка: {e}")
