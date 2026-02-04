from flask import Flask, jsonify
import requests
import pandas as pd
from ta.momentum import RSIIndicator
import time

app = Flask(__name__)

ALPHA_API_KEY = "ZMCPF2U2C6A35FJ9"
FALLBACK_PRICE = 2000

# Cache mekanizması: son veri ve zaman
cache = {
    "timestamp": 0,
    "price": FALLBACK_PRICE,
    "rsi": None
}

CACHE_TTL = 60  # saniye, 1 dakika cache

@app.route("/")
def home():
    return "Bot çalışıyor 🚀"

@app.route("/healthz")
def health():
    return "OK", 200

@app.route("/gold")
def gold():
    current_time = time.time()
    # Cache geçerli ise doğrudan dön
    if current_time - cache["timestamp"] < CACHE_TTL:
        return jsonify({
            "price": cache["price"],
            "RSI_4h": cache["rsi"],
            "warning": "Cache kullanıldı"
        })

    try:
        url = f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=XAU&to_symbol=USD&interval=60min&apikey={ALPHA_API_KEY}&outputsize=compact"

        for attempt in range(3):  # 3 defa dene
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                break
            time.sleep(5)
        else:
            raise Exception("AlphaVantage veri alınamadı (retry limit aşıldı)")

        if "Time Series FX (60min)" not in data:
            raise Exception("AlphaVantage JSON format hatası")

        time_series = data["Time Series FX (60min)"]

        # 1H kapanış fiyatları, eski -> yeni
        df = pd.DataFrame([float(v["4. close"]) for k, v in sorted(time_series.items())], columns=['close'])

        # 4H mum oluştur
        df_4h = df.groupby(df.index // 4).last()
        if len(df_4h) < 14:
            raise Exception("Yeterli veri yok, RSI hesaplanamadı")

        rsi = RSIIndicator(close=df_4h['close'], window=14).rsi()
        latest_price = round(df_4h['close'].iloc[-1], 2)
        latest_rsi = round(rsi.iloc[-1], 2)

        # Cache güncelle
        cache["timestamp"] = current_time
        cache["price"] = latest_price
        cache["rsi"] = latest_rsi

        return jsonify({"price": latest_price, "RSI_4h": latest_rsi})

    except Exception as e:
        # Hata durumunda fallback + cache güncelle
        cache["timestamp"] = current_time
        cache["price"] = FALLBACK_PRICE
        cache["rsi"] = None

        return jsonify({
            "price": FALLBACK_PRICE,
            "RSI_4h": None,
            "warning": str(e)
        }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
