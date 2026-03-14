from flask import Flask, send_from_directory, render_template
import os
from config import *


app = Flask(__name__)


@app.route("/")
def index():
    dossier = os.listdir(PHOTO_DIR)
    photos = [
        f for f in os.listdir(f"{PHOTO_DIR}/{dossier[0]}")
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    print(f"photos:{photos}")
    photos.sort(reverse=True)

    return render_template("index.html", photos=photos)


@app.route("/photos/<filename>")
def get_photo(filename):

    return send_from_directory(PHOTO_DIR, filename)


def start_server():
    app.run(host="192.168.4.1", port=5000)