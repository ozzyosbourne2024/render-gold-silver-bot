import requests
from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot çalışıyor 🚀"

@app.route("/gold")
def gold_price():
    url = "https://api.metals.live/v1/spot"
    data = requests.get(url, timeout=10).json()
    gold = next(item[1] for item in data if item[0] == "gold")
    return f"Altın (ons): {gold} USD"

@app.route("/healthz")
def health():
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
