from flask import Flask, jsonify
import pandas as pd
import time
import yfinance as yf
from ta.momentum import RSIIndicator

app = Flask(__name__)

# Cache: fiyat ve RSI
cache = {
    "timestamp": 0,
    "price": 2000,  # fallback
    "RSI_4h": None
}

CACHE_TTL = 60 * 60  # 1 saat: 4H için yeterli

@app.route("/")
def home():
    return "Bot çalışıyor 🚀"

@app.route("/healthz")
def health():
    return "OK", 200

@app.route("/gold")
def gold():
    current_time = time.time()

    # Cache geçerli ise direkt dön
    if current_time - cache["timestamp"] < CACHE_TTL:
        return jsonify({
            "price": cache["price"],
            "RSI_4h": cache["RSI_4h"],
            "warning": "Cache kullanıldı"
        })

    # Fiyat verisini yfinance ile al
    try:
        # XAU/USD 4H, son 100 bar
        data = yf.download("XAUUSD=X", interval="4h", period="30d")
        if data.empty:
            raise Exception("Veri alınamadı")

        close_prices = data['Close']
        latest_price = round(close_prices[-1], 2)

        # RSI hesapla (14 periyot)
        rsi = RSIIndicator(close=close_prices, window=14).rsi()
        latest_rsi = round(rsi[-1], 2)

        # Cache güncelle
        cache["price"] = latest_price
        cache["RSI_4h"] = latest_rsi
        cache["timestamp"] = time.time()

        return jsonify({
            "price": latest_price,
            "RSI_4h": latest_rsi
        })

    except Exception as e:
        # Fallback
        return jsonify({
            "price": cache["price"],
            "RSI_4h": cache["RSI_4h"],
            "warning": f"Veri alınamadı: {str(e)}"
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
