from flask import Flask, jsonify
import requests
import pandas as pd
from ta.momentum import RSIIndicator

app = Flask(__name__)

ALPHA_API_KEY = "ZMCPF2U2C6A35FJ9"  # AlphaVantage API key
FALLBACK_PRICE = 2000  # AlphaVantage veri gelmezse kullanılacak sabit fiyat

@app.route("/")
def home():
    return "Bot çalışıyor 🚀"

@app.route("/healthz")
def health():
    return "OK", 200

@app.route("/gold")
def gold():
    try:
        url = f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=XAU&to_symbol=USD&interval=60min&apikey={ALPHA_API_KEY}&outputsize=compact"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        # JSON alan yoksa fallback
        if "Time Series FX (60min)" not in data:
            return jsonify({
                "price": FALLBACK_PRICE,
                "RSI_4h": None,
                "warning": "AlphaVantage veri gelmedi, fallback fiyat kullanıldı"
            }), 200

        time_series = data["Time Series FX (60min)"]

        # 1H kapanış fiyatları, eski -> yeni
        df = pd.DataFrame([float(v["4. close"]) for k, v in sorted(time_series.items())], columns=['close'])

        # 4H mum oluşturmak için 4’lü gruplar (son fiyatı al)
        df_4h = df.groupby(df.index // 4).last()
        if len(df_4h) < 14:
            return jsonify({
                "price": FALLBACK_PRICE,
                "RSI_4h": None,
                "warning": "Yeterli veri yok, fallback fiyat kullanıldı"
            }), 200

        # RSI 14 periyot
        rsi = RSIIndicator(close=df_4h['close'], window=14).rsi()
        latest_price = round(df_4h['close'].iloc[-1], 2)
        latest_rsi = round(rsi.iloc[-1], 2)

        return jsonify({"price": latest_price, "RSI_4h": latest_rsi})

    except Exception as e:
        return jsonify({
            "price": FALLBACK_PRICE,
            "RSI_4h": None,
            "error": "Veri alınamadı",
            "details": str(e)
        }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
