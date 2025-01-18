import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator
from ta.trend import MACD, CCIIndicator, SMAIndicator, EMAIndicator
import numpy as np

class IndicatorAnalyzerSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(IndicatorAnalyzerSingleton, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        pass

    def apply_indicators(self, df):
        close = df['Close']
        high = df['High']
        low = df['Low']

        df = df.dropna()

        rsi = RSIIndicator(close=close, window=14)
        df['RSI'] = rsi.rsi()
        df['Signal_RSI'] = df['RSI'].apply(lambda x: 'Buy' if x < 30 else ('Sell' if x > 70 else 'Hold'))

        stoch = StochasticOscillator(high=high, low=low, close=close, window=14, smooth_window=3)
        df['Stoch_%K'] = stoch.stoch()
        df['Stoch_%D'] = stoch.stoch_signal()
        df['Signal_Stoch'] = df.apply(lambda row: 'Buy' if row['Stoch_%K'] > row['Stoch_%D'] else 'Sell', axis=1)

        macd = MACD(close=close)
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['Signal_MACD'] = df.apply(lambda row: 'Buy' if row['MACD'] > row['MACD_Signal'] else 'Sell', axis=1)

        return df
