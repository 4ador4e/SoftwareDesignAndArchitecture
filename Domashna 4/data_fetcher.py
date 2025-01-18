import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import calendar

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
        kodovi = [option['value'] for option in meni.find_all('option') if option['value'].isalpha()]
        return kodovi

    def fetch_data(self, kod):
        url = f"{self.base_url}{kod}"
        try:
            response = requests.get(url)
            data = pd.read_html(response.text)[0]
            data["kod"] = kod
            return data
        except Exception as e:
            return None

    def fetch_historical_data(self, kodovi):

        end_date = datetime.today()
        start_date = end_date - timedelta(days=365)

        historical_data = []


        for kod in kodovi:
            print(f"Fetching historical data for {kod}...")
            data = self.fetch_data(kod)

            if data is not None:

                data['Date'] = pd.to_datetime(data['Date'], format='%d-%m-%Y')

                data = data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]

                historical_data.append(data)
            else:
                print(f"Could not fetch data for {kod}.")

            time.sleep(1)

        if historical_data:
            all_data = pd.concat(historical_data, ignore_index=True)
            return all_data
        else:
            print("No data fetched.")
            return None

