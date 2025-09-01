from flask import Flask, jsonify, render_template
import subprocess
import datetime
import os
from methode import take_photo, print_document,create_hotspot
app = Flask(__name__)

PHOTO_DIR = "photos"
os.makedirs(PHOTO_DIR, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/take-photo", methods=["GET"])
def api_take_photo():
    photo_path = take_photo(PHOTO_DIR)
    return jsonify({"status": "success", "photo": photo_path})


@app.route("/print", methods=["GET"])
def api_print():
    files = sorted(os.listdir(PHOTO_DIR))
    if not files:
        return jsonify({"status": "error", "message": "Aucune photo disponible."}), 400

    last_photo = os.path.join(PHOTO_DIR, files[-1])
    message = print_document(last_photo)
    return jsonify({"status": "success", "message": message})


if __name__ == "__main__":
    create_hotspot('photomaton', 'photomaton')
    app.run(host="0.0.0.0", port=8000, debug=True)