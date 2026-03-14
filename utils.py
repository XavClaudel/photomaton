import os
import json
import pygame
from config import *
import shutil
from datetime import date


def set_environnement_variable(settings:list[dict]):
    for setting in settings:
        if settings[setting]["value"]:
            os.environ[setting] = "ACTIVE"


def create_dir(path:str):
    if not os.path.exists(path):
        os.makedirs(path)

def save_params(params:dict):

    data = {k: v["value"] for k, v in params.items()}

    with open("settings.json", "w") as f:
        json.dump(data, f, indent=4)

def load_params(params:dict):

    try:
        with open("settings.json") as f:
            data = json.load(f)

        for key in params:
            if key in data:
                params[key]["value"] = data[key]

    except FileNotFoundError:
        pass


def get_ecran_size(screen:pygame.Surface):
    screen_width, screen_height = screen.get_size()
    return screen_width, screen_height


def copy_photos_to_local(photo_path:str):
    dest_local = os.path.join(PHOTO_DIR, f"photomaton_{date.today()}")

    os.makedirs(dest_local, exist_ok=True)

    if os.path.isfile(photo_path):
        shutil.copy(photo_path, dest_local)
    print("photos copiées en local")