import os
import json
import pygame


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