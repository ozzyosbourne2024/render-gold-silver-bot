from flask import Flask, jsonify
import yfinance as yf
from ta.momentum import RSIIndicator
import pandas as pd

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot çalışıyor 🚀"

@app.route("/healthz")
def health():
    return "OK", 200

@app.route("/gold")
def gold():
    # XAUUSD verisi, 4 saatlik mumlar, son 7 gün
    data = yf.download("XAUUSD=X", interval="4h", period="7d")
    
    if data.empty:
        return jsonify({"error": "Veri alınamadı"}), 500

    # Kapanış fiyatları
    close_prices = data['Close']

    # RSI hesapla (14 periyotluk)
    rsi = RSIIndicator(close=close_prices, window=14).rsi()

    # Son fiyat ve RSI
    latest_price = round(close_prices[-1], 2)
    latest_rsi = round(rsi[-1], 2)

    return jsonify({
        "price": latest_price,
        "RSI_4h": latest_rsi
    })

# Local test ve prod uyumlu
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
