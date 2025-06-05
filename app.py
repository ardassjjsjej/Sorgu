from flask import Flask, jsonify, request
import json, yaml, logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["10 per minute"])

with open("config.json") as f:
    config = json.load(f)

logging.basicConfig(filename="logs/app.log", level=logging.INFO)

def load_data():
    if config["veri_kaynagi"].endswith(".json"):
        with open(config["veri_kaynagi"], "r", encoding="utf-8") as f:
            return json.load(f)
    elif config["veri_kaynagi"].endswith(".yaml"):
        with open(config["veri_kaynagi"], "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return []

@app.route("/capiapi/<kriter>/<deger>")
@limiter.limit("5 per minute")
def kisi_sorgula(kriter, deger):
    veriler = load_data()
    sonuc = [k for k in veriler if k.get(kriter, "").lower() == deger.lower()]
    logging.info(f"{request.remote_addr} - {kriter}:{deger} - {len(sonuc)} sonuç")
    if not sonuc:
        return jsonify({"basari": False, "mesaj": "Kayıt bulunamadı"}), 404
    return jsonify({"basari": True, "veriler": sonuc})

@app.errorhandler(404)
def not_found(e):
    return jsonify({"hata": "Geçersiz endpoint veya parametre"}), 404

if __name__ == "__main__":
    app.run(port=config["port"], ssl_context="adhoc")
