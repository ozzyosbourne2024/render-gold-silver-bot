from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot çalışıyor 🚀"

@app.route("/healthz")
def health():
    return "OK", 200

@app.route("/gold")
def gold():
    # Örnek: Sabit altın fiyatı. 
    # Daha sonra gerçek API ile değiştirebilirsin
    return jsonify({"price": 2000})

# Bu satır hem local test hem de Render prod ile uyumlu
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

