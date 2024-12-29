import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator
from ta.trend import MACD, CCIIndicator, SMAIndicator, EMAIndicator
import numpy as np


def calculate_wma(data, window):
    weights = np.arange(1, window + 1)
    return data.rolling(window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)


def calculate_hma(data, window):
    half_length = int(window / 2)
    sqrt_length = int(np.sqrt(window))
    wma_half = calculate_wma(data, half_length)
    wma_full = calculate_wma(data, window)
    diff = 2 * wma_half - wma_full
    return calculate_wma(diff, sqrt_length)


def calculate_kama(data, window, fast=2, slow=30):
    volatility = abs(data.diff())
    efficiency_ratio = abs(data.diff(window)) / volatility.rolling(window).sum()
    smoothing_constant = (efficiency_ratio * (2 / (fast + 1) - 2 / (slow + 1)) + 2 / (slow + 1)) ** 2
    kama = [data.iloc[0]]
    for i in range(1, len(data)):
        kama.append(kama[-1] + smoothing_constant.iloc[i] * (data.iloc[i] - kama[-1]))
    return pd.Series(kama, index=data.index)


def apply_indicators(df):
    close = df['Close']
    high = df['High']
    low = df['Low']

    print(close)

    df = df.dropna()

    rsi = RSIIndicator(close=df['Close'], window=14)
    df['RSI'] = rsi.rsi()
    df['Signal_RSI'] = df['RSI'].apply(lambda x: 'Buy' if x < 30 else ('Sell' if x > 70 else 'Hold'))

    stoch = StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close'], window=14, smooth_window=3)
    df['Stoch_%K'] = stoch.stoch()
    df['Stoch_%D'] = stoch.stoch_signal()
    df['Signal_Stoch'] = df.apply(lambda row: 'Buy' if row['Stoch_%K'] > row['Stoch_%D'] else 'Sell', axis=1)

    macd = MACD(close=df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    df['Signal_MACD'] = df.apply(lambda row: 'Buy' if row['MACD'] > row['MACD_Signal'] else 'Sell', axis=1)

    cci = CCIIndicator(high=df['High'], low=df['Low'], close=df['Close'], window=20)
    df['CCI'] = cci.cci()
    df['Signal_CCI'] = df['CCI'].apply(lambda x: 'Buy' if x < -100 else ('Sell' if x > 100 else 'Hold'))

    williams = WilliamsRIndicator(high=df['High'], low=df['Low'], close=df['Close'], lbp=14)
    df['Williams_%R'] = williams.williams_r()
    df['Signal_Williams'] = df['Williams_%R'].apply(lambda x: 'Buy' if x < -80 else ('Sell' if x > -20 else 'Hold'))

    sma = SMAIndicator(close=close, window=50)
    df['SMA'] = sma.sma_indicator()

    ema = EMAIndicator(close=close, window=50)
    df['EMA'] = ema.ema_indicator()

    df['WMA'] = calculate_wma(close, 50)

    df['HMA'] = calculate_hma(close, 50)

    df['KAMA'] = calculate_kama(close, 10)

    return df


def plot_indicators(df, timeframe):
    plt.figure(figsize=(14, 6))
    plt.plot(df['Close'], label=f'{timeframe} Close Price', color='blue')
    plt.plot(df['SMA'], label='SMA', color='orange')
    plt.plot(df['EMA'], label='EMA', color='purple')
    plt.plot(df['WMA'], label='WMA', color='green')
    plt.plot(df['HMA'], label='HMA', color='red')
    plt.plot(df['KAMA'], label='KAMA', color='brown')
    plt.title(f"{timeframe} Moving Averages")
    plt.legend()
    plt.show()


if __name__ == '__main__':
    ticker = "TSLA"
    data = yf.download(ticker, start="2022-01-01", end="2023-12-31")

    data_day = data
    data_week = data.resample('W').last()
    data_month = data.resample('M').last()

    data_day = apply_indicators(data_day)
    data_week = apply_indicators(data_week)
    data_month = apply_indicators(data_month)

    plot_indicators(data_day, "1 Day")
    plot_indicators(data_week, "1 Week")
    plot_indicators(data_month, "1 Month")

    data_day.to_csv('signals_day.csv', index=True)
    data_week.to_csv('signals_week.csv', index=True)
    data_month.to_csv('signals_month.csv', index=True)
