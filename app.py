from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import pandas as pd
from ta.momentum import RSIIndicator

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot çalışıyor 🚀"

@app.route("/healthz")
def health():
    return "OK", 200

@app.route("/gold")
def gold():
    try:
        # Investing.com XAUUSD Historical Data (4H)
        url = "https://www.investing.com/instruments/HistoricalDataAjax"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest"
        }
        params = {
            "curr_id": "8830",        # XAUUSD ID
            "smlID": "20332",
            "header": "XAU/USD Historical Data",
            "st_date": "01/01/2026",  # Başlangıç tarihi (dd/mm/yyyy)
            "end_date": "04/02/2026", # Bitiş tarihi
            "interval_sec": "Hourly", # 4H yok, en yakın 1H alıyoruz
            "sort_col": "date",
            "sort_ord": "DESC",
            "action": "historical_data"
        }

        r = requests.post(url, headers=headers, data=params)
        soup = BeautifulSoup(r.text, "lxml")
        table = soup.find("table")
        df = pd.read_html(str(table))[0]

        # Kapanış fiyatlarını float yap
        df['Price'] = df['Price'].str.replace(',', '').astype(float)
        close_prices = df['Price']

        # RSI hesapla (14 periyotluk)
        rsi = RSIIndicator(close=close_prices, window=14).rsi()

        latest_price = round(close_prices.iloc[0], 2)
        latest_rsi = round(rsi.iloc[0], 2)

        return jsonify({"price": latest_price, "RSI_4h": latest_rsi})

    except Exception as e:
        return jsonify({"error": "Veri alınamadı", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
