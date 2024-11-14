import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
import calendar

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

base_url = "https://www.mse.mk/mk/stats/symbolhistory/"

def fetch_symbol_codes():
    url = f"{base_url}alk"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    meni = soup.find('select', {'id': 'Code'})
    kodovi = [option['value'] for option in meni.find_all('option') if option['value'].isalpha()]
    return kodovi

def fetch_data(kod):
    url = f"{base_url}{kod}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = pd.read_html(response.text)[0]
        data["kod"] = kod
        return data
    except Exception as e:
        print(f"Failed to retrieve data for {kod}: {e}")
        return None

if __name__ == '__main__':
    pocna = time.time()

    kodovi = fetch_symbol_codes()
    print(f"Found {len(kodovi)} symbol codes.")

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_data, kodovi))

    data = [result for result in results if result is not None]

    if data:
        df = pd.concat(data, ignore_index=True)
        df.to_csv("all_companies_data.csv", index=False)
        print("Saved to all_companies_data.csv.")
    else:
        print("No data fetched.")

    celaData = []

    for kod in kodovi:
        url = f"{base_url}{kod}"
        do = datetime.now()
        for i in range(10):
            godina = do.year
            if calendar.isleap(godina):
                od = do - timedelta(days=366)
            else:
                od = do - timedelta(days=365)
            params = {
                "FromDate": od.strftime("%d.%m.%Y"),
                "ToDate": do.strftime("%d.%m.%Y"),
            }
            try:
                response = requests.get(url,params=params, timeout=(3, 10))
                response.raise_for_status()
                d = pd.read_html(response.text)[0]
                d["kod"] = kod
                celaData.append(d)
                time.sleep(0.5)
            except Exception as e:
                print(f"Failed to retrieve data for {kod}: {e}")

    if celaData:
        df = pd.concat(celaData, ignore_index=True)
        df.to_csv("Sevkupno.csv", index=False)
        print("Saved to Sevkupno.csv.")

    zavrsi = time.time()
    duration_minutes = (zavrsi - pocna) / 60
    print(f"Time taken: {duration_minutes:.2f} minutes")