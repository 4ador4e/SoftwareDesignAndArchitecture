from flask import Flask, request, jsonify
import requests
import pandas as pd

app = Flask(__name__)

BASE_URL = "https://www.mse.mk/mk/stats/symbolhistory/"


@app.route('/fetch-data', methods=['POST'])
def fetch_data():
    try:
        kod = request.json.get('kod')
        if not kod:
            return jsonify({"error": "Nedostiga 'kod'"}), 400

        url = f"{BASE_URL}{kod}"
        response = requests.get(url)
        response.raise_for_status()

        data = pd.read_html(response.text)[0]
        data["kod"] = kod

        return jsonify(data.to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": f"Ne uspesno se zedoja podatocite: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(port=5002)
