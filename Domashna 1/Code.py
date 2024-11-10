import psycopg2
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
import os

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

url = "https://www.mse.mk/mk/stats/symbolhistory/alk"
response = requests.get(url)

if __name__ == '__main__':
    pocna = time.time()
    print(response.status_code)

    soup = BeautifulSoup(response.text, 'html.parser')
    meni = soup.find('select',{'id':'Code'})
    pom = meni.find_all('option')
    kodovi = []
    for i in range (len(pom)):
        if pom[i]['value'].isalpha():
            kodovi.append(pom[i]['value'])
    print(kodovi)

    base_url = "https://www.mse.mk/mk/stats/symbolhistory/"
    data = []

    for kod in kodovi:
        url = f"{base_url}{kod}"
        try:
            response = requests.get(url)
            response.raise_for_status()

            d = pd.read_html(response.text)[0]

            d["kod"] = kod

            data.append(d)

            time.sleep(1)
        
        except Exception as e:
            print(f"Failed to retrieve data for {kod}: {e}")
    
    df = pd.concat(data, ignore_index=True)
    df.to_csv("all_companies_data.csv", index=False)
    print("Saved to all_companies_data.csv.") 

    celaData = []

    for kod in kodovi:
        url = f"{base_url}{kod}"
        denes = datetime.now()
        for i in range(10):
            godina = denes.year
            od = denes - timedelta(days=365)
            try:
                response = requests.get(url,params = {"Od": od.strftime("%d.%m.%Y"), "Do": denes.strftime("%d.%m.%Y")},timeout=(3,10))
                response.raise_for_status()

                d = pd.read_html(response.text)[0]
                d["kod"] = kod

                celaData.append(d)

                time.sleep(1)
                denes = od
            except Exception as e:
                print(f"Failed to retrieve data for {kod}: {e}")

    df = pd.concat(celaData, ignore_index=True)
    df.to_csv("Sevkupno.csv", index=False)
    print("Saved to Sevkupno.csv.")

    zavrsi = time.time()

    duration_minutes = (zavrsi - pocna) / 60
    print(f"Time taken: {duration_minutes:.2f} minutes")