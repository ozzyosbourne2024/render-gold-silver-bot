from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot çalışıyor 🚀"
@app.route("/healthz")
def healthz():
    return "ok", 200

