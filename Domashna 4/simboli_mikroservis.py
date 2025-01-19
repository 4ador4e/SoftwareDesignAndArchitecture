from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

BASE_URL = "https://www.mse.mk/mk/stats/symbolhistory/"


@app.route('/symbol-codes', methods=['GET'])
def fetch_symbol_codes():
    try:
        url = f"{BASE_URL}alk"
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        meni = soup.find('select', {'id': 'Code'})

        if not meni:
            return jsonify({"error": "kod 'Code' ne e pronajden"}), 404

        codes = [option['value'] for option in meni.find_all('option') if option['value'].isalpha()]
        return jsonify({"kodovi": codes})

    except Exception as e:
        return jsonify({"error": f"Nemozi da se zemat kodovite: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(port=5001)
