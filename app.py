from flask import Flask, jsonify
import requests
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
        # Binance API 4H mumlar
        url = "https://api.binance.com/api/v3/klines?symbol=XAUUSD_PERP&interval=4h&limit=100"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()

        # Kapanış fiyatlarını al
        close_prices = [float(candle[4]) for candle in data]
        df = pd.DataFrame(close_prices, columns=['close'])

        # RSI hesapla (14 periyot)
        rsi = RSIIndicator(close=df['close'], window=14).rsi()
        latest_price = round(df['close'].iloc[-1], 2)
        latest_rsi = round(rsi.iloc[-1], 2)

        return jsonify({"price": latest_price, "RSI_4h": latest_rsi})

    except Exception as e:
        return jsonify({"error": "Veri alınamadı", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

