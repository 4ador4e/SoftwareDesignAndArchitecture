from flask import Flask, render_template, request, redirect, url_for, session, flash
from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')

app = Flask(__name__)
app.secret_key = 'your_secret_key'
users = {}


class DataFetcherSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DataFetcherSingleton, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.base_url = "https://www.mse.mk/mk/stats/symbolhistory/"

    def fetch_symbol_codes(self):
        url = f"{self.base_url}alk"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        meni = soup.find('select', {'id': 'Code'})
        return [option['value'] for option in meni.find_all('option') if option['value'].isalpha()]

    def fetch_data(self, kod):
        url = f"{self.base_url}{kod}"
        try:
            response = requests.get(url)
            print(response.text)
            data = pd.read_html(response.text)[0]
            data["kod"] = kod
            return data
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None


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


def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi



def calculate_stochastic_oscillator(data, period=14):
    low_min = data['Low'].rolling(window=period).min()
    high_max = data['High'].rolling(window=period).max()
    stoch = 100 * (data['Close'] - low_min) / (high_max - low_min)
    return stoch


def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
    fast_ema = data['Close'].ewm(span=fast_period, adjust=False).mean()
    slow_ema = data['Close'].ewm(span=slow_period, adjust=False).mean()
    macd = fast_ema - slow_ema
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    return macd, signal


@app.route('/')
def index():
    return redirect(url_for('signup'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        repassword = request.form['repassword']

        if password != repassword:
            flash('Passwords do not match', 'error')
        elif email in users:
            flash('Email already exists', 'error')
        else:
            users[email] = password
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email in users and users[email] == password:
            session['logged_in'] = True
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    fetcher = DataFetcherSingleton()
    stock_data = fetcher.fetch_data('alk')


    if stock_data is not None:

        if 'Close' in stock_data.columns and 'High' in stock_data.columns and 'Low' in stock_data.columns:
            stock_data['RSI'] = calculate_rsi(stock_data)
            stock_data['Stochastic Oscillator'] = calculate_stochastic_oscillator(stock_data)
            macd, signal = calculate_macd(stock_data)
            stock_data['MACD'] = macd
            stock_data['MACD Signal'] = signal
            stock_data_html = stock_data.to_html(classes='table table-striped')
        else:
            stock_data_html = "Required data columns (Close, High, Low) not found."
    else:
        stock_data_html = "No data available."

    analyzer = NewsSentimentAnalyzerSingleton()
    news = analyzer.fetch_news()

    sentiments = analyzer.analyze_sentiment(news)
    news_with_sentiments = [{'Title': n['Title'], 'Sentiment': s} for n, s in zip(news, sentiments)]

    return render_template('dashboard.html', user=session.get('user'), stock_data_html=stock_data_html,
                           news=news_with_sentiments)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
