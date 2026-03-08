from flask import Flask, send_from_directory, render_template
import os

PHOTO_DIR = "photos"

app = Flask(__name__)


@app.route("/")
def index():
    photos = os.listdir(PHOTO_DIR)
    photos.sort(reverse=True)
    return render_template("index.html", photos=photos)


@app.route("/photo/<filename>")
def get_photo(filename):
    return send_from_directory(PHOTO_DIR, filename)


def start_server():
    app.run(host="0.0.0.0", port=5000)